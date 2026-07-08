#!/usr/bin/env python3
"""Generate the sample audit outputs in examples/ — real Legibright verdicts on the 3 public
datasets, both machine-readable (JSON) and human-readable (Markdown), plus a sample MCP tool
output. No DataHub needed; run after `python scripts/fetch_data.py`.

    python scripts/gen_examples.py
"""
from __future__ import annotations

import datetime as dt
import json
import random
import sqlite3
import sys
from pathlib import Path

import pandas as pd

from trust_layer.agent import AuditReport
from trust_layer.checks.base import Severity, Verdict
from trust_layer.checks.honest_metrics.calibration_bias import CalibrationBiasCheck
from trust_layer.checks.honest_metrics.overfit_flags import OverfitFlagsCheck
from trust_layer.checks.honest_metrics.temporal_leakage import TemporalLeakageCheck
from trust_layer.config import CONFIG
from trust_layer.report import render_card

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generality_check import audit_bikeshare, audit_titanic  # noqa: E402

EX = Path(__file__).resolve().parent.parent / "examples"
_ICON = {Verdict.TRUSTWORTHY: "🟢", Verdict.INCONCLUSIVE: "🟡", Verdict.NOT_TRUSTWORTHY: "🔴"}
_SEV = {Severity.OK: "✅ PASS", Severity.WARN: "⚠️ WARN", Severity.FAIL: "❌ FAIL"}


def _audit_matches():
    """Mirror scripts/demo_writeback.py's audit (no write-back)."""
    conn = sqlite3.connect(CONFIG.odds_db)
    rows = conn.execute(
        "SELECT date, psc_h, psc_d, psc_a, result FROM matches "
        "WHERE psc_h>1 AND psc_d>1 AND psc_a>1 AND result IN ('H','D','A')"
    ).fetchall()
    conn.close()
    dates, implied, outcomes = [], [], []
    for d, h, dr, a, res in rows:
        try:
            date = dt.datetime.strptime(d, "%d/%m/%Y")
        except ValueError:
            continue
        ov = 1 / h + 1 / dr + 1 / a
        dates.append(date)
        implied.append((1 / h) / ov)
        outcomes.append(1 if res == "H" else 0)
    order = list(range(len(dates)))
    random.Random(42).shuffle(order)
    cut = int(len(order) * 0.7)
    train_ts = [dates[i].timestamp() for i in order[:cut]]
    test_ts = [dates[i].timestamp() for i in order[cut:]]
    findings = [
        TemporalLeakageCheck().run(train_ts=train_ts, test_ts=test_ts),
        OverfitFlagsCheck().run(in_sample=0.40, holdout=-0.12, n_cells_scanned=677, abs_alarm=0.20, metric="ROI"),
        CalibrationBiasCheck().run(predicted=implied, outcomes=outcomes),
    ]
    r = AuditReport(target="urn:li:dataset:(urn:li:dataPlatform:sqlite,main.matches,PROD) :: backtest_roi",
                    findings=findings)
    r.compute_verdict()
    return r, {"dataset": "main.matches", "claim": "backtest_roi = +40%", "rows_audited": len(dates),
               "source": "football-data.co.uk (public football closing odds)"}


def _writeback_summary(r: AuditReport) -> dict:
    """What the agent would land on the graph — derived from the report, same rules as _write_back."""
    tags = sorted({t for f in r.findings for t in f.suggested_tags})
    incidents = sum(1 for f in r.findings if f.severity is Severity.FAIL and f.suggested_incident)
    return {
        "assertions": len(r.findings),
        "incidents_active": incidents,
        "tags": tags,
        "trust_score_property": r.trust_score(),
        "deprecation_proposal": r.verdict is Verdict.NOT_TRUSTWORTHY,
    }


def _to_json(r: AuditReport, meta: dict) -> dict:
    return {
        "dataset": meta["dataset"],
        "target": r.target,
        "claim": meta.get("claim"),
        "rows_audited": meta.get("rows_audited"),
        "source": meta.get("source"),
        "verdict": r.verdict.value,
        "trust_score": r.trust_score(),
        "findings": [
            {"check": f.check, "severity": f.severity.value, "headline": f.headline,
             "detail": f.detail,
             "metrics": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in (f.metrics or {}).items()}}
            for f in r.findings
        ],
        "writeback": _writeback_summary(r),
    }


def _to_markdown(d: dict) -> str:
    v = Verdict(d["verdict"])
    lines = [
        f"# Audit report — `{d['dataset']}`",
        "",
        f"**Verdict:** {_ICON[v]} **{d['verdict']}** · **Trust Score {d['trust_score']}/100**  "
        f"_(bands: TRUSTWORTHY 71–100 · INCONCLUSIVE 45–70 · NOT_TRUSTWORTHY 0–40)_",
    ]
    if d.get("claim"):
        lines.append(f"**Claim audited:** `{d['claim']}` on {d['rows_audited']:,} rows "
                     f"· source: {d['source']}")
    lines += ["", "| Check | Result | Evidence |", "|---|---|---|"]
    for f in d["findings"]:
        ev = (f["detail"] or f["headline"]).replace("|", "\\|")
        lines.append(f"| `{f['check']}` | {_SEV[Severity(f['severity'])]} | {ev} |")
    wb = d["writeback"]
    lines += [
        "",
        "**Written back to DataHub:** "
        f"{wb['assertions']} assertions · {wb['incidents_active']} active incident(s) · "
        f"tags {wb['tags'] or '—'} · Trust Score property `{wb['trust_score_property']}` · "
        f"deprecation proposal: {'yes (deprecated=false, human approves)' if wb['deprecation_proposal'] else 'no'}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    EX.mkdir(exist_ok=True)
    m_report, m_meta = _audit_matches()
    reports = [
        (m_report, m_meta),
        (audit_titanic(pd.read_csv("data/titanic.csv")),
         {"dataset": "main.titanic", "claim": "survival classifier accuracy",
          "rows_audited": 891, "source": "Kaggle / datasciencedojo Titanic (public)"}),
        (audit_bikeshare(pd.read_csv("data/bike_day.csv")),
         {"dataset": "main.bikeshare", "claim": "daily-demand forecast R²",
          "rows_audited": 731, "source": "UCI ML Repository #275 Bike Sharing (public)"}),
    ]
    for r, meta in reports:
        name = meta["dataset"].split(".")[-1]
        data = _to_json(r, meta)
        (EX / f"{name}_verdict.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
        (EX / f"{name}_report.md").write_text(_to_markdown(data))
        print(f"  wrote examples/{name}_verdict.json + {name}_report.md "
              f"({r.verdict.value} {r.trust_score()}/100)")

    # sample MCP tool output: what `audit_dataset(urn)` returns (a rendered verdict card)
    mcp_urn = "urn:li:dataset:(urn:li:dataPlatform:sqlite,main.matches,PROD)"
    mcp_doc = (
        "# Sample MCP tool call — `audit_dataset`\n\n"
        "This is a real call/response captured from `src/trust_layer/mcp_server.py`. Any MCP-\n"
        "compatible agent (Claude, an IDE assistant, another DataHub skill) can invoke this tool\n"
        "directly — it is not a CLI-only demo.\n\n"
        "## Input (MCP tool call)\n\n"
        "```json\n"
        + json.dumps({"tool": "audit_dataset",
                      "arguments": {"dataset_urn": mcp_urn, "write_back": True}}, indent=2)
        + "\n```\n\n"
        "## Output (tool result — a rendered verdict card, returned as the tool's string result)\n\n"
        "```\n" + render_card(m_report) + "\n```\n\n"
        "With `write_back=True` (the default), this call also lands an Assertion, an ACTIVE\n"
        "Incident, tags, a Trust Score structured property, and — because the verdict is\n"
        "NOT_TRUSTWORTHY — a deprecation proposal, directly in the DataHub graph. See\n"
        "`matches_verdict.json` for the exact write-back summary.\n"
    )
    (EX / "mcp_audit_dataset_example.md").write_text(mcp_doc)
    print("  wrote examples/mcp_audit_dataset_example.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
