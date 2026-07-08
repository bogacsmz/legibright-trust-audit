#!/usr/bin/env python3
"""Give the Legibright trust-audit agent an avatar in DataHub, so the ✓-L mark shows next to
the assertions/incidents it files. Uses the favicon SVG as a self-contained data URI.

    python scripts/set_agent_avatar.py
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

from trust_layer.config import CONFIG

ACTOR = "urn:li:corpuser:trust-layer-agent"
FAVICON = Path(__file__).resolve().parent.parent / "docs" / "assets" / "legibright-favicon.svg"


def main() -> int:
    CONFIG.require_gms()
    from datahub.emitter.mcp import MetadataChangeProposalWrapper as MCP
    from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
    from datahub.metadata import schema_classes as S

    svg = FAVICON.read_bytes()
    data_uri = "data:image/svg+xml;base64," + base64.b64encode(svg).decode()
    g = DataHubGraph(DataHubGraphConfig(server=CONFIG.gms_url, token=CONFIG.gms_token))
    # `displayName` + `title` both render in the profile header's fixed-height purple band, on a
    # narrow sidebar — even "Legibright Trust Auditor" (24 chars) truncates with "...". Keep the
    # NAME to the brand word alone and put the role in `title` as a separate short line; an EMPTY
    # title renders as a literal "None" placeholder (worse than short text), so title stays short
    # and non-empty. The longer description belongs ONLY in aboutMe (the editable bio field, shown
    # lower on the page where it has room to wrap).
    g.emit_mcp(MCP(entityUrn=ACTOR, aspect=S.CorpUserInfoClass(
        active=True, displayName="Legibright", system=True, title="Trust Auditor")))
    g.emit_mcp(MCP(entityUrn=ACTOR, aspect=S.CorpUserEditableInfoClass(
        displayName="Legibright",
        title="Trust Auditor",
        aboutMe="Statistical Trust Layer agent — audits models for leakage, overfit and "
                "calibration; writes verdicts back as assertions, incidents, tags and a "
                "0-100 Trust Score.",
        pictureLink=data_uri)))
    back = g.get_aspect(ACTOR, S.CorpUserEditableInfoClass)
    ok = bool(back and back.pictureLink)
    print(f"{'✅' if ok else '❌'} agent avatar set for {ACTOR} "
          f"(pictureLink {len(back.pictureLink) if ok else 0} bytes data URI)")
    print("   Note: SVG data URIs render in most browsers; if the DataHub build strips SVG, "
          "repoint pictureLink to the raw GitHub URL of the favicon after push.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
