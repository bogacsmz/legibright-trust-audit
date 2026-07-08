"""Sentinel check: distribution drift (PSI + KS) against a baseline.

EXTEND, not rewrite: DataHub's profiler gives you a column's distribution *right now*.
It does not tell you whether that distribution has SHIFTED away from a healthy baseline —
the thing that silently degrades a model in production. This check consumes two profiles
(baseline vs current — either from DataHub's profile history or computed from source) and
adds the drift verdict on top:

  * PSI (Population Stability Index) — the industry-standard drift score.
      < 0.10 stable · 0.10-0.25 moderate (WARN) · > 0.25 significant shift (FAIL).
  * KS (Kolmogorov-Smirnov two-sample) — complementary continuous-distribution test.
"""
from __future__ import annotations

import math
from typing import Sequence

from .base import Check, Finding, Severity


class DistributionDriftCheck(Check):
    id = "distribution_drift"

    def run(
        self,
        baseline: Sequence[float],
        current: Sequence[float],
        *,
        column: str = "value",
        n_bins: int = 10,
        psi_warn: float = 0.10,
        psi_fail: float = 0.25,
    ) -> Finding:
        if len(baseline) < 20 or len(current) < 20:
            return Finding(self.id, Severity.OK, f"{column}: insufficient data to judge drift")

        psi = _psi(baseline, current, n_bins)
        ks, ks_p = _ks_2samp(baseline, current)
        detail = f"PSI={psi:.3f}, KS={ks:.3f} (p={ks_p:.3g})"

        if psi >= psi_fail:
            return Finding(
                self.id, Severity.FAIL,
                f"{column} DISTRIBUTION SHIFTED — model likely degrading",
                detail=detail + f" — PSI over {psi_fail} significant-shift threshold.",
                metrics={"psi": psi, "ks": ks, "ks_p": ks_p},
                suggested_tags=["distribution-drift"],
                suggested_incident=True,
            )
        if psi >= psi_warn:
            return Finding(
                self.id, Severity.WARN, f"{column} moderate distribution drift",
                detail=detail, metrics={"psi": psi, "ks": ks, "ks_p": ks_p},
                suggested_tags=["distribution-drift"],
            )
        return Finding(self.id, Severity.OK, f"{column} distribution stable ({detail})",
                       metrics={"psi": psi, "ks": ks, "ks_p": ks_p})


def _psi(baseline: Sequence[float], current: Sequence[float], n_bins: int) -> float:
    """PSI using quantile bins of the baseline; epsilon-guarded."""
    lo, hi = min(baseline), max(baseline)
    if hi <= lo:
        return 0.0
    edges = [lo + (hi - lo) * i / n_bins for i in range(n_bins + 1)]
    edges[0], edges[-1] = -math.inf, math.inf

    def dist(xs):
        counts = [0] * n_bins
        for x in xs:
            for b in range(n_bins):
                if edges[b] <= x < edges[b + 1]:
                    counts[b] += 1
                    break
        n = len(xs)
        return [c / n for c in counts]

    base_d, curr_d = dist(baseline), dist(current)
    eps = 1e-4
    return sum((c - b) * math.log((c + eps) / (b + eps)) for b, c in zip(base_d, curr_d))


def _ks_2samp(baseline: Sequence[float], current: Sequence[float]) -> tuple[float, float]:
    try:
        from scipy.stats import ks_2samp

        r = ks_2samp(baseline, current)
        return float(r.statistic), float(r.pvalue)
    except Exception:
        # tiny fallback: empirical-CDF sup distance, no p-value
        allv = sorted(set(baseline) | set(current))
        b, c = sorted(baseline), sorted(current)

        def cdf(s, x):
            import bisect

            return bisect.bisect_right(s, x) / len(s)

        d = max(abs(cdf(b, x) - cdf(c, x)) for x in allv)
        return d, float("nan")
