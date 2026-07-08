#!/usr/bin/env python3
"""One-command verification of the self-audit regression suite.

Runs the adversarial regression checks that the 3-round audit produced (see docs/VERIFICATION.md).
The statistical-core checks need NO DataHub. If GMS is up, it also verifies idempotent write-back.
Exit 0 iff every assertion holds. This is the runnable proof the fixes stay fixed.

    python scripts/verify_all.py
"""
from __future__ import annotations

import random
import sys
import time

from trust_layer.agent import AuditReport
from trust_layer.checks.base import Severity, Verdict
from trust_layer.checks.honest_metrics.calibration_bias import CalibrationBiasCheck
from trust_layer.checks.honest_metrics.group_leakage import GroupLeakageCheck
from trust_layer.checks.honest_metrics.overfit_flags import OverfitFlagsCheck
from trust_layer.checks.honest_metrics.target_leakage import TargetLeakageCheck
from trust_layer.checks.null_spike import NullSpikeCheck
from trust_layer.split_inference import SplitKind, classify_sql, finding_from_queries

_passed = 0
_failed = 0


def check(name: str, cond: bool) -> None:
    global _passed, _failed
    print(f"  {'✅' if cond else '❌'} {name}")
    if cond:
        _passed += 1
    else:
        _failed += 1


def core_regressions() -> None:
    print("[R2] leakage the auditor must catch")
    y = [i % 2 for i in range(120)]
    check("target leakage (feature=label) → FAIL",
          TargetLeakageCheck().run({"leak": [float(v) for v in y]}, y).failed)
    check("group leakage (entity overlap) → FAIL",
          GroupLeakageCheck().run([1, 2, 3, 4, 5], [3, 4, 5, 6, 7]).failed)
    check("clean features → OK",
          TargetLeakageCheck().run({"a": [random.random() for _ in range(120)]}, y).severity is Severity.OK)

    print("[R2] overfit collapse vs generalizing model")
    check("0.93→0.40 collapse → FAIL",
          OverfitFlagsCheck().run(in_sample=0.93, holdout=0.40, metric="acc").failed)
    check("0.79→0.57 generalizes → OK",
          OverfitFlagsCheck().run(in_sample=0.79, holdout=0.57, metric="R2").severity is Severity.OK)

    print("[R2] split-inference dodges")
    for sql in ["SELECT * FROM t WHERE created > '2000-01-01' AND (id % 10) < 7",
                "SELECT * FROM t WHERE substr(md5(id),1,1) IN ('0','1')",
                "SELECT * FROM t WHERE NTILE(10) OVER (ORDER BY id) <= 7"]:
        check(f"random dodge → RANDOM: {sql[:38]}...", classify_sql(sql).kind is SplitKind.RANDOM)
    check("overlapping temporal ranges → FAIL",
          finding_from_queries(["SELECT * FROM t WHERE date < '2024-06-01'",
                                "SELECT * FROM t WHERE date >= '2024-01-01'"]).failed)

    print("[R2] calibration false-red rate on honest models (should be low)")
    try:
        import numpy as np
        from sklearn.linear_model import LogisticRegression

        C = CalibrationBiasCheck()
        fails = 0
        for s in range(30):
            rng = np.random.default_rng(s)
            X = rng.normal(size=(900, 4)); beta = rng.normal(size=4)
            p = 1 / (1 + np.exp(-X @ beta)); yy = (rng.random(900) < p).astype(int)
            m = LogisticRegression().fit(X[:720], yy[:720])
            pt = m.predict_proba(X[720:])[:, 1]
            if C.run(list(pt), list(yy[720:])).failed:
                fails += 1
        check(f"honest-model false-RED {fails}/30 ≤ 4 (was ~12/30 before HL fix)", fails <= 4)
    except ImportError:
        print("     (sklearn not installed — skipping; pip install -e '.[dev]')")

    print("[R3] degenerate input must not produce a confident wrong verdict")
    check("empty findings → INCONCLUSIVE (not green)",
          AuditReport(target="x", findings=[]).compute_verdict() is Verdict.INCONCLUSIVE)
    check("empty query history → WARN", finding_from_queries([]).severity is Severity.WARN)
    check("calibration mismatched inputs → WARN",
          CalibrationBiasCheck().run([0.1, 0.2, 0.3], [0, 1]).severity is Severity.WARN)
    check("null-spike on 0 rows → WARN (not fabricated FAIL)",
          NullSpikeCheck().run(baseline_null_rate=0.02, current_null_rate=1.0, current_n=0).severity is Severity.WARN)

    print("[R3] classify_sql does not hang on pathological SQL")
    sql = "SELECT * FROM a " + " ".join(f"JOIN t{i} ON a.id=t{i}.id" for i in range(40))
    t = time.time(); classify_sql(sql); dt = time.time() - t
    check(f"40-JOIN chain returns in {dt:.2f}s (< 2s)", dt < 2.0)


def writeback_idempotency() -> bool:
    """If GMS is up, verify re-running an audit does not duplicate assertion/incident entities."""
    from trust_layer.config import CONFIG

    try:
        CONFIG.require_gms()
    except Exception:
        print("[R3] write-back idempotency: SKIPPED (DataHub GMS not reachable)")
        return True
    import hashlib

    from datahub.metadata.urns import AssertionUrn, IncidentUrn

    from trust_layer.agent import TrustLayerAgent
    from trust_layer.checks.base import Finding
    from trust_layer.datahub_client import DataHubClient

    c = DataHubClient()
    urn = "urn:li:dataset:(urn:li:dataPlatform:sqlite,verify_idem,PROD)"
    ag = TrustLayerAgent(client=c, write_back=True)
    f = Finding("temporal_leakage", Severity.FAIL, "x",
                suggested_tags=["audit-failed"], suggested_incident=True)
    for _ in range(3):
        r = AuditReport(target=urn, findings=[f]); r.compute_verdict(); ag._write_back(urn, r)
    time.sleep(2)

    def det(k):
        return hashlib.sha1(f"{k}|{urn}|temporal_leakage".encode()).hexdigest()

    au, iu = str(AssertionUrn(det("assertion"))), str(IncidentUrn(det("incident")))
    ok = c._graph.exists(au) and c._graph.exists(iu)
    print("[R3] write-back idempotency (3 runs → 1 assertion + 1 incident entity)")
    check("deterministic entities exist, no duplicates", ok)
    return ok


def main() -> int:
    print("=== Statistical Trust Layer — self-audit regression suite ===\n")
    core_regressions()
    writeback_idempotency()
    print(f"\n=== {_passed} passed, {_failed} failed ===")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
