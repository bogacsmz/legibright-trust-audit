#!/usr/bin/env python3
"""Ingest our real SQLite tables into DataHub as datasets (schema + lineage).

Uses DataHub's built-in SQLite/SQLAlchemy ingestion so the graph gets real schemas
we then audit. We ALSO stamp lineage edges (raw snapshot → derived analytics table)
so the Sentinel can do root-cause walks in the demo.

Sources (250k+ rows of real odds/results):
  - tjk-sib/tjk_sib.db        (horse-racing SİB odds + results)
  - tr-spor-value/tr_odds.db  (football closing odds, Pinnacle reference)
  - tr-spor-value/iddaa_snap.db (live İddaa/Nesine/Pinnacle snapshots)

Build-week TODO: finalize the recipe emit + lineage MCPs against installed SDK.
This file documents the intended pipeline and is runnable once deps are installed.
"""
from __future__ import annotations

from trust_layer.config import CONFIG

RECIPE_TEMPLATE = {
    "source": {
        "type": "sqlite",  # via sqlalchemy generic; see ingest/recipes/*.yml
        "config": {"database": "<path>"},
    },
    "sink": {
        "type": "datahub-rest",
        "config": {"server": CONFIG.gms_url, "token": CONFIG.gms_token},
    },
}


def main() -> None:
    print("Datasets to ingest (paths from .env):")
    for label, path in (("tjk", CONFIG.tjk_db), ("tr_odds", CONFIG.tr_odds_db), ("iddaa", CONFIG.iddaa_db)):
        print(f"  - {label}: {path or '(unset — fill .env)'}")
    print(
        "\nRun DataHub ingestion with the recipes in ingest/recipes/ once quickstart is up:\n"
        "  datahub ingest -c ingest/recipes/iddaa.yml\n"
        "Then stamp demo lineage (raw.snaps -> analytics.edge_candidates) via the SDK."
    )


if __name__ == "__main__":
    main()
