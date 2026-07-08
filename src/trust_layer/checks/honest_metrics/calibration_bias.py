"""Auditor check: calibration / favorite-longshot bias.

A model whose probabilities are systematically off will still show a 'good' accuracy or
ROI on the slice it was tuned to. This check bins predicted probabilities and compares
each bin's predicted rate to the realized hit rate — the classic favorite-longshot
signature (longshots over-bet, favorites under-bet) that a single ROI number hides.

Reports an expected-calibration-error style gap + a directional bias flag. Pure stats,
distilled from our betting pipelines where multiplicative de-vig inflated longshots.
"""
from __future__ import annotations

from typing import Sequence

from ..base import Check, Finding, Severity


class CalibrationBiasCheck(Check):
    id = "calibration_bias"

    def run(
        self,
        predicted: Sequence[float],
        outcomes: Sequence[int],
        *,
        n_bins: int = 5,
        ece_warn: float = 0.03,
        ece_fail: float = 0.06,
    ) -> Finding:
        n = len(predicted)
        if n < 50 or n != len(outcomes):
            return Finding(self.id, Severity.OK, "insufficient data to judge calibration")

        # equal-width bins over [0,1]
        bins: list[list[tuple[float, int]]] = [[] for _ in range(n_bins)]
        for p, y in zip(predicted, outcomes):
            idx = min(int(p * n_bins), n_bins - 1)
            bins[idx].append((p, y))

        ece = 0.0
        rows = []
        low_over = high_under = 0
        for b, bucket in enumerate(bins):
            if not bucket:
                continue
            pred = sum(p for p, _ in bucket) / len(bucket)
            emp = sum(y for _, y in bucket) / len(bucket)
            ece += (len(bucket) / n) * abs(pred - emp)
            rows.append(f"[{b/n_bins:.1f}-{(b+1)/n_bins:.1f}] pred={pred:.2f} emp={emp:.2f} (n={len(bucket)})")
            # favorite-longshot signature: low bins realize MORE than predicted (longshots
            # over-priced) and/or high bins realize LESS (favorites under-priced)
            if b < n_bins / 2 and emp > pred + 0.02:
                low_over += 1
            if b >= n_bins / 2 and emp < pred - 0.02:
                high_under += 1

        detail = "; ".join(rows)
        if ece >= ece_fail:
            sev = Severity.FAIL
        elif ece >= ece_warn:
            sev = Severity.WARN
        else:
            return Finding(self.id, Severity.OK, f"well calibrated (ECE={ece:.3f})",
                           metrics={"ece": ece})

        bias = ""
        if low_over and high_under:
            bias = " — favorite-longshot bias: longshots over-priced AND favorites under-priced"
        elif low_over:
            bias = " — longshots systematically over-priced"
        elif high_under:
            bias = " — favorites systematically under-priced"
        return Finding(
            self.id, sev,
            f"CALIBRATION OFF (ECE={ece:.3f}){bias}",
            detail=detail,
            metrics={"ece": ece, "low_over_bins": low_over, "high_under_bins": high_under},
            suggested_tags=["audit-warn" if sev is Severity.WARN else "audit-failed"],
        )
