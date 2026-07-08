<p align="center"><img src="assets/legibright-lockup.svg" width="320" alt="Legibright"/></p>
<p align="center"><b>A statistical trust layer that catches overfit &amp; data leakage in DataHub.</b></p>

# Legibright — Devpost submission

> **Build with DataHub: The Agent Hackathon** · Category: *Agents That Do Real Work* · Apache-2.0
> Repo: https://github.com/bogacsmz/legibright-trust-audit

## Elevator pitch
AI agents now write the SQL, build the pipeline, and train the model — but nobody audits whether
the model they ship is *trustworthy* or just an overfit lie that looks great on paper. **Legibright
is the agent that audits statistical honesty** — temporal/target/group leakage, overfit, calibration —
and writes its verdict back into DataHub as an incident, tags, a 0–100 Trust Score, and a deprecation
proposal. It's not a text-to-SQL agent; it does the one thing DataHub's shipped tools don't.

## The problem
DataHub tells you if the *data* is fresh, complete, and profiled. Nothing tells you if a *number*
built on that data — "this model is 95% accurate", "+40% ROI" — is honest. That gap is where careers
and money die: a random train/test split masquerading as walk-forward, a leaked target feature, an
overfit curve that evaporates in production. Generic AI agents happily ship all three.

## What Legibright does (live, on real data)
On `main.matches` — 11,849 real football matches (public football-data.co.uk, reproducible) — it
audits a logged `backtest_roi = +40%` claim and, in one run:
- **Measures temporal leakage:** 99.8% of training rows are dated after the earliest test match — a
  random split, not a time cut. 🔴
- **Flags the overfit signature:** +40% in-sample vs −12% holdout (gap 0.52); 677 combos scanned →
  ~16 false winners expected by chance. 🔴
- **Passes calibration:** it does *not* flag what's genuinely fine. ✅
- **Verdict: NOT TRUSTWORTHY, Trust Score 28/100** — written back as 3 assertions, 1 ACTIVE incident,
  tags, a typed Trust Score property, and a **deprecation proposal** (agent proposes, human approves).

Then it proves it doesn't cry wolf: an honest model (Bike Sharing) passes 🟢 **100/100**, a leaky one
(Titanic) fails 🔴 — on public datasets unrelated to betting.

---

## How it scores on the six criteria (each with evidence)

**1 · Use of DataHub — deep, native, write-back.**
MCP tool (`audit_dataset(urn)`, any agent can call) · installs as the **6th DataHub Skill** beside the
official five (setup/search/lineage/enrich/quality) · writes native **Assertion + Incident + Tag +
Structured Property (Trust Score)** + a **Deprecation proposal** · sets the agent's **avatar** in the
graph. Built on the **Agent Context Kit**; extends the canonical **Data Quality Agent** pattern.
*Evidence:* `src/trust_layer/writeback.py`, `datahub_client.py`, `skills/datahub-trust-audit/`,
`.claude-plugin/`. Verified write→read-back on DataHub 1.6.

**2 · Technical Execution — tested and reproducible.**
48/48 unit tests + a 16/16 adversarial regression suite (`scripts/verify_all.py`). Write-back is
**idempotent** (deterministic entity keys → re-runs update, never duplicate) with incident lifecycle
(resolves on FAIL→OK) and best-effort transactionality. Scales: on 250k rows, distribution-drift 1.1s,
calibration 0.14s, target-leakage 3s, peak RSS ~323 MB. *Evidence:* `tests/`, `docs/VERIFICATION.md`.

**3 · Originality — the layer DataHub doesn't ship.**
DataHub ships freshness/volume/profiling. Legibright adds *statistical honesty*: temporal leakage
(SQL-classified via sqlglot), target/group leakage, overfit collapse, and a sample-size-aware
Hosmer–Lemeshow calibration test. **Extend, not rewrite** — it composes `datahub-search` and
`datahub-quality`. *Evidence:* `src/trust_layer/checks/honest_metrics/`, `split_inference.py`.

**4 · Real-World Usefulness — a market-validated need.**
"Is this model trustworthy?" is a real, acquired need: **TruEra** (ML observability) was acquired by
**Snowflake** (2024) and **Robust Intelligence** (AI validation) by **Cisco** (2024). Legibright puts
that discipline *inside the catalog the whole team already uses*, as an agent, for free. *Evidence:*
the closed loop above — detect → write back → propose fix — on real data.

**5 · Submission Quality — this video + docs.**
A ≤3-minute scripted demo (`demo/SCRIPT.md`), a reproducible driver (`demo/run_demo.sh`), a README
with a clear "extend not rewrite" positioning, and an honest-limitations ledger. Consistent brand
(Legibright, ✓-L mark).

**6 · Bonus · Open source.**
Apache-2.0. Contributes upstream: the **6th skill** (`datahub-trust-audit`, registry-format), an
**RFC** for statistical-honesty assertions, and a **SQLite profiling docs fix**. *Evidence:*
`docs/upstream/`, `docs/OSS_CONTRIBUTION.md`.

---

## Why we're different (one line)
**We're not another text-to-SQL agent. We audit whether the number an agent produced is honest —
the thing DataHub doesn't do — and write the verdict back into the graph.**

## Try it in 60 seconds
```bash
git clone https://github.com/bogacsmz/legibright-trust-audit && cd legibright-trust-audit
pip install -e '.[dev]'
python scripts/fetch_data.py         # public data → data/*.db (reproducible)
python scripts/verify_all.py         # 16/16 adversarial checks (no DataHub needed)
bash demo/run_demo.sh                # full demo (needs DataHub quickstart up)
```

## Honest limitations (we don't hide them)
The auto-fed verdict covers split leakage; target/group/calibration checks are opt-in (need the
caller's features). Calibration has a ~5% nominal false-positive rate by construction. `schema_drift`
partially overlaps DataHub's native schema history (disclosed). Full ledger:
**[`docs/VERIFICATION.md`](VERIFICATION.md)** — 12 flaws found+fixed across a 3-round self-audit, 6
limits documented, nothing loosened to go green.

## Built with
DataHub **Agent Context Kit** · **MCP** (FastMCP) · **DataHub Skills** · `acryl-datahub` (SDK 1.6) ·
`sqlglot` · `numpy`/`scipy` · Python 3.

## Links
- **Repo:** https://github.com/bogacsmz/legibright-trust-audit
- **Adversarial suite:** [`scripts/verify_all.py`](../scripts/verify_all.py)
- **Verification & honest limits:** [`docs/VERIFICATION.md`](VERIFICATION.md)
- **OSS skill:** [`skills/datahub-trust-audit/`](../skills/datahub-trust-audit/)
