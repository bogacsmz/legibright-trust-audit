"""Round-3 robustness: degenerate inputs must degrade to INCONCLUSIVE/WARN, never a
confident wrong verdict; split classifier must not hang on pathological SQL."""
import time

from trust_layer.agent import AuditReport
from trust_layer.checks.base import Severity, Verdict
from trust_layer.checks.honest_metrics.calibration_bias import CalibrationBiasCheck
from trust_layer.checks.null_spike import NullSpikeCheck
from trust_layer.split_inference import SplitKind, classify_sql, finding_from_queries


def test_empty_findings_is_inconclusive_not_green():
    # "no checks ran" must never read as TRUSTWORTHY
    assert AuditReport(target="x", findings=[]).compute_verdict() is Verdict.INCONCLUSIVE


def test_empty_query_history_warns():
    assert finding_from_queries([]).severity is Severity.WARN


def test_calibration_mismatched_inputs_warns_not_ok():
    assert CalibrationBiasCheck().run([0.1, 0.2, 0.3, 0.4, 0.5], [0, 1, 0, 1]).severity is Severity.WARN


def test_null_spike_zero_rows_does_not_fabricate_fail():
    f = NullSpikeCheck().run(baseline_null_rate=0.02, current_null_rate=1.0, current_n=0)
    assert f.severity is Severity.WARN   # not a z=1000 FAIL from no data


def test_classify_sql_join_chain_does_not_hang():
    sql = "SELECT * FROM a " + " ".join(f"JOIN t{i} ON a.id=t{i}.id" for i in range(40))
    t = time.time()
    kind = classify_sql(sql).kind
    assert time.time() - t < 2.0            # guarded, not super-linear
    assert kind in (SplitKind.UNKNOWN, SplitKind.RANDOM, SplitKind.TEMPORAL)


def test_classify_sql_garbage_is_graceful():
    for bad in ["", "not sql at all", "DROP TABLE x", "SÉLÉCT ünïcödé"]:
        assert classify_sql(bad).kind in (SplitKind.UNKNOWN, SplitKind.RANDOM)


def _calib_case(shift):
    """Large-n calibration: outcomes drawn from true p, predictions shifted by `shift`."""
    import numpy as np

    rng = np.random.default_rng(0)
    n = 12000
    p = rng.uniform(0.1, 0.9, n)
    y = (rng.random(n) < p).astype(int)
    pred = np.clip(p + shift, 0, 1)
    return CalibrationBiasCheck().run(list(pred), list(y))


def test_calibration_significant_but_immaterial_stays_ok():
    # the demo case: at n=12k a 0.02 shift is HL-significant yet ECE<0.03 → must NOT cry wolf
    f = _calib_case(0.02)
    assert f.severity is Severity.OK
    assert f.metrics["p"] < 0.05 and f.metrics["ece"] < 0.03   # significant yet immaterial


def test_calibration_material_miscalibration_fails():
    # a 0.12 shift is both significant AND material (ECE≥0.03) → must FAIL
    f = _calib_case(0.12)
    assert f.failed and f.metrics["ece"] >= 0.03


def test_calibration_degenerate_hard_predictions_not_green():
    # hard 0/1 predictions (overfit tree) that are badly calibrated make HL undefined (p=1);
    # that must NOT read "well calibrated" — the observed ECE is material → WARN, not OK.
    pred = [0.0] * 100 + [1.0] * 100
    y = [1] * 30 + [0] * 70 + [0] * 30 + [1] * 70   # 30% wrong in each hard-prediction group
    f = CalibrationBiasCheck().run(pred, y)
    assert f.severity is Severity.WARN
    assert f.metrics["ece"] >= 0.03 and f.metrics["hl_bins_used"] < 2


def test_calibration_partial_degenerate_not_green():
    # soft-honest on some rows, confidently-WRONG hard 0/1 on others: the hard bins drop out of
    # χ² (p looks fine) but their error still counts toward ECE. Must be WARN "not certifiable",
    # never a green OK — this is the partial-degenerate residual of the earlier full-degenerate fix.
    pred = [0.0] * 30 + [1.0] * 30 + [0.5] * 40
    y = [1] * 30 + [0] * 30 + [1, 0] * 20            # hard bins inverted; soft bin balanced
    f = CalibrationBiasCheck().run(pred, y)
    assert f.severity is Severity.WARN                # not OK
    assert f.metrics["ece"] >= 0.03
    assert f.metrics["hl_bins_used"] < 10             # some bins were dropped as degenerate
