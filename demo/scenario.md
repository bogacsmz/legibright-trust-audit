# Demo — the ≤3-minute video flow

**Title:** *"The agent that tells you whether to trust a model."*
**One-liner (on screen, 0:00):** Before an ML/data team trusts a model, this agent audits
whether it actually works — or just fits stale data. Runs on 30k real matches, live.

Structure: **problem → live AUDIT FAILED → write-back visible in DataHub → the moat.**

## Beat 1 — the problem (0:00–0:30)
- DataHub open on `main.matches` (30,352 real football matches, Pinnacle closing odds).
- A "backtest_roi = +40%" claim sits on it. Looks great. Every generic AI agent would say ship it.
- Narration: DataHub ships freshness, profiling, incidents — but nothing tells you if this
  **number is honest**. That's the gap.

## Beat 2 — the Auditor runs, live AUDIT FAILED (0:30–1:30)
- `python scripts/demo_writeback.py`. The verdict card prints in real time:
  - ❌ **temporal leakage** — 20% of training rows dated after the test cutoff (random split
    wearing a walk-forward costume).
  - ❌ **overfit flags** — +40% in-sample vs −12% holdout; 677 cells scanned → ~16 false winners.
  - ✅ **calibration** — ECE 0.012. *(Say it out loud: the Auditor is calibrated itself — it
    PASSES what's genuinely fine, so a ❌ means something.)*
  - **🔴 NOT TRUSTWORTHY.**

## Beat 3 — write it back into the graph (1:30–2:15) — the "Use of DataHub" money shot
- Switch to the DataHub UI, refresh `main.matches`:
  - **Assertions tab:** three new CUSTOM/EXTERNAL assertions, `honest-metrics/*`, FAILURE.
  - **Incidents tab:** an ACTIVE incident "[trust-layer] temporal leakage" with the detail.
  - **Tags:** `audit-failed`, `temporal-leakage`.
- Narration: the verdict isn't a console print — it's now graph-native. The next engineer or
  agent that opens this asset **inherits the judgment**.

## Beat 4 — the moat + honest close (2:15–3:00)
- Why we can build this and a generic team can't: distilled from two production betting
  pipelines, 250k+ rows, where this exact protocol **killed 10+ "winning" strategies**.
- Show the Sentinel cameo: freeze a source feed → Sentinel catches silent staleness
  (values frozen while the write-heartbeat stays green) → tags downstream `contaminated`.
- Close: *"Everyone's agent shows you a number. Ours writes back whether to believe it —
  and it says NO when it should."*

## Notes for recording
- Pre-ingest both dbs; pre-open the UI tabs so the refresh is instant.
- Keep the Auditor the star; Sentinel is a 15-second cameo, not half the video.
- 3 takes (our discipline). Target 2:45 to leave breathing room under the 3:00 cap.
