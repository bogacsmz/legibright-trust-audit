<p align="center"><img src="../docs/assets/legibright-lockup.svg" width="300" alt="Legibright"/></p>

# Demo script — Legibright (≤ 3:00)

Every number below is produced live by `bash demo/run_demo.sh` (idempotent — take 1/2/3 match).
Each beat has **ON-SCREEN** text (for the muted juror) and **VO** (voiceover). Times are targets;
aim to land the close by 2:55. Brand: indigo `#1E1B4B`/`#4F46E5`, ✓-L logo, verdict colors stay
semantic (🟢🟡🔴). Watermark `legibright-mark.svg` bottom-right throughout.

---

### 0:00–0:18 · HOOK — the meta-position  *(title card → face/screen)*
**ON-SCREEN:** `AI agents now write the SQL, build the pipeline, train the model.` → `But is the model they ship trustworthy — or an overfit lie that looks great on paper?` → `Who audits that? → Nobody.` → **Legibright.**
**VO:** "AI agents already write SQL, build pipelines, train models. But the model they hand you — is it trustworthy, or an overfit lie that looks perfect on paper? Who checks? Nobody does. That's Legibright."
*Note: this is the wedge — everyone else at this hackathon is text-to-SQL. We audit the honesty of the result.*

### 0:18–1:25 · LIVE CATCH — the aha  *(terminal running `demo_writeback.py`, DataHub UI in a second tab)*
**ON-SCREEN (as the card prints):**
- `Dataset: main.matches — 11,849 real football matches (public, reproducible)`
- `Claim logged: "backtest_roi = +40%"  ✅ looks shippable`
- `Legibright audits →`
- `❌ TEMPORAL LEAKAGE — 99.8% of training rows dated after the earliest test match (random split in a walk-forward costume)`
- `❌ OVERFIT — +40% in-sample vs −12% holdout (gap 0.52); 677 combos scanned → ~16 false winners by chance`
- `✅ CALIBRATION — well calibrated (it does NOT flag what's fine)`
- `🔴 NOT TRUSTWORTHY · Trust Score 28/100`
- `→ DataHub: incident (ACTIVE) · tags · Trust Score property · deprecation PROPOSED`

**VO:** "Here's a dataset in DataHub and a logged claim — a backtest returning plus-forty-percent ROI. Every generic agent says ship it. Legibright audits the honesty. It measures, from the real match dates, that ninety-nine percent of the training rows are dated *after* the test period began — a random split wearing a walk-forward costume. It flags the overfit signature — plus forty in-sample, minus twelve on holdout. But calibration? It passes — Legibright doesn't cry wolf. Verdict: not trustworthy, Trust Score twenty-eight. And it doesn't just print that — it writes an incident, tags, a typed Trust Score, and even *proposes* deprecation, back into DataHub." *(cut to UI: red incident + Trust Score 28 on the asset)*
*This is the closed loop: detect → write back → propose a fix.*

### 1:25–1:55 · NO WOLF-CRYING — the moat  *(terminal `generality_check.py`)*
**ON-SCREEN:**
- `Same auditor, an HONEST model (Bike Sharing, clean time-split):`
- `🟢 TRUSTWORTHY · Trust Score 100/100`
- `A leaky one (Titanic): 🔴 NOT TRUSTWORTHY`
- `✅ Generality proven on public data unrelated to betting.`

**VO:** "A tool that flags everything red is useless. Same auditor, a genuinely honest model — it passes, green, a hundred out of a hundred. A leaky one — caught. And these are public datasets, Bike Sharing and Titanic, nothing to do with betting. It discriminates."

### 1:55–2:25 · REAL DataHub + ANY AGENT  *(show MCP call / SKILL.md / the graph)*
**ON-SCREEN:**
- `Exposed as an MCP tool → any agent can call audit_dataset(urn)`
- `Installs as the 6th DataHub Skill (setup·search·lineage·enrich·quality· + trust-audit)`
- `Writes native entities: Assertion · Incident · Tag · Structured Property`
- `Extends the Data Quality Agent pattern — not a rewrite.`

**VO:** "This isn't a toy script. It's an MCP tool any agent can call, and it installs as a sixth DataHub Skill next to the official five. It's built on DataHub's Agent Context Kit and extends the canonical Data Quality Agent pattern — adding the statistical-honesty layer DataHub doesn't ship. We compose search and quality; we don't rebuild them."

### 2:25–2:52 · MIC-DROP — it survives its own audit  *(terminal `verify_all.py`)*
**ON-SCREEN:**
- `A tool that audits others' honesty must survive the same cruelty.`
- `3-round adversarial self-audit — a separate agent tried to break it.`
- `Nothing loosened to pass. 12 real flaws found + fixed · 6 honest limits documented.`
- `48/48 tests · verify_all 16/16 · run it yourself.`

**VO:** "A tool that judges other people's honesty has to survive the same cruelty. So a separate agent spent three rounds trying to break this one — and nothing was ever loosened to go green. Twelve real flaws found and fixed, six honest limits documented in the open. Forty-eight tests, sixteen adversarial checks. Don't trust me — run verify_all yourself."

### 2:52–3:00 · CLOSE  *(close card)*
**ON-SCREEN:** ✓-L logo · **Legibright — make model trust legible.** · `github.com/bogacsmz/legibright-trust-audit`
**VO:** "Legibright. Make model trust legible."

---

## Recording notes
- Pre-open two tabs: terminal + DataHub UI on `main.matches` (Quality & Incidents). Run `run_demo.sh`
  once before recording so data/avatar are warm; the second run is your take.
- `DEMO_PAUSE=1 bash demo/run_demo.sh` pauses between beats so you can narrate without racing.
- 3 takes (our discipline mirrors the product's). Target 2:45–2:55 to stay under the 3:00 cap.
- If the terminal font is small on camera, `export FIGLET=0` — banners already use big indigo bars.
- Honesty guardrail for narration: say "measured" for leakage/calibration, "reconstructed claim"
  for the +40%/−12% overfit inputs (we judge a representative claim; we don't fabricate a fit).
