# Verification & Honest Limitations

> **15 bugs found in ourselves, and fixed** — 12 across a 3-round adversarial self-audit,
> plus 3 caught while hardening the demo/UI and in a fresh delta audit. **No test or check was
> ever loosened to go green.**

This project audits other people's models for honesty, so it must survive the same scrutiny.
On 8 Jul 2026 we ran a 3-round adversarial self-audit: each round a **separate, clean-context
subagent** with a different adversary role, read-only on the repo (grader), while the author
fixed findings (builder). Flaws 13–15 surfaced later — while preparing the demo, hardening the UI,
and running a fresh delta-verification pass — recorded here too, because hiding a bug you found
yourself would defeat the entire point of the tool. Every finding was either honestly fixed or is
recorded below as a known limitation.

Run `python scripts/verify_all.py` to reproduce the regression checks. It runs **16 checks: 15
stand-alone with no DataHub**, and a 16th (write-back idempotency) when the GMS quickstart is up —
so you'll see `15 passed` offline and `16 passed` with DataHub running.

## What was tested
- **Round 1 (skeptical judge):** clean-room reproduce from README in a fresh venv; install path;
  every concrete claim vs reality; reproducibility of the "real data" demos.
- **Round 2 (ML expert):** adversarial data to force wrong verdicts — hidden target/group/temporal
  leakage; overfit-threshold blind spots; calibration false pos/neg; false-positive/negative rates
  over 100+ real sklearn models; determinism; overfit-to-3-datasets.
- **Round 3 (chaos/reliability):** degenerate inputs (empty query history, all-null, single row,
  broken/huge SQL); idempotency (re-run → duplicate incidents?); DataHub down; 250k-row time/memory;
  partial-write consistency; incident lifecycle.

## Found & fixed — 15 flaws (evidence in git history: c594766, 443fb46, 73ed511, b738c54, c0771f3, + delta pass)
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
| Demo-prep | **False green (calibration):** hard-label / non-probabilistic predictions (e.g. an overfit tree's `predict_proba` returning 0/1) make Hosmer-Lemeshow undefined — every bin has E∈{0,ng}, denom=0, χ²=0, p=1 — so a badly-calibrated model (Titanic, ECE 0.254) was stamped "well calibrated". The R2 HL fix had its own blind spot. | Guard on HL validity: if <2 bins contribute to χ² (test degenerate) and observed ECE is material, return **WARN "not certifiable"**, never OK. OK message now leads with ECE, not a bare contradictory p. +3 calibration tests (`test_robustness.py`). |
| UI-hardening | **Silent-swallow — the exact failure we hunt, in our own code:** the Auditor-owner write threw (the ownership-type aspect was missing required `created`/`lastModified` stamps) but the best-effort `_try` in write-back swallowed the exception — the demo logged success while **nothing was written to the graph**. Caught only by reading the graph back, not trusting the log. | Fixed the aspect; write-back already surfaces a partial-write error summary; **+1 test** (`test_writeback_owner`) asserts the owner lands as a custom *Auditor* type. |
| Delta-pass | **False green (calibration, residual of #Demo-prep):** the degenerate-HL guard only caught *full* degeneracy (`used < 2`). A model that is soft-and-honest on some rows but confidently-wrong hard 0/1 on others drops only the hard bins from χ² (`2 ≤ used < n_bins`), gets a high p, and reached the OK branch — so a 60%-miscalibrated model (ECE 0.60) was stamped "well calibrated". Found by a **fresh delta grader**. | Generalized the guard: **any** dropped bin (`used < len(bins)`) with material ECE ⇒ WARN "not certifiable", never OK. **+1 test** (`test_calibration_partial_degenerate_not_green`). |

## Delta-verification pass (fresh grader, 8 Jul)
After the OSS PRs, a fresh read-only grader re-audited every claim in README/SUBMISSION/SCRIPT against
code/tests, adversarially attacked the newer code paths (owner-write, Trust Score, deprecation,
`reconcile_tags`, `cleanup_incidents`, calibration), swept for stale numbers/links, and re-ran the
judge quickstart from a clean clone. It found the **#Delta-pass** calibration silent-green above (fixed)
and several honesty nits, all fixed: stale test counts (a `(25 tests)` and `25/25` left in README/PLAN),
a README "~12,900" vs the demo's actual **11,849 audited** matches, `cleanup_incidents.py` deleting
*all* incidents on the demo datasets rather than only trust-layer-authored ones (now filtered), and the
unverifiable "250k rows … 323 MB" figure (now reproducible via `scripts/bench_scale.py`). What held up:
all core verdict numbers, idempotency, the OSS PRs, MCP tool, owner/avatar, deprecation proposal.

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
5. **Private betting data is not shipped.** The reproducible demo audits the public football dataset
   (11,849 complete-odds matches of 12,904). The 250k-row *scale* claim is now judge-reproducible on
   synthetic data via `scripts/bench_scale.py`; the private betting corpus itself is not shipped.
6. **DataHub incident search** via GraphQL has a known DataHub-side bug for the incident entity type;
   we verify incidents via `get_aspect` (direct read), which works.

## What held up under attack (genuine robustness)
- Statistical core is **deterministic** (same input → same verdict); no unseeded RNG in the verdict path.
- **250k synthetic rows** (reproducible: `python scripts/bench_scale.py`): each of distribution_drift,
  calibration, and target_leakage runs **sub-second**; process peak RSS **~210–240 MB** (machine-dependent).
- Random-split detection (per-row timestamps) and memorizing-model overfit: 25/25 each in adversarial trials.
- `classify_sql` on empty/garbage/1 MB/deep-nested strings: graceful UNKNOWN, no crash.
- A generalizing model with a real train/test gap (Bike Sharing R² 0.79→0.57) correctly PASSES — no wolf-crying.
- Tag reconciliation converges (a now-clean asset loses its stale `audit-failed`).
