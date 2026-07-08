# Verification & Honest Limitations

This project audits other people's models for honesty, so it must survive the same scrutiny.
On 8 Jul 2026 we ran a 3-round adversarial self-audit: each round a **separate, clean-context
subagent** with a different adversary role, read-only on the repo (grader), while the author
fixed findings (builder). **Guardrail: no test or check was ever loosened to go green** — every
finding was either honestly fixed or is recorded below as a known limitation.

Run `python scripts/verify_all.py` to reproduce the regression checks (no DataHub needed for the
statistical core; write-back/idempotency checks run if GMS is up).

## What was tested
- **Round 1 (skeptical judge):** clean-room reproduce from README in a fresh venv; install path;
  every concrete claim vs reality; reproducibility of the "real data" demos.
- **Round 2 (ML expert):** adversarial data to force wrong verdicts — hidden target/group/temporal
  leakage; overfit-threshold blind spots; calibration false pos/neg; false-positive/negative rates
  over 100+ real sklearn models; determinism; overfit-to-3-datasets.
- **Round 3 (chaos/reliability):** degenerate inputs (empty query history, all-null, single row,
  broken/huge SQL); idempotency (re-run → duplicate incidents?); DataHub down; 250k-row time/memory;
  partial-write consistency; incident lifecycle.

## Found & fixed (evidence in git history: commits c594766, 443fb46, 73ed511)
| # | Finding | Fix |
|---|---|---|
| R1 | Clean clone couldn't reproduce: no data, `[sqlalchemy]` extra missing, milestone1 tracebacks | `scripts/fetch_data.py` downloads PUBLIC data (football-data.co.uk + Titanic + Bike); `acryl-datahub[sqlalchemy]` in deps; scripts default to repo-local public DBs |
| R1 | Over-claims ("250k+ rows", "killed 10+ strategies") | Scoped honestly: ~12.9k reproducible public matches; 250k is private-aggregate context, not a claim |
| R2 | **False green:** target & group leakage invisible (auditor never saw features) | Added `target_leakage` (single-feature separation / rank-AUC) + `group_leakage` (entity overlap) checks |
| R2 | **False red:** calibration flagged 41% of honest models at n=180 (fixed ECE threshold, n-biased) | Replaced with Hosmer-Lemeshow significance test (sample-size aware); false-red ~41% → ~5% (nominal) |
| R2 | Overfit cliff: 0.93→0.40 collapse was only WARN (needed in-sample ≥0.95 to FAIL) | FAIL on holdout collapse (gap > 0.25) at any in-sample level |
| R2 | Split classifier dodged by md5/ntile/modulo/hash; a cosmetic date predicate masked a random split; overlapping temporal ranges passed | Random-first classification + those patterns; `finding_from_queries` detects train/test cutoff overlap |
| R2 | demo split was a no-op (`microsecond` always 0), not the advertised random split | Real seeded shuffle |
| R3 | **Silent green:** empty query history / empty findings → TRUSTWORTHY | `compute_verdict([])` → INCONCLUSIVE; audit always records the split finding (empty → WARN) |
| R3 | **Idempotency:** re-runs spawned unbounded duplicate assertions + ACTIVE incidents | Deterministic URNs per (dataset, check) → re-runs update; incident lifecycle resolves on FAIL→OK |
| R3 | Silent-wrong on degenerate input: calibration mismatch → OK; null-spike on 0 rows → fabricated z=1000 FAIL | Both → WARN ("not assessed") |
| R3 | `classify_sql` hung super-linearly on JOIN chains (untrusted query-history input) | Guard: skip parse on oversized/≥8-JOIN SQL → keyword-only |
| R3 | DataHub down → raw ConnectionError traceback; no transactionality on write-back | `require_gms` reachability + friendly message; write-back is best-effort per-artifact with an error summary |

## Remaining honest limitations (NOT hidden)
1. **Auto-fed scope.** `audit_dataset_from_datahub` / the MCP `audit_dataset` tool judge the
   *split methodology* from query history. Target-leakage, group-leakage, overfit and calibration
   checks exist and are unit-tested, but they only fire when a caller supplies features / group ids /
   predictions (the graph doesn't expose the feature matrix). So the fully-automatic verdict covers
   split leakage; the deeper checks are opt-in via the API. This is a scope boundary, not a bug.
2. **Calibration significance test** has a ~5% nominal false-positive rate by construction (p<0.05),
   mitigated by requiring a material effect size (ECE ≥ 0.03). At very large n a tiny-but-real
   miscalibration can trip WARN — which is arguably correct, but worth knowing.
3. **Sentinel `schema_drift` partially overlaps** DataHub's native schema-history. We position it as a
   *downstream-contract* diff (dropped/retyped columns vs what consumers depend on) layered on top,
   not a replacement — but the overlap is real and disclosed. `distribution_drift`, `null_spike`
   (as spike-vs-baseline), and value-`freshness` have no OOB DataHub equivalent.
4. **GMS-down** now raises a clear RuntimeError, but scripts still print a Python traceback rather
   than a one-line exit. Message is actionable; cosmetics could be cleaner.
5. **Private betting data is not shipped.** The reproducible demo is the public football dataset
   (~12.9k matches). The 250k-row figure is the author's aggregate private context.
6. **DataHub incident search** via GraphQL has a known DataHub-side bug for the incident entity type;
   we verify incidents via `get_aspect` (direct read), which works.

## What held up under attack (genuine robustness)
- Statistical core is **deterministic** (same input → same verdict); no unseeded RNG in the verdict path.
- **250k rows:** distribution_drift 1.1s, calibration 0.14s, target_leakage 3s; process peak RSS ~323 MB.
- Random-split detection (per-row timestamps) and memorizing-model overfit: 25/25 each in adversarial trials.
- `classify_sql` on empty/garbage/1 MB/deep-nested strings: graceful UNKNOWN, no crash.
- A generalizing model with a real train/test gap (Bike Sharing R² 0.79→0.57) correctly PASSES — no wolf-crying.
- Tag reconciliation converges (a now-clean asset loses its stale `audit-failed`).
