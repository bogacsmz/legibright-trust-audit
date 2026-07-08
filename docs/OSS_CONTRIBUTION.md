# Open-Source Contribution Plan (bonus criterion)

The Auditor is built as a **liftable module** so it can become an upstream contribution,
not just a demo. Everything statistical lives behind `checks/honest_metrics/registry.py`
with declared inputs and zero DataHub coupling — extraction is mechanical.

## Planned contribution (pick 1–2 before submit, ~day 28)
1. **`datahub-skill-honest-metrics`** — package the registry as a DataHub *skill*: given a
   dataset/metric URN, the skill fetches split + predictions via MCP and returns a verdict
   + emits the assertion. This is the cleanest "extend DataHub" artifact.
2. **Docs / RFC** — a short guide: "Statistical honesty assertions on top of DataHub"
   (temporal-leakage / calibration as CUSTOM assertions). Low effort, high visibility.
3. **Fix / example PR** — the SQLite-profiling `max_overflow` failure we hit
   (`ingest/recipes/iddaa.yml` note) is a real rough edge; a small docs/issue or config
   example for SQLite ingestion is a legitimate upstream improvement.

## Why this is "extend", not "rebuild"
DataHub already ships: freshness assertions, volume assertions, column profiling, incidents.
We do **not** reimplement those. We:
- **read** DataHub's profiling / native assertion status (Sentinel consumes it),
- **add** the statistical layer DataHub lacks (Auditor: leakage / overfit / calibration),
- **write** results back through DataHub's own Assertion + Incident + Tag entities.
