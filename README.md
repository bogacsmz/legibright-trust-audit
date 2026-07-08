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

The supporting cast: a **Sentinel** that *extends* DataHub's freshness (it consumes DataHub's
profiling + write-time status and adds value-dynamics to catch a feed that's silently frozen),
then walks lineage to tag contaminated downstreams. Sentinel guards the *source*; the Auditor
judges the *metric* built on it.

## Why this isn't just another AI+MCP agent
The moat is domain honesty. This exact protocol is distilled from two production betting-model
pipelines — **250k+ rows of real odds+results** — where it honestly **killed 10+ "profitable-
looking" strategies**. The demo runs on that real data: the Auditor catches a fake +40% ROI edge
live, and you watch the AUDIT FAILED verdict appear in the DataHub UI.

## Contribute back to the graph (verified live)
On a verdict the agent emits, against live GMS:
- a **CUSTOM/EXTERNAL Assertion** + run result (SUCCESS/FAILURE) → DataHub's Data-Quality tab,
- an **ACTIVE Incident** with the failure detail → the asset's Incidents tab,
- **Tags** (`audit-failed`, `contaminated-upstream`) → fast visible signal.

`src/trust_layer/writeback.py` is verified end-to-end (write → read-back) on DataHub 1.6.

## Quickstart
```bash
pip install -e .
bash scripts/quickstart_up.sh                       # local DataHub :9002 / :8080
IDDAA_DB=/path/iddaa_snap.db datahub ingest -c ingest/recipes/iddaa.yml
python scripts/milestone1.py                         # read a dataset's health end-to-end
trust-layer selftest                                 # statistical core, no DataHub needed
python scripts/demo_writeback.py                     # emit a live verdict → see it in the UI
```
MCP wiring for judges (drive it from Claude/Cursor): `scripts/mcp_config.json`.

## Layout
- `src/trust_layer/checks/honest_metrics/` — **the Auditor** (registry-packaged for OSS reuse)
- `src/trust_layer/checks/freshness.py` — the Sentinel (extends DataHub, supporting)
- `src/trust_layer/writeback.py` — Assertion + Incident + Tag emission (live-verified)
- `src/trust_layer/agent.py` — orchestration + lineage propagation
- `ingest/`, `demo/scenario.md`, `docs/PLAN.md`, `docs/OSS_CONTRIBUTION.md`

## Status
M0 scaffold ✅ · M1 live read ✅ · M2 write-back ✅ (Assertion+Incident+Tag land in GMS).
Next: demo seed + honest-metrics run on real data. See `docs/PLAN.md`.
