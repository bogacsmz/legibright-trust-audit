# Demo Scenario — the ≤3-minute video script

**Title:** "The agent that catches the backtest that's lying to you."

## Setup (pre-recorded state)
- Local DataHub with 3 ingested datasets from real betting pipelines:
  `raw.iddaa_snaps` → `analytics.edge_candidates` → `dashboard.roi_metric` (lineage stamped).
- `dashboard.roi_metric` proudly shows **+40% ROI**.

## Beat 1 — the silent failure (0:00–0:45)
- We freeze the `raw.iddaa_snaps` odds feed: rows keep arriving on schedule (heartbeat OK),
  but values stop moving. DataHub's built-in freshness assertion stays GREEN — it only
  checks "was the table written". **This is the gap.**
- Run the agent. Sentinel's statistical freshness check FAILS:
  "odds column silently stale — σ collapsed to 3% of historical."
- Agent writes back: `silently-stale` tag + Incident on `raw.iddaa_snaps`.

## Beat 2 — root-cause propagation (0:45–1:30)
- Agent walks lineage: `raw.iddaa_snaps` feeds `analytics.edge_candidates` feeds the ROI metric.
- It tags both downstream assets `contaminated-upstream` — "the next person inherits this."

## Beat 3 — the moat: honest-metrics audit (1:30–2:30)
- Now the star turn. The agent audits the +40% ROI claim itself.
- Auditor finds the training/test split via lineage + query history, runs temporal-leakage:
  "31% of training rows are dated after the test cutoff — random split masquerading as
  walk-forward." Plus overfit flags: "in-sample 40% vs holdout −12%; 677 cells scanned."
- Verdict card: **🔴 NOT TRUSTWORTHY**. Agent stamps `audit-failed` + `audit.verdict` on the metric.

## Beat 4 — the honest close (2:30–3:00)
- Feed a genuinely-clean metric → **🟡 INCONCLUSIVE**: "real but thin: holdout z+2.4,
  after-tax +1.8%, high limit risk." Not a fake green — a calibrated verdict.
- Line: "Everyone's agent shows you a number. Ours tells you whether to believe it —
  and writes that judgment back into DataHub so your whole team inherits it."

## Why judges care (say it once, on screen)
DataHub ships freshness + assertions. It does NOT ship statistical honesty:
calibration, temporal-leakage, multiple-testing. That's the layer we add on top —
distilled from 250k+ rows where this protocol killed 10+ real 'winning' strategies.
