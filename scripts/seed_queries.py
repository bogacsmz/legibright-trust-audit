#!/usr/bin/env python3
"""Seed DataHub query history so the agent can auto-infer split methodology.

Records, on main.matches, the SQL a data scientist used to build train/test sets.
The RANDOM split here is the planted mistake the auto-fed Auditor should catch.
Swap to the temporal SQL to show the clean case.
"""
from __future__ import annotations

import sys

from trust_layer.config import CONFIG

MATCHES = "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.matches,PROD)"

LEAKY = {
    "build_train_set": "SELECT * FROM matches WHERE rand() < 0.7  -- 70% train (RANDOM split)",
    "build_test_set": "SELECT * FROM matches WHERE rand() >= 0.7  -- 30% test",
}
CLEAN = {
    "build_train_set": "SELECT * FROM matches WHERE date < '2025-07-01'  -- train (temporal)",
    "build_test_set": "SELECT * FROM matches WHERE date >= '2025-07-01'  -- test",
}


def main(mode: str = "leaky") -> int:
    CONFIG.require_gms()
    from trust_layer.datahub_client import DataHubClient

    client = DataHubClient()
    queries = LEAKY if mode == "leaky" else CLEAN
    for name, sql in queries.items():
        client.seed_query(MATCHES, name, sql)
        print(f"  seeded [{mode}] {name}: {sql[:60]}")
    print(f"\nDone. Now run: python scripts/audit_auto.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "leaky"))
