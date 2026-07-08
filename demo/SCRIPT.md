<p align="center"><img src="../docs/assets/legibright-lockup.svg" width="300" alt="Legibright"/></p>

# Demo script — Legibright (final read-aloud version, ≤ 3:00)

**Reading speed:** ~130 words per minute (slow and clear). Pause 1–2 seconds between scenes —
let the last card or number sit on screen before you speak again.
**Total voiceover: ~325 words** (~2:30 of speech), leaving room for pauses and screen time to land
under 3:00.

**Pronunciation help (say these slowly):**
- **Legibright** → "LEJ-ih-bright" (like "legible" + "bright")
- **DataHub** → "DAY-ta-hub"
- **MCP** → say the letters: "M... C... P"
- **99.8 percent** → say it in three small pieces: "ninety-nine ~ point eight ~ percent"

Every number below is produced live by `bash demo/run_demo.sh` — it's the same on every take.
Verdict colors stay as-is on screen (🟢🟡🔴); title/transition cards are indigo `#1E1B4B` with the
✓-L logo (`demo/cards/*.png`, ready to drop into your editor).

---

## Scene 1 — Hook (0:00–0:15)
[SCREEN: Title card — `demo/cards/title-open.png`]
[ON-SCREEN TEXT: "Who checks if an AI's model is trustworthy? Nobody. Until now."]
[VOICEOVER: "AI agents can write code, build pipelines, and train models. But is the model any good? Or does it just look good on paper? Right now, nobody checks. Legibright checks. And it starts by checking itself."]

## Scene 2 — The Catch (0:15–1:00)
[SCREEN: Terminal running `demo/run_demo.sh`, Beat 1 (`demo_writeback.py`) — let the verdict card print live, then cut to the DataHub UI on `main.matches` (Incidents + Quality tabs)]
[ON-SCREEN TEXT: "11,849 real matches. Claim: +40% profit. 99.8% of the training data is from AFTER the test period. Trust Score: 28/100."]
[VOICEOVER: "Here is real data: almost twelve thousand football matches. A model claims plus-forty-percent profit. Looks like a big win. Legibright checks it. It finds that ninety-nine ~ point eight ~ percent of the training data came from AFTER the test period. That is not a fair test. The model saw the future. Legibright gives it a Trust Score: twenty-eight out of one hundred. Not trustworthy. And it writes this straight into DataHub: an incident, a tag, the score, and a note saying 'maybe remove this dataset.'"]

## Scene 3 — Trust, Not Accuracy (1:00–1:35)
[SCREEN: Transition card `demo/cards/transition-trust-accuracy.png` (1–2 sec), then terminal Beat 2 (`generality_check.py`) showing Bike Sharing pass, then Titanic fail]
[ON-SCREEN TEXT: "Bike demand model: only 57% accurate. But HONEST. Trust Score: 100/100."]
[VOICEOVER: "Now watch this. Same tool, an honest model this time: predicting bike demand. It is only fifty-seven percent accurate. Not amazing. But it is HONESTLY fifty-seven percent — clean data, no cheating. Trust Score: one hundred out of one hundred. Legibright does not score accuracy. It scores honesty. A high number built on a lie fails. A small number built the right way passes. And a leaky model, Titanic survival, gets caught again."]

## Scene 4 — Real DataHub, Any Agent (1:35–2:00)
[SCREEN: Quick look at `skills/datahub-trust-audit/SKILL.md`, then cut back to the DataHub UI Quality tab (3 FAIL assertions) and the Trust Score property]
[ON-SCREEN TEXT: "Any agent can call this over MCP. Installs as a DataHub Skill. Writes real data back."]
[VOICEOVER: "This is not just a demo script. Any AI agent can call Legibright, using something called MCP. It installs as a new DataHub Skill, next to the five official ones. It builds ON TOP of DataHub — it does not replace it. It writes real data back: an assertion, an incident, a tag, a score."]

## Scene 5 — Mic Drop (2:00–2:35)
[SCREEN: Transition card `demo/cards/transition-self-audit.png` (1–2 sec), then terminal Beat 3 (`pytest` + `verify_all.py`) showing "53 passed" and "16 passed, 0 failed"]
[ON-SCREEN TEXT: "15 real bugs found in OUR OWN code. All fixed. 53 tests, all green. Run it yourself."]
[VOICEOVER: "One more thing. A tool that checks other people's honesty must be honest about itself. So we brought in a second AI agent — just to try to break this one. Three rounds of attacks. We found fifteen real bugs, in our OWN code. We fixed every one. Nothing was hidden. Fifty-three tests, all green. Do not trust me — run it yourself."]

## Scene 6 — Close (2:35–2:48)
[SCREEN: Closing card — `demo/cards/title-close.png`]
[ON-SCREEN TEXT: "Legibright — make model trust legible. github.com/bogacsmz/legibright-trust-audit"]
[VOICEOVER: "Legibright. Make model trust legible. Thank you."]

---

## Recording notes
- Run `bash demo/reset_demo.sh` right before you record (and before each retake) — it wipes and
  rebuilds the DataHub catalog to the exact clean demo state (matches 28, titanic 25, bikeshare
  100), so every take starts identical.
- `DEMO_PAUSE=1 bash demo/run_demo.sh` pauses between beats so you can narrate without racing.
- 3 takes is our own discipline — record 3, pick the cleanest.
- Honesty guardrail for narration: say "checks" or "finds," not "proves." Say "reconstructed
  claim" in your head for the +40%/−12% numbers if asked — Legibright judges a representative
  claim on real match dates, it doesn't fabricate a backtest.
- Full step-by-step walkthrough (what to click, how long to hold each screen): `demo/RECORDING_GUIDE.md`.
