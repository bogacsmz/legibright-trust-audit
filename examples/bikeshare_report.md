# Audit report — `main.bikeshare`

**Verdict:** 🟢 **TRUSTWORTHY** · **Trust Score 100/100**  _(bands: TRUSTWORTHY 71–100 · INCONCLUSIVE 45–70 · NOT_TRUSTWORTHY 0–40)_
**Claim audited:** `daily-demand forecast R²` on 731 rows · source: UCI ML Repository #275 Bike Sharing (public)

| Check | Result | Evidence |
|---|---|---|
| `temporal_leakage` | ✅ PASS | clean temporal split (train strictly precedes test) |
| `overfit_flags` | ✅ PASS | no overfit red flags (R² generalizes) |

**Written back to DataHub:** 2 assertions · 0 active incident(s) · tags — · Trust Score property `100` · deprecation proposal: no
