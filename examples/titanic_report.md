# Audit report — `main.titanic`

**Verdict:** 🔴 **NOT_TRUSTWORTHY** · **Trust Score 25/100**  _(bands: TRUSTWORTHY 71–100 · INCONCLUSIVE 45–70 · NOT_TRUSTWORTHY 0–40)_
**Claim audited:** `survival classifier accuracy` on 891 rows · source: Kaggle / datasciencedojo Titanic (public)

| Check | Result | Evidence |
|---|---|---|
| `temporal_leakage` | ❌ FAIL | 622/623 (99.8%) training rows are dated at/after the earliest test row. Split is not a clean time cut (train_max=890 ≥ test_min=1); looks like a RANDOM split masquerading as walk-forward. |
| `overfit_flags` | ❌ FAIL | holdout collapse: accuracy 0.987→0.735 (gap +0.252 > 0.25) |
| `calibration_bias` | ⚠️ WARN | HL χ²=0.2, p=1, ECE=0.254 over 10 bins |

**Written back to DataHub:** 3 assertions · 1 active incident(s) · tags ['audit-failed', 'audit-warn', 'temporal-leakage'] · Trust Score property `25` · deprecation proposal: yes (deprecated=false, human approves)
