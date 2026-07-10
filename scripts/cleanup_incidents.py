#!/usr/bin/env python3
"""One-off cleanup: hard-delete stale/duplicate incidents left by pre-idempotency-fix demo runs,
and strip stale non-audit tags (e.g. an old `schema-drift`). After this, re-run `run_demo.sh` to
recreate ONE deterministic incident per (dataset, check) — a clean, idempotent set.

    python scripts/cleanup_incidents.py
"""
from __future__ import annotations

import sys

from trust_layer.config import CONFIG

DATASETS = [
    "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.revenue,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.titanic,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.bikeshare,PROD)",
    "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.matches,PROD)",
]
# tags NOT owned by the auditor write-back that we still want gone from the demo assets
STALE_TAGS = {"schema-drift"}


def main() -> int:
    CONFIG.require_gms()
    from datahub.emitter.mcp import MetadataChangeProposalWrapper as MCP
    from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig, RelationshipDirection
    from datahub.metadata import schema_classes as S

    g = DataHubGraph(DataHubGraphConfig(server=CONFIG.gms_url, token=CONFIG.gms_token))

    def _is_ours(urn: str) -> bool:
        # only delete incidents Legibright authored — never a human- or other-tool-filed incident
        info = g.get_aspect(urn, S.IncidentInfoClass)
        return bool(info and (getattr(info, "customType", "") == "honest-metrics-audit"
                              or (info.title or "").startswith("[trust-layer]")))

    total = 0
    for ds in DATASETS:
        incs = list(g.get_related_entities(ds, ["IncidentOn"], RelationshipDirection.INCOMING))
        ours = [r for r in incs if _is_ours(r.urn)]
        for r in ours:
            g.hard_delete_entity(r.urn)
        total += len(ours)
        # strip stale tags
        tags = g.get_aspect(ds, S.GlobalTagsClass)
        stripped = 0
        if tags:
            keep = [t for t in tags.tags if t.tag.split(":")[-1] not in STALE_TAGS]
            stripped = len(tags.tags) - len(keep)
            if stripped:
                g.emit_mcp(MCP(entityUrn=ds, aspect=S.GlobalTagsClass(tags=keep)))
        print(f"  {ds.split(',')[1]:15s} deleted {len(ours)}/{len(incs)} incidents (trust-layer only)"
              + (f", stripped {stripped} stale tag(s)" if stripped else ""))
    print(f"\n✓ removed {total} incident entities. Now run: bash demo/run_demo.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
