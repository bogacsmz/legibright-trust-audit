# RFC: Statistical-honesty assertions on top of DataHub

- Status: Draft (prepared for the DataHub community; not yet submitted)
- Author: Statistical Trust Layer contributors
- Affects: Assertions, Incidents, Agent Context Kit / Skills

## Summary
Recognize a family of **statistical-honesty assertions** as a documented CUSTOM/EXTERNAL
assertion pattern in DataHub: temporal-leakage, overfit, and calibration checks that judge
whether a metric/model built on a dataset is *trustworthy*, distinct from data-quality
assertions that judge whether the *data* is correct.

## Motivation
DataHub ships freshness, volume, column, schema, and SQL assertions — all about whether the
DATA is right. None judge whether a MODEL/METRIC derived from that data is honest. In practice
the most expensive failures are metrics that look great and are wrong: a backtest that "wins"
because of a random train/test split (leakage), an unpruned model at 0.99 train accuracy
(overfit), or a probability that is systematically miscalibrated. Teams ship these because
nothing in the catalog flags them.

These checks fit DataHub's existing model cleanly — they are just CUSTOM assertions with
EXTERNAL source and their run results, attached to the dataset (or a metric/dataJob asset),
plus an Incident on failure. No new entity type is required.

## Proposal
1. **Document a canonical shape** for statistical-honesty assertions:
   - `AssertionInfo.type = CUSTOM`, `customAssertion.type = "honest-metrics/<check>"`,
     `source.type = EXTERNAL`.
   - Run result via `AssertionRunEvent` with `AssertionResultType.SUCCESS|FAILURE` and the
     evidence in `nativeResults` (e.g. PSI, leak ratio, ECE).
2. **Split-methodology from query history.** Encourage agents to derive the train/test split
   from `get_dataset_queries` and classify it (temporal vs random) rather than trusting a
   claimed methodology. Reference implementation: sqlglot-based classifier (Apache-2.0).
3. **A skill** (`datahub-trust-audit`) that orchestrates read (MCP) → check → write-back so
   any agent can run the audit. (Submitted separately to datahub-skills.)

## Reference implementation
Provided under Apache-2.0: pure Python checks (temporal-leakage, overfit, calibration, PSI/KS
drift, null-spike, schema-drift), a DataHub emitter for assertion/incident/tag write-back, and
an MCP server. Verified end-to-end on DataHub 1.6 OSS quickstart across three domains
(sports-betting odds, UCI Bike Sharing, Kaggle Titanic) — correct verdict on each.

## Non-goals
- Not a new entity type. Not a replacement for freshness/volume/profiling assertions.
- Not a modeling framework; it audits metrics others produce.

## Open questions
- Should the natural anchor be the dataset, or a first-class `mlModel`/`dataJob` asset when one
  exists? (Proposal: attach to whatever produced the metric; fall back to the dataset.)
- Standard vocabulary for `customAssertion.type` names.
