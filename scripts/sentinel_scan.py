#!/usr/bin/env python3
"""SENTINEL scan — the data-health suite EXTENDING DataHub on real data.

Demonstrates the 'read DataHub, add the layer it lacks' contract:
  * schema-drift : reads the CURRENT schema from DataHub, diffs vs a baseline contract.
  * distribution-drift : reads real match odds (early season = baseline vs late = current),
                         computes PSI/KS — the temporal drift DataHub's profile doesn't.
Writes any findings back to the graph.

Prereqs: quickstart up, tr_odds ingested, pip install -e .
"""
from __future__ import annotations

import sqlite3
import sys

from trust_layer.agent import AuditReport, TrustLayerAgent
from trust_layer.checks.distribution_drift import DistributionDriftCheck
from trust_layer.checks.schema_drift import SchemaDriftCheck
from trust_layer.config import CONFIG
from trust_layer.report import render_card

MATCHES = "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.matches,PROD)"
UI = "http://localhost:9002"

# what downstream code was built against (a stored contract; a column got renamed since)
BASELINE_SCHEMA = {
    "date": "TEXT", "league": "TEXT", "home": "TEXT", "away": "TEXT",
    "result": "TEXT", "psc_h": "FLOAT", "psc_d": "FLOAT", "psc_a": "FLOAT",
    "closing_home_odds": "FLOAT",   # <- downstream expects this; current schema lacks it
}


def main() -> int:
    CONFIG.require_gms()
    from trust_layer.datahub_client import DataHubClient

    client = DataHubClient()

    # 1) schema-drift: read CURRENT schema straight from DataHub, diff vs baseline contract
    fields = client.get_schema_fields(MATCHES)
    current_schema = {f["fieldPath"]: f["type"] for f in fields}
    print(f"[sentinel] read {len(current_schema)} live fields from DataHub schema")
    schema_finding = SchemaDriftCheck().run(BASELINE_SCHEMA, current_schema, dataset="main.matches")

    # 2) distribution-drift on real odds: early rows (baseline) vs late rows (current)
    base_odds, curr_odds = _odds_by_period(CONFIG.tr_odds_db)
    print(f"[sentinel] odds drift: baseline n={len(base_odds)} vs current n={len(curr_odds)}")
    drift_finding = DistributionDriftCheck().run(base_odds, curr_odds, column="psc_h")

    report = AuditReport(target=MATCHES, findings=[schema_finding, drift_finding])
    report.compute_verdict()
    print(render_card(report))

    agent = TrustLayerAgent(client=client, write_back=True)
    agent._write_back(MATCHES, report)
    print(f"\n[sentinel] findings written back → {UI}/dataset/{MATCHES}")
    return 0


def _odds_by_period(db_path: str):
    """Home-win closing odds: first 40% of rows (baseline) vs last 40% (current)."""
    conn = sqlite3.connect(db_path)
    rows = [r[0] for r in conn.execute(
        "SELECT psc_h FROM matches WHERE psc_h > 1 ORDER BY date")]
    conn.close()
    k = int(len(rows) * 0.4)
    return rows[:k], rows[-k:]


if __name__ == "__main__":
    sys.exit(main())
