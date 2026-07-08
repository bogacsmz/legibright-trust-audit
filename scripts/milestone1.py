#!/usr/bin/env python3
"""MILESTONE 1 — end-to-end 'hello world':
read ONE dataset's health from DataHub and print a verdict card.

Prereqs:
  1. DataHub quickstart running (scripts/quickstart_up.sh) at http://localhost:8080
  2. A dataset ingested (ingest/sqlite_to_datahub.py) — e.g. our odds snapshots table
  3. pip install -e .   (installs acryl-datahub + deps)

What it proves: DataHub read (schema + recent values via SDK) → statistical freshness
check → verdict card. The write-back + lineage propagation land in milestone 2.
"""
from __future__ import annotations

import sys

from trust_layer.agent import AuditReport, TrustLayerAgent
from trust_layer.checks.freshness import FreshnessCheck
from trust_layer.config import CONFIG
from trust_layer.report import render_card


def main(urn: str | None = None) -> int:
    CONFIG.require_gms()
    try:
        from trust_layer.datahub_client import DataHubClient
    except RuntimeError as e:
        print(f"[setup] {e}")
        return 2

    client = DataHubClient()
    # Default demo target: the İddaa odds snapshot table once ingested.
    urn = urn or client.dataset_urn("sqlite", "iddaa_snap.snaps")

    fields = client.get_schema_fields(urn)
    if not fields:
        print(f"[milestone1] No schema for {urn}. Ingest it first (ingest/sqlite_to_datahub.py).")
        return 1
    print(f"[milestone1] read {len(fields)} fields from {urn}")

    # For the hello-world we assert freshness on a numeric column using a tiny
    # sample the SDK/query layer will provide in milestone 2; here we show the path.
    finding = FreshnessCheck().run(
        recent_values=[2.0, 2.0, 2.0, 2.0, 2.0],  # placeholder until query wiring (day 2)
        historical_stdev=0.7,
        column="o1",
    )
    report = AuditReport(target=urn, findings=[finding])
    report.compute_verdict()
    print(render_card(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
