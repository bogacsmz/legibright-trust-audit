<p align="center"><img src="assets/legibright-lockup.svg" width="320" alt="Legibright"/></p>
<p align="center"><b>A statistical trust layer that catches overfit &amp; data leakage in DataHub.</b></p>

# Legibright — Devpost submission

> **Build with DataHub: The Agent Hackathon** · Category: *Agents That Do Real Work* · Apache-2.0
> Repo: https://github.com/bogacsmz/legibright-trust-audit

> *Every other agent produces answers. Legibright tells you which to trust — and it starts by not trusting itself.*
>
> 🔍 **14 bugs found in ourselves — and fixed** across a 3-round adversarial self-audit + demo/UI hardening,
> nothing loosened to go green. The one honesty tool that survives its own honesty test → [`docs/VERIFICATION.md`](VERIFICATION.md).

## Elevator pitch
AI agents now write the SQL, build the pipeline, and train the model — but nobody audits whether
the model they ship is *trustworthy* or just an overfit lie that looks great on paper. **Legibright
is the agent that audits statistical honesty** — temporal/target/group leakage, overfit, calibration —
and writes its verdict back into DataHub as an incident, tags, a 0–100 Trust Score, and a deprecation
proposal. It's not a text-to-SQL agent; it does the one thing DataHub's shipped tools don't.

## Why it's "Agents That Do Real Work"
*Does it do real, autonomous, useful work end-to-end?* Yes — the full loop runs with no human in the
middle until the graph is already updated and a decision is queued:
- **Reads** the dataset, lineage, and query history from DataHub over the **MCP Server** — real context, not a toy input.
- **Decides** by running statistical-honesty checks (leakage / overfit / calibration) and computing a verdict + Trust Score.
- **Acts on the graph** — opens an **Incident**, stamps **Tags**, writes the **Trust Score** as a typed property, files a **deprecation proposal**. These are native artifacts a data team already consumes, not a console print.
- **Hands off** — the verdict is inherited by the next engineer *and* by other agents, which call Legibright as an **MCP tool**. Agent-to-agent, closed loop: **detect → write back → propose → hand off.**

*Evidence:* [`src/trust_layer/agent.py`](../src/trust_layer/agent.py) · [`writeback.py`](../src/trust_layer/writeback.py) · [`mcp_server.py`](../src/trust_layer/mcp_server.py) · run it: [`demo/run_demo.sh`](../demo/run_demo.sh).

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

> ### Trust ≠ accuracy
> Legibright scores **honesty, not performance**. A bike-demand model that's only ~57% accurate but
> *honestly* 57% (clean split, no overfit) earns **Trust Score 100**; a leaky "+40% ROI winner" earns
> **28**. It rewards the modest-but-honest number and punishes the impressive lie — the opposite of
> what an accuracy dashboard does.

---

## How it scores on the six criteria (one line + clickable evidence)

**1 · Use of DataHub — deep, native, write-back.** Reads over MCP and *writes back* native Assertion +
Incident + Tag + Trust Score property + a deprecation proposal + agent avatar; installs as the 6th
DataHub Skill; built on the Agent Context Kit, extends the Data Quality Agent pattern.
→ [`writeback.py`](../src/trust_layer/writeback.py) · [`datahub_client.py`](../src/trust_layer/datahub_client.py) · [`skills/`](../skills/datahub-trust-audit/) · [`.claude-plugin/`](../.claude-plugin/)

**2 · Technical Execution — tested & reproducible.** 52/52 unit tests + a 16-check adversarial suite
(15 stand-alone, +1 write-back idempotency with DataHub up); deterministic idempotent write-back;
scales to 250k rows in seconds (~323 MB). Judge-verified from a clean clone + fresh venv.
→ [`verify_all.py`](../scripts/verify_all.py) · [`tests/`](../tests/) · [`VERIFICATION.md`](VERIFICATION.md)

**3 · Originality — the layer DataHub doesn't ship.** Statistical honesty: temporal leakage (sqlglot),
target/group leakage, overfit collapse, sample-size-aware Hosmer–Lemeshow calibration. Extend, not rewrite.
→ [`checks/honest_metrics/`](../src/trust_layer/checks/honest_metrics/) · [`split_inference.py`](../src/trust_layer/split_inference.py)

**4 · Real-World Usefulness — a market-validated need.** "Is this model trustworthy?" is an *acquired*
need (TruEra→Snowflake, Robust Intelligence→Cisco, 2024); Legibright puts it inside the catalog, as an agent, on real data.
→ the closed loop above · [`demo/SCRIPT.md`](../demo/SCRIPT.md)

**5 · Submission Quality — video + docs.** Scripted ≤3-min demo, reproducible driver, honest-limits ledger, consistent brand.
→ [`demo/SCRIPT.md`](../demo/SCRIPT.md) · [`run_demo.sh`](../demo/run_demo.sh) · [`VERIFICATION.md`](VERIFICATION.md)

**6 · Bonus · Open source.** Apache-2.0; contributes upstream a 6th skill, an RFC for statistical-honesty assertions, and a SQLite-profiling docs fix.
→ [`docs/upstream/`](upstream/) · [`OSS_CONTRIBUTION.md`](OSS_CONTRIBUTION.md)

---

## Why we're different (one line)
**We're not another text-to-SQL agent. We audit whether the number an agent produced is honest —
the thing DataHub doesn't do — write the verdict back into the graph, and prove it by surviving our
own 3-round adversarial audit (14 bugs found in ourselves, fixed).**

## Open-source contributions (contribute back)
Two prepared PRs — clickable "contribute back" evidence (the rules count RFCs, docs, and skills):
1. **New skill** → `datahub-project/datahub-skills`: the `datahub-trust-audit` skill, conforming to the
   repo template so it installs beside the official five. **PR:** _(link added on open — see [`contrib/`](../contrib/))_
2. **Docs fix** → `datahub-project/datahub`: a SQLite-profiling caveat (`max_overflow`/`NullPool`) we hit
   firsthand while ingesting demo data. **PR:** _(link added on open — see [`contrib/`](../contrib/))_

Prepared PR bodies + exact fork/push/open steps are in [`contrib/`](../contrib/); plus an RFC for
statistical-honesty assertions in [`docs/upstream/`](upstream/).

## Try it in 60 seconds
```bash
git clone https://github.com/bogacsmz/legibright-trust-audit && cd legibright-trust-audit
pip install -e '.[dev]'
python scripts/fetch_data.py         # public data → data/*.db (reproducible)
python scripts/verify_all.py         # 15 adversarial checks, NO DataHub needed → "15 passed"
bash demo/run_demo.sh                # full demo (DataHub quickstart up) → verify shows "16 passed"
```

## Honest limitations (we don't hide them)
The auto-fed verdict covers split leakage; target/group/calibration checks are opt-in (need the
caller's features). Calibration has a ~5% nominal false-positive rate by construction. `schema_drift`
partially overlaps DataHub's native schema history (disclosed). Full ledger:
**[`docs/VERIFICATION.md`](VERIFICATION.md)** — 14 flaws found+fixed (12 in a 3-round self-audit + 2
while hardening the demo/UI), 6 limits documented, nothing loosened to go green.

## Built with
DataHub **Agent Context Kit** · **MCP** (FastMCP) · **DataHub Skills** · `acryl-datahub` (SDK 1.6) ·
`sqlglot` · `numpy`/`scipy` · Python 3.

## Links
- **Repo:** https://github.com/bogacsmz/legibright-trust-audit
- **Adversarial suite:** [`scripts/verify_all.py`](../scripts/verify_all.py)
- **Verification & honest limits:** [`docs/VERIFICATION.md`](VERIFICATION.md)
- **OSS skill:** [`skills/datahub-trust-audit/`](../skills/datahub-trust-audit/)
