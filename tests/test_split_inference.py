"""Unit tests for split-methodology inference from SQL (the auto-feed brain)."""
from trust_layer.checks.base import Severity
from trust_layer.split_inference import SplitKind, classify_sql, finding_from_queries


def test_temporal_predicate():
    assert classify_sql("SELECT * FROM m WHERE date < '2024-01-01'").kind is SplitKind.TEMPORAL


def test_random_function():
    assert classify_sql("SELECT * FROM m WHERE rand() < 0.7").kind is SplitKind.RANDOM


def test_order_by_random():
    assert classify_sql("SELECT * FROM m ORDER BY RANDOM() LIMIT 100").kind is SplitKind.RANDOM


def test_hash_mod_bucketing():
    assert classify_sql("SELECT * FROM m WHERE MOD(ABS(HASH(id)),10) < 7").kind is SplitKind.RANDOM


def test_tablesample():
    assert classify_sql("SELECT * FROM m TABLESAMPLE (70 PERCENT)").kind is SplitKind.RANDOM


def test_no_signal_is_unknown():
    assert classify_sql("SELECT * FROM m WHERE pclass = 1").kind is SplitKind.UNKNOWN


def test_finding_random_fails():
    f = finding_from_queries(["SELECT * FROM m WHERE rand() < 0.7"])
    assert f.severity is Severity.FAIL and f.suggested_incident


def test_finding_temporal_passes():
    f = finding_from_queries(["SELECT * FROM m WHERE date < '2024-01-01'"])
    assert f.severity is Severity.OK


def test_finding_unknown_warns():
    f = finding_from_queries(["SELECT * FROM m WHERE pclass = 1"])
    assert f.severity is Severity.WARN
