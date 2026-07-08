# Audit report — `main.matches`

**Verdict:** 🔴 **NOT_TRUSTWORTHY** · **Trust Score 28/100**  _(bands: TRUSTWORTHY 71–100 · INCONCLUSIVE 45–70 · NOT_TRUSTWORTHY 0–40)_
**Claim audited:** `backtest_roi = +40%` on 11,849 rows · source: football-data.co.uk (public football closing odds)

| Check | Result | Evidence |
|---|---|---|
| `temporal_leakage` | ❌ FAIL | 8277/8294 (99.8%) training rows are dated at/after the earliest test row. Split is not a clean time cut (train_max=1768345200 ≥ test_min=1599775200); looks like a RANDOM split masquerading as walk-forward. |
| `overfit_flags` | ❌ FAIL | in-sample ROI 0.40 > 0.20 implausibility alarm; holdout ROI collapsed to -0.12; holdout collapse: ROI 0.400→-0.120 (gap +0.520 > 0.25); 677 cells scanned → ~15.6 expected false z≥2 winners |
| `calibration_bias` | ✅ PASS | HL χ²=31.4, p=0.000117, ECE=0.019 over 10 bins |

**Written back to DataHub:** 3 assertions · 1 active incident(s) · tags ['audit-failed', 'temporal-leakage'] · Trust Score property `28` · deprecation proposal: yes (deprecated=false, human approves)
