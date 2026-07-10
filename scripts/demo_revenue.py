#!/usr/bin/env python3
"""DEMO (hero) — Legibright audits a revenue-forecast model, writes the verdict to DataHub.

Target: `main.revenue` — daily e-commerce revenue aggregated from UCI Online Retail II
(real invoices, 2009-2011, CC BY 4.0; built by `scripts/fetch_data.py`). We audit a model
built the STANDARD naive way — the exact mistake most first drafts make, not a strawman:

  * a default `DecisionTreeRegressor()` (unconstrained → it memorizes), trained with
  * sklearn's DEFAULT `train_test_split(shuffle=True)` — a RANDOM split on a time series,
    so training rows are dated AFTER the test window: the model trains on the future.

Every number is MEASURED from that real model on real data (nothing reconstructed):
  * temporal leakage — from the split's actual timestamps
  * overfit flags     — from the model's actual in-sample vs holdout R²

It then emits Assertion + Incident + Tag + Trust Score (+ a deprecation proposal) into GMS.

Prereqs: quickstart up, `python scripts/fetch_data.py`, `pip install -e '.[dev]'`.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor

from trust_layer.agent import AuditReport, TrustLayerAgent
from trust_layer.checks.base import Verdict
from trust_layer.checks.honest_metrics.overfit_flags import OverfitFlagsCheck
from trust_layer.checks.honest_metrics.temporal_leakage import TemporalLeakageCheck
from trust_layer.config import CONFIG
from trust_layer.report import render_card

DATASET = "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.revenue,PROD)"
UI = "http://localhost:9002"
REVENUE_DB = Path(__file__).resolve().parent.parent / "data" / "revenue.db"


def main() -> int:
    CONFIG.require_gms()
    from trust_layer.datahub_client import DataHubClient

    con = sqlite3.connect(REVENUE_DB)
    df = pd.read_sql("SELECT day, revenue FROM revenue ORDER BY day", con)
    con.close()

    d = pd.to_datetime(df["day"])
    X = pd.DataFrame({
        "year": d.dt.year, "month": d.dt.month, "day": d.dt.day,
        "dow": d.dt.dayofweek, "doy": d.dt.dayofyear,
        "weekend": (d.dt.dayofweek >= 5).astype(int),
    }).values
    y = df["revenue"].values
    ts = (d.astype("int64") // 10**9).values

    # THE common mistake, verbatim: sklearn's DEFAULT split shuffles rows (shuffle=True),
    # so a time series is cut at random and the future leaks into training. The default,
    # unconstrained tree then memorizes. This is the standard naive pipeline, not a strawman.
    Xtr, Xte, ytr, yte, tr_ts, te_ts = train_test_split(X, y, ts, test_size=0.3, random_state=42)
    model = DecisionTreeRegressor(random_state=0).fit(Xtr, ytr)      # default params, no tuning
    r2_in = r2_score(ytr, model.predict(Xtr))
    r2_out = r2_score(yte, model.predict(Xte))
    print(f"[demo] audited claim: 'daily-revenue forecaster, R² {r2_in:.2f}' on {len(df)} days "
          f"of real e-commerce revenue (UCI Online Retail II)\n")

    findings = [
        TemporalLeakageCheck().run(train_ts=list(map(float, tr_ts)), test_ts=list(map(float, te_ts))),
        OverfitFlagsCheck().run(in_sample=r2_in, holdout=r2_out, metric="R²"),
    ]
    report = AuditReport(target=f"{DATASET} :: revenue_forecast", findings=findings)
    report.compute_verdict()
    print(render_card(report))
    print(f"   ↳ {findings[0].detail}")           # surface the measured temporal leak %

    print("\n[demo] writing verdict back into DataHub graph...")
    agent = TrustLayerAgent(client=DataHubClient(), write_back=True, propose_deprecation=True)
    written = agent._write_back(DATASET, report)
    n_assert = sum("assertion" in u for u in written)
    n_incident = sum("incident" in u for u in written)
    n_tag = sum("tag" in u for u in written)
    print(f"   ✓ {n_assert} assertions → Data-Quality tab (SUCCESS/FAILURE, with history)")
    print(f"   ✓ {n_incident} incident → Incidents tab (ACTIVE, carries the failure detail)")
    print(f"   ✓ {n_tag} tags → audit-failed, temporal-leakage")
    print(f"   ✓ Trust Score {report.trust_score()}/100 → typed numeric structured property")
    if report.verdict is Verdict.NOT_TRUSTWORTHY:
        print("   ✓ deprecation PROPOSED → deprecated=false (agent proposes, a human approves)")
    print(f"\n[demo] see it in DataHub → Assertions + Incidents tabs:\n   {UI}/dataset/{DATASET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
