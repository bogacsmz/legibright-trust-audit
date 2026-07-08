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
