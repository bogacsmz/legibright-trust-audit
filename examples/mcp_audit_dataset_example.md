# Sample MCP tool call — `audit_dataset`

This is a real call/response captured from `src/trust_layer/mcp_server.py`. Any MCP-
compatible agent (Claude, an IDE assistant, another DataHub skill) can invoke this tool
directly — it is not a CLI-only demo.

## Input (MCP tool call)

```json
{
  "tool": "audit_dataset",
  "arguments": {
    "dataset_urn": "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.matches,PROD)",
    "write_back": true
  }
}
```

## Output (tool result — a rendered verdict card, returned as the tool's string result)

```
┌─────────────────────────────────────────────────────────────
│  TRUST LAYER AUDIT — 🔴 NOT TRUSTWORTHY  (Trust Score 28/100)
│  target: urn:li:dataset:(urn:li:dataPlatform:sqlite,main.matches,PROD) :: backtest_roi
├─────────────────────────────────────────────────────────────
│  ❌ [temporal_leakage] TEMPORAL LEAKAGE — training data overlaps the test period
│      8277/8294 (99.8%) training rows are dated at/after the earliest test row. Split is not a clean time cut (train_max=1768345200 ≥ test_min=1599775200); looks like a RANDOM split masquerading as walk-forward.
│  ❌ [overfit_flags] OVERFIT RED FLAGS present
│      in-sample ROI 0.40 > 0.20 implausibility alarm; holdout ROI collapsed to -0.12; holdout collapse: ROI 0.400→-0.120 (gap +0.520 > 0.25); 677 cells scanned → ~15.6 expected false z≥2 winners
│  ✅ [calibration_bias] well calibrated — ECE 0.019 below the 0.03 material floor (HL deviation significant, p=0.00012, but immaterial at n=11849)
│      HL χ²=31.4, p=0.000117, ECE=0.019 over 10 bins
└─────────────────────────────────────────────────────────────
```

With `write_back=True` (the default), this call also lands an Assertion, an ACTIVE
Incident, tags, a Trust Score structured property, and — because the verdict is
NOT_TRUSTWORTHY — a deprecation proposal, directly in the DataHub graph. See
`matches_verdict.json` for the exact write-back summary.
