#!/usr/bin/env python3
"""Reproducible scale benchmark: run the heaviest checks on 250k SYNTHETIC rows and report
timings + peak RSS. Makes the "scales to 250k rows" claim judge-verifiable (no private data).

    python scripts/bench_scale.py
"""
from __future__ import annotations

import resource
import sys
import time

import numpy as np

from trust_layer.checks.honest_metrics.calibration_bias import CalibrationBiasCheck
from trust_layer.checks.honest_metrics.target_leakage import TargetLeakageCheck
from trust_layer.checks.distribution_drift import DistributionDriftCheck

N = 250_000


def _peak_rss_mb() -> float:
    kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return kb / (1024 * 1024) if sys.platform == "darwin" else kb / 1024  # macOS bytes, Linux KB


def _time(label, fn) -> None:
    t = time.perf_counter()
    fn()
    print(f"  {label:22s} {time.perf_counter() - t:6.2f}s")


def main() -> int:
    rng = np.random.default_rng(0)
    print(f"Benchmarking on {N:,} synthetic rows...")

    # distribution drift: reference vs current numeric columns
    ref = rng.normal(size=N)
    cur = rng.normal(0.1, 1.0, size=N)
    _time("distribution_drift", lambda: DistributionDriftCheck().run(baseline=list(ref), current=list(cur)))

    # calibration: 250k predicted probs vs outcomes
    p = rng.uniform(0.05, 0.95, size=N)
    y = (rng.random(N) < p).astype(int)
    _time("calibration", lambda: CalibrationBiasCheck().run(list(p), list(y)))

    # target leakage: a few features vs label (rank-AUC per feature)
    feats = {f"f{i}": list(rng.normal(size=N)) for i in range(3)}
    _time("target_leakage", lambda: TargetLeakageCheck().run(feats, list(y)))

    print(f"  peak RSS               {_peak_rss_mb():6.0f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
