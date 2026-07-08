# Statistical Trust Layer — a DataHub agent that catches the backtest that's lying to you

> **Build with DataHub: The Agent Hackathon** submission · Challenge: *Agents That Do Real Work*
> Deadline 10 Aug 2026. License: Apache-2.0.

An agent that reads DataHub through the **MCP Server**, runs statistical audits generic
tools skip, and **writes verdicts back into the graph** (tags, structured properties,
incidents) so the next person or agent inherits the knowledge.

Two layers:

- **Sentinel (data health)** — catches *silent* failures DataHub's built-in freshness
  can't: a feed that keeps its write-heartbeat but whose **values froze** (statistical
  freshness / distribution drift / null spikes / schema drift), then walks lineage to tag
  contaminated downstreams and opens an incident.
- **Auditor (honest metrics) — our moat.** Given a metric/backtest claim ("+40% ROI"),
  it decides whether the number is *trustworthy*: temporal-leakage / random-split detection,
  overfit red flags (ROI>20%, in-sample≫holdout), multiple-testing luck, calibration bias.
  Verdict: 🟢 TRUSTWORTHY / 🟡 INCONCLUSIVE / 🔴 NOT TRUSTWORTHY — stamped onto the asset.

## Why this wins (not just another AI agent)
Everyone can wire an LLM to MCP. The differentiator is **domain honesty**: this protocol
is distilled from two production betting-model pipelines (**250k+ rows of real odds+results**)
where it honestly **killed 10+ "profitable-looking" strategies**. DataHub ships freshness
and assertions; it does **not** ship statistical honesty. That's the layer we add on top.

The demo runs on that **real data**, live — the Auditor catches a fake edge on camera.

## Architecture
```
        ┌────────────── DataHub (local OSS quickstart) ──────────────┐
        │  datasets · schema · lineage · query history · assertions  │
        └───────▲───────────────────────────────────────▲───────────┘
                │ READ (MCP: search/get_lineage/                │ WRITE-BACK
                │       list_schema_fields/get_dataset_queries) │ (add_tags,
                │                                               │  structured props,
        ┌───────┴───────────────────────────────────────┐      │  incidents, assertions)
        │              TrustLayerAgent                    │──────┘
        │  Sentinel checks  +  Auditor checks (pure stats)│
        │  → Finding → Verdict card → graph write-back     │
        └──────────────────────────────────────────────────┘
```
- `src/trust_layer/checks/` — pure, unit-tested statistical checks (no DataHub dep).
- `src/trust_layer/datahub_client.py` — SDK read + write-back; MCP tool names documented.
- `src/trust_layer/agent.py` — orchestration + lineage propagation.
- `ingest/` — DataHub recipes to load our real SQLite odds tables.
- `demo/scenario.md` — the ≤3-min video script.

## Quickstart
```bash
pip install -e .
bash scripts/quickstart_up.sh          # local DataHub at :9002 / :8080
python ingest/sqlite_to_datahub.py      # load a real odds table
python scripts/milestone1.py            # end-to-end: read one dataset's health
trust-layer selftest                    # statistical core, no DataHub needed
```
MCP wiring for judges: `scripts/mcp_config.json`.

## Status
Milestone 0 (scaffold + statistical core + tests) ✅ — `trust-layer selftest` prints a
real verdict card; `pytest` green. See `docs/PLAN.md` for the 34-day plan.
