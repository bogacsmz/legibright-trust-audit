"""Renders the verdict card — the artifact judges see in the demo."""
from __future__ import annotations

from .agent import AuditReport
from .checks.base import Severity, Verdict

_ICON = {Severity.OK: "✅", Severity.WARN: "⚠️", Severity.FAIL: "❌"}
_VERDICT_ICON = {
    Verdict.TRUSTWORTHY: "🟢 TRUSTWORTHY",
    Verdict.INCONCLUSIVE: "🟡 INCONCLUSIVE",
    Verdict.NOT_TRUSTWORTHY: "🔴 NOT TRUSTWORTHY",
}


def render_card(report: AuditReport) -> str:
    lines = [
        "┌─────────────────────────────────────────────────────────────",
        f"│  TRUST LAYER AUDIT — {_VERDICT_ICON[report.verdict]}",
        f"│  target: {report.target}",
        "├─────────────────────────────────────────────────────────────",
    ]
    for f in report.findings:
        lines.append(f"│  {_ICON[f.severity]} [{f.check}] {f.headline}")
        if f.detail:
            lines.append(f"│      {f.detail}")
    lines.append("└─────────────────────────────────────────────────────────────")
    return "\n".join(lines)
