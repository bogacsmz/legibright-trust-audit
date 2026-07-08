# Sample outputs

This folder contains **real** Legibright audit outputs — not mocked or hand-written — so a judge
can see output quality without running anything. Each was produced by
[`scripts/gen_examples.py`](../scripts/gen_examples.py), which calls the same audit engine used by
[`scripts/demo_writeback.py`](../scripts/demo_writeback.py) and
[`scripts/generality_check.py`](../scripts/generality_check.py) on the three public demo datasets.
Regenerate them yourself: `python scripts/fetch_data.py && python scripts/gen_examples.py`.

| File | What it is |
|---|---|
| `matches_verdict.json` / `matches_report.md` | A `backtest_roi = +40%` claim on 11,849 real football matches — caught: temporal leakage + overfit. 🔴 NOT_TRUSTWORTHY, Trust Score 28/100. |
| `titanic_verdict.json` / `titanic_report.md` | An overfit tree on a random split (Kaggle Titanic) — caught: leakage + overfit; calibration flagged as not-certifiable. 🔴 NOT_TRUSTWORTHY, Trust Score 25/100. |
| `bikeshare_verdict.json` / `bikeshare_report.md` | An honest walk-forward forecast (UCI Bike Sharing, R² 0.79→0.57) — passes cleanly. 🟢 TRUSTWORTHY, Trust Score 100/100. Proof the tool doesn't cry wolf. |
| `mcp_audit_dataset_example.md` | A sample MCP tool call — the exact input an agent sends and the verdict card it gets back from `audit_dataset(...)`. |

## Reading a `_verdict.json`

Machine-readable, meant for another agent or a CI gate to consume:

```json
{
  "verdict": "NOT_TRUSTWORTHY",
  "trust_score": 28,
  "findings": [ { "check": "temporal_leakage", "severity": "FAIL", "detail": "..." } ],
  "writeback": { "assertions": 3, "incidents_active": 1, "tags": [...], "deprecation_proposal": true }
}
```

The `_report.md` next to it is the same data rendered for a human: verdict + Trust Score, one row
per check (✅ PASS / ⚠️ WARN / ❌ FAIL) with the evidence line, and a summary of exactly what landed
on the DataHub graph (assertions, incident, tags, Trust Score property, deprecation proposal).
