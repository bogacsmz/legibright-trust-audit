# Recording Guide — the only file you need to record the demo

Follow this top to bottom like a recipe. It's synced 1:1 with [`SCRIPT.md`](SCRIPT.md) — same
scene numbers, same numbers, same words. `SCRIPT.md` is what you *read*; this is what you *do*.

## Before you hit record (5 minutes)

1. **Turn on Do Not Disturb** (macOS: Control Center → Focus → Do Not Disturb). No Slack popups,
   no message banners mid-take.
2. **Close every browser tab except one.** Open a fresh Chrome/Safari window, just the DataHub UI.
   Close bookmarks bar, extensions toolbar — anything that isn't the page content.
3. **Open one terminal window**, large font (18–20pt), dark theme, nothing else on screen. `cd` into
   the repo:
   ```bash
   cd ~/Claude/Projects/hackathon
   ```
4. **Reset the demo catalog** — do this before every single take, no exceptions:
   ```bash
   bash demo/reset_demo.sh
   ```
   Wait for `READY TO RECORD` at the end. If it prints `NOT CLEAN`, read the mismatch line and
   run it again — don't record until you see `READY TO RECORD`.
5. **Pre-navigate the browser tab** to `http://localhost:9002/dataset/urn:li:dataset:(urn:li:dataPlatform:sqlite,main.revenue,PROD)/Incidents`
   so it's one click away from Scene 2 — but don't switch to it until the script tells you to.
6. Have `demo/cards/title-open.png`, `transition-trust-accuracy.png`, `transition-self-audit.png`,
   and `title-close.png` open in Preview (or already imported into your editor timeline) so you can
   cut to them instantly.

## Recording tool

- **Screen + mic, one file:** macOS **QuickTime Player** → File → New Screen Recording → pick the
  mic → record. Free, built in, no watermark.
- **Trim + add title cards:** **CapCut** (free, no watermark on export) or iMovie. Drop the 5 PNGs
  from `demo/cards/` onto the timeline at the points marked below.
- **No music, no royalty question to worry about:** the terminal keystrokes and DataHub UI are the
  visual, your voice is the only audio track. If you want a bed track, use CapCut's built-in
  royalty-free library only — don't pull anything from outside it.
- **Keep it under 3:00.** `SCRIPT.md`'s voiceover is ~320 words at ~130 wpm ≈ 2:30 of speech. The
  scene timings below add the screen-holds and land you at ~2:48, leaving ~10s of margin.

## Scene-by-scene (do this, read that)

### Scene 1 — Hook · 0:00–0:15
- **Show:** `demo/cards/title-open.png` full-screen. Hold it the whole scene.
- **Read:** the Scene 1 VOICEOVER line in `SCRIPT.md` (starts "AI agents can write code...").
- Hold 1 second of silence on the card before you start talking, and 1 second after — gives your
  editor room to trim the cut cleanly.

### Scene 2 — The Catch · 0:15–1:00 (longest scene, ~45s)
- **Switch to the terminal.** Run:
  ```bash
  DEMO_PAUSE=1 bash demo/run_demo.sh
  ```
  Let it print the intro banner and the avatar line, then press Enter once to reach **BEAT 1**.
- The verdict card prints live (temporal_leakage ❌, overfit_flags ❌, Trust Score 28/100 — the
  revenue forecaster that scored R² 1.00 in training). **Start reading the Scene 2 VOICEOVER as soon as the card starts printing** — your
  words and the numbers appearing on screen should land close together.
- When the card finishes printing and the "writing verdict back into DataHub" lines appear, **cut
  to the pre-navigated browser tab** (`main.revenue` → Incidents). Let it sit for 3–4 seconds so
  the viewer can read the red incident row and the Trust Score.
- Don't press Enter to continue yet — pause the terminal here, you'll come back to it in Scene 5.

### Scene 3 — Trust, Not Accuracy · 1:00–1:35
- **Show:** `demo/cards/transition-trust-accuracy.png` for 1–2 seconds (silent, just the card).
- **Switch back to the terminal**, press Enter to reach **BEAT 2**. It runs `generality_check.py`
  and prints Bike Sharing (🟢 TRUSTWORTHY, Trust Score 100/100) then Titanic (🔴 NOT_TRUSTWORTHY).
- **Read the Scene 3 VOICEOVER** while this prints — time it so "Trust Score: one hundred out of
  one hundred" lands right when that line appears on screen.

### Scene 4 — Real DataHub, Any Agent · 1:35–2:00
- **Open** `skills/datahub-trust-audit/SKILL.md` in your editor (VS Code, or `cat` it in a second
  terminal tab) — just 2–3 seconds, enough to show it's a real file with real frontmatter.
- **Cut back to the browser tab**, `main.revenue` → **Quality** tab this time (2 FAIL assertions)
  — then the **Properties** tab showing the Trust Score row.
- **Read the Scene 4 VOICEOVER** over this — it's short, keep the cuts moving.

### Scene 5 — Mic Drop · 2:00–2:35
- **Show:** `demo/cards/transition-self-audit.png` for 1–2 seconds.
- **Switch to the terminal**, press Enter to reach **BEAT 3**. It runs `pytest` then
  `verify_all.py` — you'll see `53 passed` and then `16 passed, 0 failed` near the end.
- **Read the Scene 5 VOICEOVER** as those two lines print. Let "53 passed" and "16 passed" actually
  be visible on screen while you say "fifty-three tests, all green."

### Scene 6 — Close · 2:35–2:48
- **Show:** `demo/cards/title-close.png` full-screen.
- **Read:** "Legibright. Make model trust legible. Thank you."
- Hold the card 2 extra seconds after you stop talking before you cut.

## Retaking a scene
Just re-run `bash demo/reset_demo.sh` and start over from Scene 1 — it rebuilds the exact same
verdicts every time (28 / 25 / 100), so a stitched-together take from run 1 and run 3 will still
match. Don't re-record a single scene from a stale catalog state; always reset first.

## Capture these extra moments (for the README, not the video)
While `reset_demo.sh` / `run_demo.sh` output is still on screen, grab:
1. **A "catalog contrast" screenshot** — the DataHub search results page (or the 3 dataset cards
   side by side) showing `main.revenue` (🔴 28), `main.titanic` (🔴 25), and `main.bikeshare`
   (🟢 100) together. This one image tells the whole "it discriminates" story at a glance — great
   for the top of the README.
2. **A ~20-second "catch loop" GIF** — screen-record just Scene 2's terminal output (the verdict
   card printing, ending on `🔴 NOT TRUSTWORTHY · Trust Score 28/100`), no voice needed. Convert
   with `ffmpeg -i catch.mov -vf "fps=12,scale=800:-1" catch.gif` or [gifski](https://gif.ski/).
   Drop it inline in the README right under the "Data sources" or "Positioning" section — GitHub
   auto-plays GIFs, so a scrolling judge sees the product working without clicking anything.

## Guardrails (same as everywhere else in this repo)
- Every number you say must come from the screen in front of you — don't round up, don't say
  "proves," say "checks" or "finds." The numbers in `SCRIPT.md` are exactly what `reset_demo.sh`
  reproduces; if what's on your screen doesn't match the script, stop and re-run the reset.
- No stock music, no copyrighted clips, no AI voice unless it's yours or clearly disclosed.
