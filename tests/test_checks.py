"""Unit tests for the statistical core — runnable with zero DataHub."""
from trust_layer.checks.base import Severity, Verdict
from trust_layer.checks.freshness import FreshnessCheck
from trust_layer.checks.honest_metrics.overfit_flags import OverfitFlagsCheck
from trust_layer.checks.honest_metrics.temporal_leakage import TemporalLeakageCheck
from trust_layer.agent import AuditReport


def test_freshness_flags_frozen_feed():
    f = FreshnessCheck().run(recent_values=[2.0, 2.0, 2.0, 2.0], historical_stdev=0.8, column="odds")
    assert f.severity is Severity.FAIL
    assert "silently-stale" in f.suggested_tags


def test_freshness_ok_when_moving():
    f = FreshnessCheck().run(recent_values=[2.0, 2.6, 1.8, 2.3], historical_stdev=0.4, column="odds")
    assert f.severity is Severity.OK


def test_temporal_leakage_catches_random_split():
    f = TemporalLeakageCheck().run(train_ts=[1, 2, 3, 9, 10], test_ts=[4, 5, 6])
    assert f.severity is Severity.FAIL
    assert 0 < f.metrics["leak_ratio"] <= 1


def test_temporal_leakage_ok_on_clean_cut():
    f = TemporalLeakageCheck().run(train_ts=[1, 2, 3], test_ts=[4, 5, 6])
    assert f.severity is Severity.OK


def test_overfit_flags_fire_on_too_good():
    f = OverfitFlagsCheck().run(roi_in_sample=0.42, roi_holdout=-0.12, n_cells_scanned=677)
    assert f.severity is Severity.FAIL


def test_calibration_flags_longshot_bias():
    from trust_layer.checks.honest_metrics.calibration_bias import CalibrationBiasCheck
    # low predicted prob but high realized (longshots over-priced) + favorites under
    predicted = [0.1] * 60 + [0.9] * 60
    outcomes = [1] * 30 + [0] * 30 + [0] * 40 + [1] * 20  # low bin realizes .5, high bin .33
    f = CalibrationBiasCheck().run(predicted, outcomes, n_bins=5)
    assert f.severity is Severity.FAIL
    assert "bias" in f.headline.lower()


def test_calibration_ok_when_sharp():
    from trust_layer.checks.honest_metrics.calibration_bias import CalibrationBiasCheck
    import random
    random.seed(0)
    predicted, outcomes = [], []
    for _ in range(5000):  # enough to keep per-bin sampling noise below the ECE threshold
        p = random.random()
        predicted.append(p)
        outcomes.append(1 if random.random() < p else 0)
    f = CalibrationBiasCheck().run(predicted, outcomes, n_bins=5)
    assert f.severity is Severity.OK


def test_verdict_aggregation():
    report = AuditReport(
        target="x",
        findings=[TemporalLeakageCheck().run(train_ts=[1, 2, 9], test_ts=[4, 5])],
    )
    assert report.compute_verdict() is Verdict.NOT_TRUSTWORTHY
