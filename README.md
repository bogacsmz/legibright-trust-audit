# Honest Metrics Auditor — a DataHub agent that tells you whether to trust a model

> **Build with DataHub: The Agent Hackathon** · Challenge: *Agents That Do Real Work* · Apache-2.0
> Deadline 10 Aug 2026.

**Before an ML/data team trusts a model, this agent automatically audits whether the model
actually works — or whether it just fits stale data (overfit / temporal leakage).** It reads
the model's dataset and lineage from DataHub via the **MCP Server**, runs the statistical
honesty tests that a plain "look, it's profitable!" backtest hides, and **writes the verdict
back into the DataHub graph** as an Assertion + Incident + Tag — so the whole team inherits it.

## The star: the Auditor (this is the original part)
DataHub already ships freshness/volume assertions, profiling, and incidents. It does **not**
ship *statistical honesty*. That's what we add on top:

| Auditor check | The lie it catches (that a single ROI number hides) |
|---|---|
| **Temporal leakage** | training rows dated after the test cutoff — a random split wearing a walk-forward costume; the model "saw the future" |
| **Overfit red flags** | implausible in-sample ROI, in-sample ≫ holdout, multiple-testing luck (N cells scanned → expected false winners) |
| **Calibration / favorite-longshot bias** | systematic probability miscalibration a good-looking accuracy score papers over |

Verdict: 🟢 TRUSTWORTHY / 🟡 INCONCLUSIVE / 🔴 NOT TRUSTWORTHY — stamped onto the asset in DataHub.

The supporting cast: a **Sentinel** data-health suite that *extends* DataHub (each check reads
what DataHub already knows and adds the temporal/baseline layer it doesn't ship):

| Sentinel check | Reads from DataHub | Adds |
|---|---|---|
| freshness | write-time status + profile stdev | value-dynamics: a feed that updates on schedule but froze |
| distribution-drift | column distribution profiles | PSI + KS drift vs baseline (point-in-time profile can't) |
| null-spike | per-column null counts | anomaly test: is today's null rate an abnormal spike |
| schema-drift | SchemaMetadata | breaking-change diff: dropped/retyped columns |

Sentinel guards the *source*; the Auditor judges the *metric* built on it.

## Why this isn't just another AI+MCP agent
The moat is domain honesty. The reproducible demo runs on **~12,900 real matches** of public
football closing odds (Pinnacle + bookmakers, football-data.co.uk) that `fetch_data.py` downloads
for you — the Auditor catches a fake +40% ROI edge live and you watch the AUDIT FAILED verdict
appear in the DataHub UI. The protocol itself was distilled from the author's larger private
betting pipelines (horse-racing + live football snapshots, ~250k rows in aggregate, not shipped)
where this same honest-validation discipline repeatedly rejected profitable-looking-but-overfit
edge candidates. Everything a judge runs here is public and reproducible; the private-data
provenance is context, not a claim you have to take on faith.

## The agent does real work: auto-fed from DataHub, callable over MCP
You don't hand it a split. Point it at a dataset URN and it **reads how the train/test split
was actually built** from DataHub's query history (`get_dataset_queries`), classifies the SQL
with sqlglot — TEMPORAL (clean) vs RANDOM/hash/TABLESAMPLE (leakage) — and judges the
methodology at the source. Then it writes the verdict back.

And it's exposed as an **MCP server** so any agent (Claude, Cursor, another pipeline) can call it:
```
python -m trust_layer.mcp_server         # tools: audit_dataset, classify_split_sql, list_auditor_skills
```
```bash
python scripts/seed_queries.py leaky      # a data scientist logs a random-split query
python scripts/audit_auto.py              # agent reads it, catches the leak, writes verdict — no hardcoded split
```

## Contribute back to the graph (verified live)
On a verdict the agent emits, against live GMS:
- a **CUSTOM/EXTERNAL Assertion** + run result (SUCCESS/FAILURE) → DataHub's Data-Quality tab,
- an **ACTIVE Incident** with the failure detail → the asset's Incidents tab,
- **Tags** (`audit-failed`, `contaminated-upstream`) → fast visible signal.

`src/trust_layer/writeback.py` is verified end-to-end (write → read-back) on DataHub 1.6.

## Quickstart (fully reproducible from a clean clone)
```bash
pip install -e .                 # engine + CLI + MCP server (installs acryl-datahub[sqlalchemy])
trust-layer selftest             # statistical core — no DataHub, no data needed (start here)

python scripts/fetch_data.py     # download PUBLIC data → data/matches.db + data/generality.db
bash scripts/quickstart_up.sh    # local DataHub at :9002 (UI) / :8080 (GMS), login datahub/datahub
datahub ingest -c ingest/recipes/matches.yml       # ingest the public odds → main.matches

python scripts/milestone1.py     # read a dataset's health from DataHub, end-to-end
python scripts/demo_writeback.py # Auditor on real matches → live 🔴 verdict written to the UI
python scripts/generality_check.py  # proof on Bike Sharing + Titanic (non-betting)
python scripts/seed_queries.py leaky && python scripts/audit_auto.py  # auto-fed from query history

pip install -e '.[dev]' && pytest -q                # run the test suite (25 tests)
```
MCP wiring for judges (drive it from Claude/Cursor): `scripts/mcp_config.json`.
Env: `datahub ingest` reads `MATCHES_DB` / `DATAHUB_GMS_URL` (both default sensibly; see `.env.example`).

## Layout
- `src/trust_layer/checks/honest_metrics/` — **the Auditor** (registry-packaged for OSS reuse)
- `src/trust_layer/checks/freshness.py` — the Sentinel (extends DataHub, supporting)
- `src/trust_layer/writeback.py` — Assertion + Incident + Tag emission (live-verified)
- `src/trust_layer/agent.py` — orchestration + lineage propagation
- `ingest/`, `demo/scenario.md`, `docs/PLAN.md`, `docs/OSS_CONTRIBUTION.md`

## Status
M0 scaffold ✅ · M1 live read ✅ · M2 write-back ✅ (Assertion+Incident+Tag land in GMS).
Next: demo seed + honest-metrics run on real data. See `docs/PLAN.md`.
