"""Sentinel check: statistical freshness / silent-staleness detection.

Why this is NOT what DataHub already ships: DataHub's out-of-box freshness assertions
check "did the table get written recently". They CANNOT catch a feed that keeps
updating rows on schedule but whose *values have frozen* — the exact failure mode we
hit in production (a betting odds feed that kept its heartbeat but stopped moving).

This check looks at value dynamics, not just write timestamps: if a column that should
vary across snapshots has gone flat (near-zero dispersion over the recent window while
historically it moved), that's silent staleness.
"""
from __future__ import annotations

import statistics
from typing import Sequence

from .base import Check, Finding, Severity


class FreshnessCheck(Check):
    id = "freshness"

    def run(
        self,
        recent_values: Sequence[float],
        historical_stdev: float,
        *,
        column: str = "value",
        flat_ratio_threshold: float = 0.05,
    ) -> Finding:
        """
        recent_values     : the column's values over the recent snapshot window
        historical_stdev   : that column's typical stdev in healthy periods
        Flags FAIL if recent dispersion collapsed to <5% of historical.
        """
        n = len(recent_values)
        if n < 3 or historical_stdev <= 0:
            return Finding(self.id, Severity.OK, f"{column}: insufficient data to judge freshness")

        recent_stdev = statistics.pstdev(recent_values)
        ratio = recent_stdev / historical_stdev
        if ratio < flat_ratio_threshold:
            return Finding(
                self.id,
                Severity.FAIL,
                f"{column} is SILENTLY STALE — values frozen while feed still updates",
                detail=(
                    f"recent σ={recent_stdev:.4f} is {ratio:.1%} of historical σ={historical_stdev:.4f} "
                    f"over the last {n} snapshots (threshold {flat_ratio_threshold:.0%})."
                ),
                metrics={"recent_stdev": recent_stdev, "hist_stdev": historical_stdev, "ratio": ratio},
                suggested_tags=["silently-stale"],
                suggested_incident=True,
            )
        sev = Severity.WARN if ratio < 3 * flat_ratio_threshold else Severity.OK
        return Finding(
            self.id, sev, f"{column} freshness ok (σ ratio {ratio:.1%})",
            metrics={"ratio": ratio},
        )
