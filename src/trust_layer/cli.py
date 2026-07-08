"""CLI entrypoint: `trust-layer ...`

Subcommands (fleshed out during build week):
  hello      — milestone 1: read one dataset's health end-to-end
  audit      — run the full Sentinel+Auditor pass on a dataset/metric
  demo       — run the scripted 'frozen feed → contaminated metric' scenario
"""
from __future__ import annotations

import typer

from .agent import AuditReport, TrustLayerAgent
from .checks.freshness import FreshnessCheck
from .checks.honest_metrics.overfit_flags import OverfitFlagsCheck
from .checks.honest_metrics.temporal_leakage import TemporalLeakageCheck
from .report import render_card

app = typer.Typer(help="Statistical Trust Layer agent for DataHub.", no_args_is_help=True)


@app.command()
def selftest() -> None:
    """Run the statistical core on synthetic data — proves checks work with no DataHub."""
    findings = [
        FreshnessCheck().run(recent_values=[2.0, 2.0, 2.0, 2.0], historical_stdev=0.8, column="odds"),
        TemporalLeakageCheck().run(train_ts=[1, 2, 3, 9, 10], test_ts=[4, 5, 6]),
        OverfitFlagsCheck().run(roi_in_sample=0.42, roi_holdout=-0.12, n_cells_scanned=677),
    ]
    report = AuditReport(target="synthetic://demo-metric", findings=findings)
    report.compute_verdict()
    print(render_card(report))


@app.command()
def hello() -> None:
    """Milestone 1 placeholder — see scripts/milestone1.py for the live-DataHub version."""
    typer.echo("Run: python scripts/milestone1.py  (requires DataHub quickstart up).")


if __name__ == "__main__":
    app()
