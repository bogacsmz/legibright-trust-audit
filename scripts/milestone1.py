#!/usr/bin/env python3
"""MILESTONE 1 — end-to-end 'hello world':
read ONE dataset's schema from DataHub + its recent values from source, run the
statistical freshness check, print a verdict card.

Proves the full path: DataHub read (SDK) → statistical check → verdict.
Write-back + lineage propagation land in milestone 2.

Prereqs: quickstart up, `datahub ingest -c ingest/recipes/iddaa.yml` done, `pip install -e .`
"""
from __future__ import annotations

import sqlite3
import statistics
import sys

from trust_layer.agent import AuditReport
from trust_layer.checks.freshness import FreshnessCheck
from trust_layer.config import CONFIG
from trust_layer.report import render_card


def main(urn: str | None = None) -> int:
    CONFIG.require_gms()
    from trust_layer.datahub_client import DataHubClient

    client = DataHubClient()
    # Public reproducible dataset (built by fetch_data.py, ingested via recipes/matches.yml):
    urn = urn or client.dataset_urn("sqlite", "main.matches")

    fields = client.get_schema_fields(urn)
    if not fields:
        print(f"[milestone1] No schema for {urn}. First run:\n"
              f"  python scripts/fetch_data.py && datahub ingest -c ingest/recipes/matches.yml")
        return 1
    print(f"[milestone1] DataHub → read {len(fields)} fields from {urn}:")
    print("            " + ", ".join(f["fieldPath"] for f in fields))

    # Pull recent home-win closing odds from the source table + a historical stdev baseline,
    # and run the real freshness check.
    recent, hist_stdev, col = _sample_odds(CONFIG.odds_db, column="psc_h")
    if not recent:
        print(f"[milestone1] source table not found in {CONFIG.odds_db} — run fetch_data.py")
        return 1
    print(f"[milestone1] source → {len(recent)} recent '{col}' values; hist σ={hist_stdev:.3f}")

    finding = FreshnessCheck().run(recent_values=recent, historical_stdev=hist_stdev, column=col)
    report = AuditReport(target=urn, findings=[finding])
    report.compute_verdict()
    print(render_card(report))
    return 0


def _sample_odds(db_path: str, column: str, recent_n: int = 40):
    """Most-recent `column` values + a robust historical stdev, from the matches table."""
    try:
        conn = sqlite3.connect(db_path)
        rows = [r[0] for r in conn.execute(
            f"SELECT {column} FROM matches WHERE {column} IS NOT NULL ORDER BY date DESC LIMIT ?",
            (recent_n,))]
        allvals = [r[0] for r in conn.execute(
            f"SELECT {column} FROM matches WHERE {column} IS NOT NULL")]
        conn.close()
    except sqlite3.OperationalError:
        return [], 1.0, column   # table missing → caller handles gracefully
    hist = statistics.pstdev(allvals) if len(allvals) > 2 else 1.0
    return rows, hist, column


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
