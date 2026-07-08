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

    def compute_verdict(self) -> Verdict:
        if any(f.severity is Severity.FAIL for f in self.findings):
            self.verdict = Verdict.NOT_TRUSTWORTHY
        elif any(f.severity is Severity.WARN for f in self.findings):
            self.verdict = Verdict.INCONCLUSIVE
        else:
            self.verdict = Verdict.TRUSTWORTHY
        return self.verdict


class TrustLayerAgent:
    def __init__(self, client=None, *, write_back: bool = True):
        self.client = client            # DataHubClient | None (None = dry run)
        self.write_back = write_back and client is not None

    def audit(self, target_urn: str, findings: list[Finding]) -> AuditReport:
        """Assemble findings into a report and (optionally) write verdicts to the graph."""
        report = AuditReport(target=target_urn, findings=findings)
        report.compute_verdict()
        if self.write_back:
            self._write_back(target_urn, report)
        return report

    def _write_back(self, urn: str, report: AuditReport) -> list[str]:
        """Materialize the verdict as graph-native artifacts (Assertion + Tag + Incident).

        Every check becomes a DataHub assertion run (SUCCESS/FAILURE) so the verdict lives
        in the native Data-Quality surface with history; FAILs also raise an incident and
        stamp tags. Returns the URNs written (handy for the demo to deep-link the UI).
        """
        written: list[str] = []
        for f in report.findings:
            # 1) assertion run — the verdict in DataHub's own Data-Quality tab
            written.append(
                self.client.emit_assertion_result(
                    urn, check_id=f.check, passed=not f.failed, detail=f.detail or f.headline
                )
            )
            # 2) incidents — hard failures the next person/agent inherits
            if f.severity is Severity.FAIL and f.suggested_incident:
                written.append(
                    self.client.raise_incident(urn, f"[trust-layer] {f.check}", f.detail or f.headline)
                )
        # 3) tags — reconciled once so the graph reflects the LATEST verdict
        #    (a now-clean asset drops a stale audit-failed tag)
        current_tags = sorted({t for f in report.findings for t in f.suggested_tags})
        written += self.client.reconcile_tags(urn, current_tags)
        return written

    def propagate_downstream(self, source_urn: str, get_downstreams) -> list[str]:
        """When a source FAILs, tag downstreams 'contaminated' via lineage."""
        marked: list[str] = []
        for urn in get_downstreams(source_urn):
            if self.write_back:
                self.client.add_tag(urn, "contaminated-upstream")
            marked.append(urn)
        return marked
