"""Auditor check: calibration / miscalibration — sample-size aware.

A single ROI/accuracy number hides whether the model's *probabilities* are honest. But a
naive fixed ECE threshold is itself dishonest: empirical ECE is positively biased at small n,
so a fixed cutoff cries wolf on perfectly-calibrated models when the holdout is small.

So we use the **Hosmer-Lemeshow goodness-of-fit test** (chi-square p-value over quantile bins),
which accounts for n, and only flag when the deviation is BOTH statistically significant AND
materially large (ECE). Quantile bins (not equal-width) avoid the within-bin cancellation that
lets 0.45-for-0 / 0.55-for-1 look "calibrated". Under ~50 rows we do NOT certify — we WARN.

Distilled from betting pipelines where multiplicative de-vig inflated longshots.
"""
from __future__ import annotations

from typing import Sequence

from ..base import Check, Finding, Severity

_MIN_N = 50


class CalibrationBiasCheck(Check):
    id = "calibration_bias"

    def run(
        self,
        predicted: Sequence[float],
        outcomes: Sequence[int],
        *,
        n_bins: int = 10,
        p_fail: float = 0.01,
        p_warn: float = 0.05,
        ece_material: float = 0.03,
    ) -> Finding:
        n = len(predicted)
        if n != len(outcomes):
            return Finding(self.id, Severity.OK, "calibration: mismatched inputs")
        if n < _MIN_N:
            # honest: too few rows to certify calibration either way (do NOT stamp OK)
            return Finding(self.id, Severity.WARN,
                           f"calibration NOT certified — only {n} rows (< {_MIN_N})",
                           suggested_tags=["audit-warn"])

        bins = _quantile_bins(list(zip(predicted, outcomes)), n_bins)
        hl, p, ece, rows = _hosmer_lemeshow(bins, n)
        detail = f"HL χ²={hl:.1f}, p={p:.3g}, ECE={ece:.3f} over {len(bins)} bins"

        if p < p_fail and ece >= ece_material:
            return Finding(self.id, Severity.FAIL,
                           f"CALIBRATION OFF (significant, p={p:.2g}, ECE={ece:.3f})",
                           detail=detail + " | " + "; ".join(rows),
                           metrics={"hl": hl, "p": p, "ece": ece},
                           suggested_tags=["audit-failed"])
        if p < p_warn and ece >= ece_material:
            return Finding(self.id, Severity.WARN, f"calibration suspect (p={p:.2g}, ECE={ece:.3f})",
                           detail=detail, metrics={"hl": hl, "p": p, "ece": ece},
                           suggested_tags=["audit-warn"])
        return Finding(self.id, Severity.OK, f"well calibrated ({detail})",
                       metrics={"hl": hl, "p": p, "ece": ece})


def _quantile_bins(pairs, n_bins):
    """Split rows into ~equal-count bins by predicted prob (stable, no empty bins)."""
    pairs = sorted(pairs, key=lambda x: x[0])
    n = len(pairs)
    k = max(2, min(n_bins, n // 5))     # keep >=5 rows/bin so HL is meaningful
    bins = []
    for b in range(k):
        lo, hi = b * n // k, (b + 1) * n // k
        chunk = pairs[lo:hi]
        if chunk:
            bins.append(chunk)
    return bins


def _hosmer_lemeshow(bins, n):
    hl = 0.0
    ece = 0.0
    rows = []
    for b, chunk in enumerate(bins):
        ng = len(chunk)
        pred = sum(p for p, _ in chunk) / ng
        obs = sum(y for _, y in chunk) / ng
        E = sum(p for p, _ in chunk)
        O = sum(y for _, y in chunk)
        ece += (ng / n) * abs(pred - obs)
        denom = E * (1 - E / ng) if 0 < E < ng else 0.0
        if denom > 0:
            hl += (O - E) ** 2 / denom
        rows.append(f"[b{b}] pred={pred:.2f} obs={obs:.2f} n={ng}")
    df = max(len(bins) - 2, 1)
    p = _chi2_sf(hl, df)
    return hl, p, ece, rows


def _chi2_sf(x, df):
    try:
        from scipy.stats import chi2

        return float(chi2.sf(x, df))
    except Exception:
        import math

        # crude fallback: Wilson-Hilferty normal approximation to chi-square upper tail
        if x <= 0:
            return 1.0
        t = ((x / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
        return 0.5 * math.erfc(t / math.sqrt(2))
