#!/usr/bin/env python3
"""AUTO-FED audit — the agent reads the split from DataHub query history itself.

No hand-supplied timestamps: point it at a dataset URN, it fetches the split SQL via
query history, judges the methodology, adds metric-level checks, writes the verdict back.

  python scripts/seed_queries.py leaky      # plant a random-split query
  python scripts/audit_auto.py              # agent catches it, no hardcoded split
"""
from __future__ import annotations

import sys

from trust_layer.agent import TrustLayerAgent
from trust_layer.checks.honest_metrics.overfit_flags import OverfitFlagsCheck
from trust_layer.config import CONFIG
from trust_layer.report import render_card

MATCHES = "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.matches,PROD)"
UI = "http://localhost:9002"


def main(urn: str = MATCHES) -> int:
    CONFIG.require_gms()
    from trust_layer.datahub_client import DataHubClient

    client = DataHubClient()
    qs = client.get_dataset_queries(urn)
    print(f"[auto] read {len(qs)} split queries from DataHub query history:")
    for q in qs:
        print(f"       {q[:70]}")

    agent = TrustLayerAgent(client=client, write_back=True)
    # extra metric-level finding the agent still supplies (reported ROI on the claim)
    extra = [OverfitFlagsCheck().run(in_sample=0.40, holdout=-0.12, n_cells_scanned=677,
                                     abs_alarm=0.20, metric="ROI")]
    report = agent.audit_dataset_from_datahub(urn, extra=extra)
    print("\n" + render_card(report))
    print(f"\n[auto] verdict written back → {UI}/dataset/{urn}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else MATCHES))
