"""Expose the Auditor as an MCP server, so ANY agent (Claude, Cursor, another pipeline)
can call `audit_dataset` on a DataHub asset and get a trust verdict — with the verdict
written back into the graph.

Run:
    pip install -e .
    DATAHUB_GMS_URL=http://localhost:8080 python -m trust_layer.mcp_server
Then point an MCP client at it (stdio). Tools exposed:
    * audit_dataset(dataset_urn)     — auto-fed audit (reads split from query history), writes back
    * classify_split_sql(sql)        — quick check: is this split TEMPORAL or RANDOM?
    * list_auditor_skills()          — the honest-metrics checks this server can run
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .checks.honest_metrics.registry import list_skills
from .report import render_card
from .split_inference import classify_sql

mcp = FastMCP("statistical-trust-layer")


@mcp.tool()
def audit_dataset(dataset_urn: str, write_back: bool = True) -> str:
    """Audit a DataHub dataset for trustworthiness. Reads how its train/test split was built
    from query history, judges leakage/methodology, and (by default) writes the verdict back
    to the graph as an assertion + incident + tags. Returns the verdict card."""
    from .agent import TrustLayerAgent
    from .datahub_client import DataHubClient

    agent = TrustLayerAgent(client=DataHubClient(), write_back=write_back)
    report = agent.audit_dataset_from_datahub(dataset_urn)
    return render_card(report)


@mcp.tool()
def classify_split_sql(sql: str) -> str:
    """Classify a single train/test split SQL statement as TEMPORAL (clean), RANDOM (leakage
    risk), or UNKNOWN — without touching DataHub. Useful as a quick lint."""
    info = classify_sql(sql)
    return f"{info.kind.value}: {info.detail}"


@mcp.tool()
def list_auditor_skills() -> str:
    """List the honest-metrics checks (temporal leakage, overfit, calibration) this auditor runs."""
    return "\n".join(f"- {s.id}: {s.title} — catches {s.catches}" for s in list_skills())


if __name__ == "__main__":
    mcp.run()
