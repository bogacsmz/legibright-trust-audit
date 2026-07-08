"""The Statistical Trust Layer agent orchestrator.

Flow (Challenge 1 — "Agents That Do Real Work"):
  1. READ  — pull a dataset's schema/lineage/recent values from DataHub (MCP or SDK).
  2. AUDIT — run Sentinel health checks + Auditor honest-metrics checks (pure stats).
  3. WRITE — push verdicts back to the graph: tags + structured verdict, and (for FAILs)
             an incident, so the next person/agent inherits the knowledge.
  4. TRACE — if a downstream metric depends on a failing source, walk lineage and mark it.

The DataHub client is injected so the orchestrator is testable without a live graph.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .checks.base import Finding, Severity, Verdict


@dataclass
class AuditReport:
    target: str
    findings: list[Finding] = field(default_factory=list)
    verdict: Verdict = Verdict.TRUSTWORTHY

    def trust_score(self) -> int:
        """0-100 statistical-honesty score, banded to the verdict:
        TRUSTWORTHY 71-100 · INCONCLUSIVE 45-70 · NOT_TRUSTWORTHY 0-40."""
        fails = sum(1 for f in self.findings if f.severity is Severity.FAIL)
        warns = sum(1 for f in self.findings if f.severity is Severity.WARN)
        if not self.findings:
            return 50                                   # no evidence → mid INCONCLUSIVE
        if fails:
            return max(0, 40 - 12 * (fails - 1) - 3 * warns)
        if warns:
            return max(45, 70 - 10 * warns)
        return 100

    def compute_verdict(self) -> Verdict:
        if not self.findings:
            # no checks ran ≠ trustworthy. Absence of evidence is INCONCLUSIVE, never green.
            self.verdict = Verdict.INCONCLUSIVE
        elif any(f.severity is Severity.FAIL for f in self.findings):
            self.verdict = Verdict.NOT_TRUSTWORTHY
        elif any(f.severity is Severity.WARN for f in self.findings):
            self.verdict = Verdict.INCONCLUSIVE
        else:
            self.verdict = Verdict.TRUSTWORTHY
        return self.verdict


class TrustLayerAgent:
    def __init__(self, client=None, *, write_back: bool = True, propose_deprecation: bool = False):
        self.client = client            # DataHubClient | None (None = dry run)
        self.write_back = write_back and client is not None
        # opt-in governance: on NOT_TRUSTWORTHY, propose (not enact) deprecation for human review
        self.propose_deprecation = propose_deprecation

    def audit(self, target_urn: str, findings: list[Finding]) -> AuditReport:
        """Assemble findings into a report and (optionally) write verdicts to the graph."""
        report = AuditReport(target=target_urn, findings=findings)
        report.compute_verdict()
        if self.write_back:
            self._write_back(target_urn, report)
        return report

    def audit_dataset_from_datahub(self, dataset_urn: str, extra: list[Finding] | None = None) -> AuditReport:
        """AUTO-FED audit: the agent reads the split methodology from DataHub query history
        (no hand-supplied timestamps), judges it, and adds any extra metric-level findings.

        This is the "agent does real work" path: point it at a dataset URN and it discovers
        how the split was built, decides trustworthiness, and writes the verdict back.
        """
        from .split_inference import finding_from_queries

        queries = self.client.get_dataset_queries(dataset_urn) if self.client else []
        # ALWAYS record the split finding — finding_from_queries([]) returns a WARN
        # ("methodology unverifiable"), so an un-instrumented dataset is INCONCLUSIVE, not green.
        findings: list[Finding] = [finding_from_queries(queries)]
        findings.extend(extra or [])
        return self.audit(dataset_urn, findings)

    def _write_back(self, urn: str, report: AuditReport) -> list[str]:
        """Materialize the verdict as graph-native artifacts (Assertion + Tag + Incident).

        Every check becomes a DataHub assertion run (SUCCESS/FAILURE) so the verdict lives
        in the native Data-Quality surface with history; FAILs also raise an incident and
        stamp tags. Returns the URNs written (handy for the demo to deep-link the UI).
        """
        written: list[str] = []
        errors: list[str] = []

        def _try(label, fn):
            try:
                r = fn()
                if isinstance(r, list):
                    written.extend(r)            # reconcile_tags returns a list of tag URNs
                elif r:
                    written.append(r)
            except Exception as e:  # best-effort per artifact; one failure doesn't abort the rest
                errors.append(f"{label}: {type(e).__name__}: {e}")

        for f in report.findings:
            # 1) assertion run (idempotent, keyed on dataset+check) — Data-Quality tab
            _try(f"assertion/{f.check}", lambda f=f: self.client.emit_assertion_result(
                urn, check_id=f.check, passed=not f.failed, detail=f.detail or f.headline))
            # 2) incident lifecycle: raise if this check fails, else resolve any prior one
            active = f.severity is Severity.FAIL and f.suggested_incident
            _try(f"incident/{f.check}", lambda f=f, active=active: self.client.set_incident(
                urn, f.check, active, f"[trust-layer] {f.check}", f.detail or f.headline))
        # 3) tags — reconciled once so the graph reflects the LATEST verdict
        current_tags = sorted({t for f in report.findings for t in f.suggested_tags})
        _try("tags", lambda: self.client.reconcile_tags(urn, current_tags))
        # 4) Trust Score — a typed numeric structured property (not a tag)
        _try("trust_score", lambda: self.client.set_trust_score(urn, report.trust_score()))
        # 4b) Legibright as an *Auditor* owner → its ✓-L avatar shows in the Owners panel
        _try("owner", lambda: self.client.set_auditor_owner(urn))
        # 5) opt-in governance: PROPOSE (not enact) deprecation on an untrustworthy verdict
        if self.propose_deprecation and report.verdict is Verdict.NOT_TRUSTWORTHY:
            reason = next((f.headline for f in report.findings if f.failed), "failed trust audit")
            _try("deprecation-proposal", lambda: self.client.propose_deprecation(urn, reason))

        if errors:  # surface partial-write inconsistency instead of hiding it
            print(f"[write-back] {len(written)} ok, {len(errors)} FAILED: " + "; ".join(errors))
        return written

    def propagate_downstream(self, source_urn: str, get_downstreams) -> list[str]:
        """When a source FAILs, tag downstreams 'contaminated' via lineage."""
        marked: list[str] = []
        for urn in get_downstreams(source_urn):
            if self.write_back:
                self.client.add_tag(urn, "contaminated-upstream")
            marked.append(urn)
        return marked
