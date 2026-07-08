#!/usr/bin/env python3
"""DEMO — Legibright audits a backtest and writes the verdict back into DataHub.

Target: `main.matches` — ~12.9k real football matches (public football-data.co.uk, 6 leagues,
reproducible via `scripts/fetch_data.py`). The audit runs on the 11,849 rows with complete
Pinnacle closing odds. We judge a representative "backtest_roi = +40%" claim on it:

  * temporal leakage  — MEASURED from the real match dates under a RANDOM split (future in train)
  * overfit flags     — the RECONSTRUCTED claim's curve (+40% in-sample vs −12% holdout)
  * calibration bias  — MEASURED: real implied-prob vs real outcomes

The temporal-leakage and calibration findings are measured from real data; the overfit numbers
are the reconstructed claim being judged (we don't have the modeler's original curve). It then
emits Assertion + Incident + Tag + Trust Score (+ a deprecation proposal) into live GMS.

Prereqs: quickstart up, `python scripts/fetch_data.py`, `pip install -e .`.
"""
from __future__ import annotations

import datetime as dt
import sqlite3
import sys

from trust_layer.agent import AuditReport, TrustLayerAgent
from trust_layer.checks.base import Verdict
from trust_layer.checks.honest_metrics.calibration_bias import CalibrationBiasCheck
from trust_layer.checks.honest_metrics.overfit_flags import OverfitFlagsCheck
from trust_layer.checks.honest_metrics.temporal_leakage import TemporalLeakageCheck
from trust_layer.config import CONFIG
from trust_layer.report import render_card

DATASET = "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.matches,PROD)"
UI = "http://localhost:9002"


def main() -> int:
    CONFIG.require_gms()
    from trust_layer.datahub_client import DataHubClient

    dates, implied, outcomes = _load(CONFIG.odds_db)
    print(f"[demo] audited claim: 'backtest_roi = +40%' on {len(dates)} real matches\n")

    # A RANDOM split (industry-common mistake): shuffle rows, ignoring time → future leaks.
    import random

    order = list(range(len(dates)))
    random.Random(42).shuffle(order)          # genuinely random, seeded for reproducibility
    cut = int(len(order) * 0.7)
    train_ts = [dates[i].timestamp() for i in order[:cut]]
    test_ts = [dates[i].timestamp() for i in order[cut:]]

    findings = [
        TemporalLeakageCheck().run(train_ts=train_ts, test_ts=test_ts),
        OverfitFlagsCheck().run(in_sample=0.40, holdout=-0.12, n_cells_scanned=677, abs_alarm=0.20, metric="ROI"),
        CalibrationBiasCheck().run(predicted=implied, outcomes=outcomes),
    ]
    report = AuditReport(target=f"{DATASET} :: backtest_roi", findings=findings)
    report.compute_verdict()
    print(render_card(report))
    print(f"   ↳ {findings[0].detail}")          # surface the measured temporal leak %

    print("\n[demo] writing verdict back into DataHub graph...")
    agent = TrustLayerAgent(client=DataHubClient(), write_back=True, propose_deprecation=True)
    written = agent._write_back(DATASET, report)
    n_assert = sum("assertion" in u for u in written)
    n_incident = sum("incident" in u for u in written)
    n_tag = sum("tag" in u for u in written)
    print(f"   ✓ {n_assert} assertions → Data-Quality tab (SUCCESS/FAILURE, with history)")
    print(f"   ✓ {n_incident} incident → Incidents tab (ACTIVE, carries the failure detail)")
    print(f"   ✓ {n_tag} tags → audit-failed, temporal-leakage")
    print(f"   ✓ Trust Score {report.trust_score()}/100 → typed numeric structured property")
    if report.verdict is Verdict.NOT_TRUSTWORTHY:
        print("   ✓ deprecation PROPOSED → deprecated=false (agent proposes, a human approves)")
    print(f"\n[demo] see it in DataHub → Assertions + Incidents tabs:\n   {UI}/dataset/{DATASET}")
    return 0


def _load(db_path: str):
    """Real dates, Pinnacle-implied home-win prob (de-vig), and home-win outcomes."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT date, psc_h, psc_d, psc_a, result FROM matches "
        "WHERE psc_h>1 AND psc_d>1 AND psc_a>1 AND result IN ('H','D','A')"
    ).fetchall()
    conn.close()
    dates, implied, outcomes = [], [], []
    for d, h, dr, a, res in rows:
        try:
            date = dt.datetime.strptime(d, "%d/%m/%Y")
        except ValueError:
            continue
        ov = 1 / h + 1 / dr + 1 / a
        dates.append(date)
        implied.append((1 / h) / ov)          # de-vigged home-win probability
        outcomes.append(1 if res == "H" else 0)
    return dates, implied, outcomes


if __name__ == "__main__":
    sys.exit(main())
