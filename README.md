<p align="center">
  <img src="docs/assets/legibright-lockup.svg" width="320" alt="Legibright"/>
</p>
<p align="center">
  <b>A statistical trust layer that catches overfit &amp; data leakage in DataHub.</b>
</p>
<p align="center">
  <i>Every other agent produces answers. Legibright tells you which to trust — and it starts by not trusting itself.</i>
</p>
<p align="center">
  🔍 <b>15 bugs found in ourselves — and fixed.</b> A 3-round adversarial self-audit + demo/UI hardening + a fresh delta audit → <a href="docs/VERIFICATION.md">VERIFICATION.md</a>
</p>

# Statistical Trust Layer — an autonomous DataHub agent that audits whether a model can be trusted

> **Build with DataHub: The Agent Hackathon** · Category: **Agents That Do Real Work** · Apache-2.0 · Deadline 10 Aug 2026.
>
> Brand: **Legibright** — the "L" is a ✓ (checkmark), the audit/trust mark. Palette: indigo
> `#1E1B4B` / `#4F46E5` / `#6366F1`. Assets in [`docs/assets/`](docs/assets/).

**Agents That Do Real Work — end to end.** Agents need reliable context before they act. Legibright
is that trust gate: it decides which datasets and models an agent can safely rely on, before the
agent acts on them. It's an autonomous agent, not a validation library — it reads a model's dataset
and lineage from DataHub over the **MCP Server**, runs the statistical-honesty checks a "look, it's
profitable!" backtest hides, and then *acts on the graph*: it opens an **Incident**, stamps **Tags**,
writes a 0–100 **Trust Score** property, and files a **deprecation proposal** for a human to approve.
Other agents invoke it as an MCP tool. **Closed loop: detect → write to the catalog → propose a
fix → hand off.** The verdict lives as a first-class DataHub citizen next to the data it's about —
not a side report in a console or a Slack message. Trust belongs in the catalog.

> **Trust ≠ accuracy.** Legibright scores *honesty*, not performance. A bike-demand model that's only
> ~57% accurate but *honestly* 57% (clean split, no overfit) earns **Trust Score 100**; a leaky
> "+40% ROI winner" earns **28**. It rewards the modest-but-honest number and punishes the impressive lie.

## Judge quickstart — try it in 60 seconds
Tested end-to-end from a clean clone + fresh venv (Python 3.11–3.13):
```bash
git clone https://github.com/bogacsmz/legibright-trust-audit && cd legibright-trust-audit
python -m venv .venv && source .venv/bin/activate         # clean, optional
pip install -e '.[dev]'
python scripts/fetch_data.py     # public data → data/*.db (12,904 matches + Titanic + Bike)
python scripts/verify_all.py     # 15 adversarial checks — NO DataHub needed → "15 passed"
```
That's the honest core, no infra. For the full write-back demo (verdicts land in the graph):
```bash
bash scripts/quickstart_up.sh    # starts local DataHub at http://localhost:9002 (first run pulls images)
bash demo/run_demo.sh            # audits 3 datasets, writes back, and reruns verify → "16 passed"
```
`verify_all` prints **15 passed** offline and **16 passed** with DataHub up (the 16th check is
write-back idempotency). No PYTHONPATH or env fiddling required.

## Positioning: extend, don't rewrite
This **extends DataHub's canonical Data Quality Agent pattern**. It composes the official
`datahub-search` / `datahub-lineage` / `datahub-quality` skills (search, lineage, query history,
assertions, incidents) and adds the one thing they don't ship: the **statistical honesty of a
metric** built on the data. DataHub's shipped skills answer *"is the DATA correct?"*; this
answers *"is the NUMBER trustworthy?"*. We write verdicts back through DataHub's own
Assertion / Incident / Tag entities — not reimplemented, extended.

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
The moat is domain honesty. The reproducible demo audits **11,849 real matches** (the complete-odds
subset of a 12,904-row public dataset) of
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
- an **Incident** with the failure detail → the asset's Incidents tab (auto-resolved when a check later passes),
- reconciled **Tags** (`audit-failed`, `temporal-leakage`, …) → fast visible signal,
- a typed **Trust Score (0-100)** as a numeric **structured property** — queryable/sortable in the catalog.

**Trust Score ≠ DataHub Analytics Agent's context-quality-score.** Theirs measures how well the
catalog metadata supported a question (context completeness). Ours measures whether *this dataset's
metric/model claim is statistically trustworthy* (leakage/overfit/calibration) — a different axis.

Write-back is **idempotent** (deterministic entity keys per dataset+check → re-runs update, never
duplicate) and verified end-to-end (write → read-back) on DataHub 1.6. See `docs/VERIFICATION.md`.

**Governed, not unilateral (opt-in).** With `propose_deprecation=True`, an untrustworthy verdict
also files a **deprecation proposal** (`deprecated=false` + a note) — the agent proposes, a human
approves. It respects DataHub's governance model rather than deleting/deprecating on its own.

## Install as a DataHub skill
`skills/datahub-trust-audit/` conforms to the `datahub-project/datahub-skills` format (SKILL.md +
`references/` + `templates/`), and `.claude-plugin/{plugin,marketplace}.json` make it installable as
a Claude Code plugin — a 6th skill alongside the official five (setup/search/lineage/enrich/quality).
Submittable upstream as-is; see `docs/OSS_CONTRIBUTION.md` and `docs/upstream/`.

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

pip install -e '.[dev]' && pytest -q                # run the test suite (53 tests)
```
MCP wiring for judges (drive it from Claude/Cursor): `scripts/mcp_config.json`.
Env: `datahub ingest` reads `MATCHES_DB` / `DATAHUB_GMS_URL` (both default sensibly; see `.env.example`).

## Data sources
The reproducible demo (`scripts/fetch_data.py`) downloads three public, redistributable datasets —
no private data is required to run or verify anything in this repo:
- **[football-data.co.uk](https://www.football-data.co.uk/)** — public football match results and
  closing odds, free for personal/research use.
- **[UCI Machine Learning Repository — Bike Sharing Dataset](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset)**
  — public domain, cited per UCI's terms.
- **[Kaggle / Titanic](https://www.kaggle.com/c/titanic)** (the classic `datasciencedojo` mirror) —
  public dataset used for the standard educational classification task.

See `examples/` for sample Legibright outputs on all three, generated by `scripts/gen_examples.py`.

## Layout
- `src/trust_layer/checks/honest_metrics/` — **the Auditor** (registry-packaged for OSS reuse)
- `src/trust_layer/checks/freshness.py` — the Sentinel (extends DataHub, supporting)
- `src/trust_layer/writeback.py` — Assertion + Incident + Tag emission (live-verified)
- `src/trust_layer/agent.py` — orchestration + lineage propagation
- `ingest/`, `docs/OSS_CONTRIBUTION.md`, `examples/` (sample outputs)

## Demo & submission
- **[`demo/SCRIPT.md`](demo/SCRIPT.md)** — the ≤3-min video script (on-screen text + voiceover), every
  number produced live. **[`demo/run_demo.sh`](demo/run_demo.sh)** — reproducible, idempotent driver.
- **[`demo/RECORDING_GUIDE.md`](demo/RECORDING_GUIDE.md)** — turnkey recording runbook (setup, scene-by-scene
  steps, tools). **[`demo/reset_demo.sh`](demo/reset_demo.sh)** — resets the DataHub catalog to the clean
  demo state before every take.
- **[`docs/SUBMISSION.md`](docs/SUBMISSION.md)** — the Devpost writeup (six criteria, each with evidence).
- **[`demo/TITLE_CARDS.md`](demo/TITLE_CARDS.md)** + `demo/cards/` — brand title cards & thumbnail (PNG, ready to use).

## We audited ourselves (a trust tool must survive its own scrutiny)
A 3-round adversarial self-audit (separate clean-context grader agents; author as builder;
**no test ever loosened to go green**) found and fixed real blind spots — silent green on empty
evidence, a 41% false-red calibration bias, invisible target/group leakage, non-idempotent
write-back. All fixed and locked as regressions. See **`docs/VERIFICATION.md`** for the full
tested / fixed / honest-limitations ledger, and run:
```bash
python scripts/verify_all.py     # 15 checks stand-alone (no DataHub); 16 with the quickstart up
```

## Status
M0 scaffold ✅ · M1 live read ✅ · M2 write-back ✅ · auto-fed + MCP ✅ · Sentinel suite ✅ ·
OSS skill ✅ · self-audit ✅ (53 tests + verify_all 15 stand-alone / 16 with DataHub, green).
