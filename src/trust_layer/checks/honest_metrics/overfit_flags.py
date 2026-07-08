"""Auditor check: overfit red flags on a reported metric.

Cheap, high-signal heuristics that catch the 'too good to be true' backtest:
  - implausibly high ROI (>20% flat is almost always leakage/overfit in real markets),
  - in-sample vs out-of-sample gap (train ROI >> holdout ROI),
  - multiple-testing luck (N candidate cells scanned → expected false positives at z>=2).

Distilled from the walk-forward discipline in our betting pipelines.
"""
from __future__ import annotations

from ..base import Check, Finding, Severity


class OverfitFlagsCheck(Check):
    id = "overfit_flags"

    def run(
        self,
        *,
        roi_in_sample: float,
        roi_holdout: float | None = None,
        n_cells_scanned: int = 1,
        roi_alarm: float = 0.20,
    ) -> Finding:
        flags: list[str] = []
        if roi_in_sample > roi_alarm:
            flags.append(f"in-sample ROI {roi_in_sample:.0%} > {roi_alarm:.0%} alarm")
        if roi_holdout is not None and (roi_in_sample - roi_holdout) > 0.10:
            flags.append(
                f"train→holdout drop {roi_in_sample:.0%}→{roi_holdout:.0%} (overfit fingerprint)"
            )
        if n_cells_scanned > 1:
            # ~2.3% of cells clear z>=2 by chance (one-sided); flag if a 'win' among many.
            expected_false = n_cells_scanned * 0.023
            if expected_false >= 1:
                flags.append(
                    f"{n_cells_scanned} cells scanned → ~{expected_false:.1f} expected false z≥2 winners"
                )

        if flags:
            sev = Severity.FAIL if (roi_holdout is not None and roi_holdout <= 0) else Severity.WARN
            return Finding(
                self.id, sev, "OVERFIT RED FLAGS present", detail="; ".join(flags),
                metrics={"roi_in_sample": roi_in_sample, "roi_holdout": roi_holdout,
                         "n_cells": n_cells_scanned},
                suggested_tags=["audit-warn"] if sev is Severity.WARN else ["audit-failed"],
            )
        return Finding(self.id, Severity.OK, "no overfit red flags")
