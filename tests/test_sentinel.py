"""Unit tests for the Sentinel data-health checks (drift / null-spike / schema-drift)."""
import random

from trust_layer.checks.base import Severity
from trust_layer.checks.distribution_drift import DistributionDriftCheck
from trust_layer.checks.null_spike import NullSpikeCheck
from trust_layer.checks.schema_drift import SchemaDriftCheck


def _gauss(mu, n, seed):
    r = random.Random(seed)
    return [r.gauss(mu, 1) for _ in range(n)]


def test_drift_stable_passes():
    f = DistributionDriftCheck().run(_gauss(0, 400, 1), _gauss(0, 400, 2))
    assert f.severity is Severity.OK


def test_drift_shift_fails():
    f = DistributionDriftCheck().run(_gauss(0, 400, 1), _gauss(1.5, 400, 3))
    assert f.severity is Severity.FAIL and f.metrics["psi"] > 0.25


def test_null_spike_fails():
    f = NullSpikeCheck().run(baseline_null_rate=0.02, current_null_rate=0.35, current_n=1000)
    assert f.severity is Severity.FAIL


def test_null_stable_ok():
    f = NullSpikeCheck().run(baseline_null_rate=0.02, current_null_rate=0.03, current_n=1000)
    assert f.severity is Severity.OK


def test_schema_added_column_ok():
    f = SchemaDriftCheck().run({"a": "INT"}, {"a": "integer", "b": "TEXT"})
    assert f.severity is Severity.OK


def test_schema_drop_fails():
    f = SchemaDriftCheck().run({"a": "INT", "b": "FLOAT"}, {"a": "INT"})
    assert f.severity is Severity.FAIL


def test_schema_retype_fails():
    f = SchemaDriftCheck().run({"a": "INT"}, {"a": "VARCHAR"})
    assert f.severity is Severity.FAIL


def test_type_normalization_no_false_drift():
    # INT vs integer, FLOAT vs double must NOT be flagged
    f = SchemaDriftCheck().run({"a": "INT", "b": "FLOAT"}, {"a": "integer", "b": "double"})
    assert f.severity is Severity.OK
