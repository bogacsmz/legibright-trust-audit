#!/usr/bin/env python3
"""GENERALITY PROOF — the Auditor is domain-agnostic (not a betting gadget).

Runs the SAME honest-metrics checks on two well-known, NON-betting public datasets and
shows it gives the RIGHT verdict on each:

  1. UCI Bike Sharing (731 daily records, 2011-2012) — an HONEST walk-forward forecast:
     train on earlier days, test on later. Real Ridge model. → should PASS (TRUSTWORTHY):
     no temporal leakage, small in-sample→holdout gap. Proves NO FALSE ALARM.

  2. Kaggle Titanic (891 rows) — a DELIBERATELY OVERFIT model (unpruned decision tree)
     + a RANDOM train/test split injected onto a synthetic time index (leakage).
     → should FAIL (NOT TRUSTWORTHY): overfit gap + temporal leakage + miscalibration.

Real sklearn models, real numbers. Then writes each verdict back to DataHub and prints
the UI links. This is the proof the tool generalizes beyond our betting data.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import accuracy_score, r2_score
from sklearn.tree import DecisionTreeClassifier

from trust_layer.agent import AuditReport, TrustLayerAgent
from trust_layer.checks.honest_metrics.calibration_bias import CalibrationBiasCheck
from trust_layer.checks.honest_metrics.overfit_flags import OverfitFlagsCheck
from trust_layer.checks.honest_metrics.temporal_leakage import TemporalLeakageCheck
from trust_layer.config import CONFIG
from trust_layer.report import render_card

UI = "http://localhost:9002"
DS_BIKE = "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.bikeshare,PROD)"
DS_TITANIC = "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.titanic,PROD)"


def audit_bikeshare(df: pd.DataFrame) -> AuditReport:
    """Honest walk-forward forecast → should be TRUSTWORTHY."""
    df = df.sort_values("dteday").reset_index(drop=True)
    ts = pd.to_datetime(df["dteday"]).astype("int64") // 10**9
    feats = ["season", "yr", "mnth", "holiday", "weekday", "workingday",
             "weathersit", "temp", "atemp", "hum", "windspeed"]
    X, y = df[feats].values, df["cnt"].values
    cut = int(len(df) * 0.75)                       # time-ordered split (no shuffle)
    m = Ridge(alpha=1.0).fit(X[:cut], y[:cut])
    r2_in = r2_score(y[:cut], m.predict(X[:cut]))
    r2_out = r2_score(y[cut:], m.predict(X[cut:]))
    findings = [
        TemporalLeakageCheck().run(train_ts=list(ts[:cut]), test_ts=list(ts[cut:])),
        OverfitFlagsCheck().run(in_sample=r2_in, holdout=r2_out, metric="R²"),
    ]
    print(f"   [bikeshare] honest walk-forward: R²_in={r2_in:.2f}  R²_holdout={r2_out:.2f}")
    r = AuditReport(target=DS_BIKE, findings=findings)
    r.compute_verdict()
    return r


def audit_titanic(df: pd.DataFrame) -> AuditReport:
    """Overfit tree + injected random split → should be NOT TRUSTWORTHY."""
    df = df.copy()
    df["Age"] = df["Age"].fillna(df["Age"].median())
    df["Sex"] = (df["Sex"] == "male").astype(int)
    df["Embarked"] = df["Embarked"].fillna("S").map({"S": 0, "C": 1, "Q": 2})
    feats = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]
    X, y = df[feats].values, df["Survived"].values

    # synthetic time index = PassengerId order; a RANDOM split leaks future into train
    rng = np.random.default_rng(0)
    idx = np.arange(len(df))
    ts = idx.astype(float)                           # pseudo-time
    shuffled = rng.permutation(idx)                  # <- random split (the mistake)
    cut = int(len(df) * 0.7)
    tr, te = shuffled[:cut], shuffled[cut:]

    tree = DecisionTreeClassifier(max_depth=None, random_state=0).fit(X[tr], y[tr])  # overfit
    acc_in = accuracy_score(y[tr], tree.predict(X[tr]))
    acc_out = accuracy_score(y[te], tree.predict(X[te]))
    proba = tree.predict_proba(X[te])[:, 1]
    findings = [
        TemporalLeakageCheck().run(train_ts=list(ts[tr]), test_ts=list(ts[te])),
        OverfitFlagsCheck().run(in_sample=acc_in, holdout=acc_out, metric="accuracy"),
        CalibrationBiasCheck().run(predicted=list(proba), outcomes=list(y[te])),
    ]
    print(f"   [titanic] overfit tree + random split: acc_in={acc_in:.2f}  acc_holdout={acc_out:.2f}")
    r = AuditReport(target=DS_TITANIC, findings=findings)
    r.compute_verdict()
    return r


def main() -> int:
    bike = pd.read_csv("data/bike_day.csv")
    titanic = pd.read_csv("data/titanic.csv")

    print("=== CLEAN dataset: UCI Bike Sharing (honest walk-forward) ===")
    r_bike = audit_bikeshare(bike)
    print(render_card(r_bike))
    print("\n=== BROKEN dataset: Kaggle Titanic (overfit tree + random split) ===")
    r_titanic = audit_titanic(titanic)
    print(render_card(r_titanic))

    # write verdicts back to DataHub if it's up
    try:
        CONFIG.require_gms()
        from trust_layer.datahub_client import DataHubClient

        agent = TrustLayerAgent(client=DataHubClient(), write_back=True)
        for label, report, urn in (("bikeshare", r_bike, DS_BIKE), ("titanic", r_titanic, DS_TITANIC)):
            written = agent._write_back(urn, report)
            print(f"\n[{label}] wrote {len(written)} graph artifacts → {UI}/dataset/{urn}")
    except Exception as e:
        print(f"\n[write-back skipped: {e}]")

    ok = (r_bike.verdict.value == "TRUSTWORTHY" and r_titanic.verdict.value == "NOT_TRUSTWORTHY")
    print(f"\n{'✅ GENERALITY PROVEN' if ok else '❌ unexpected verdicts'}: "
          f"bike={r_bike.verdict.value}, titanic={r_titanic.verdict.value}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
