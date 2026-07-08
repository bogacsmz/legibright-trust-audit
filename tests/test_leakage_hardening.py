"""Tests for the round-2 hardening: feature leakage + split-inference dodges + overfit collapse."""
import random

from trust_layer.checks.base import Severity
from trust_layer.checks.honest_metrics.group_leakage import GroupLeakageCheck
from trust_layer.checks.honest_metrics.overfit_flags import OverfitFlagsCheck
from trust_layer.checks.honest_metrics.target_leakage import TargetLeakageCheck
from trust_layer.split_inference import SplitKind, classify_sql, finding_from_queries


# --- target / group leakage (were structurally invisible before) ---
def test_target_leakage_caught():
    y = [i % 2 for i in range(120)]
    feats = {"noise": [random.random() for _ in range(120)], "leak": [float(v) for v in y]}
    assert TargetLeakageCheck().run(feats, y).severity is Severity.FAIL


def test_target_leakage_clean_passes():
    random.seed(0)
    y = [random.randint(0, 1) for _ in range(120)]
    feats = {"a": [random.random() for _ in range(120)], "b": [random.random() for _ in range(120)]}
    assert TargetLeakageCheck().run(feats, y).severity is Severity.OK


def test_group_leakage_caught():
    assert GroupLeakageCheck().run([1, 2, 3, 4, 5], [3, 4, 5, 6, 7]).severity is Severity.FAIL


def test_group_leakage_clean_passes():
    assert GroupLeakageCheck().run([1, 2, 3], [4, 5, 6]).severity is Severity.OK


# --- split-inference dodges (were misclassified as TEMPORAL/UNKNOWN) ---
def test_cosmetic_date_does_not_mask_modulo_split():
    assert classify_sql("SELECT * FROM t WHERE created > '2000-01-01' AND (id % 10) < 7").kind is SplitKind.RANDOM


def test_md5_bucketing_is_random():
    assert classify_sql("SELECT * FROM t WHERE substr(md5(id),1,1) IN ('0','1')").kind is SplitKind.RANDOM


def test_ntile_is_random():
    assert classify_sql("SELECT * FROM t WHERE NTILE(10) OVER (ORDER BY id) <= 7").kind is SplitKind.RANDOM


def test_overlapping_temporal_ranges_fail():
    f = finding_from_queries([
        "SELECT * FROM t WHERE date < '2024-06-01'",
        "SELECT * FROM t WHERE date >= '2024-01-01'",
    ])
    assert f.severity is Severity.FAIL


def test_nonoverlapping_temporal_ranges_pass():
    f = finding_from_queries([
        "SELECT * FROM t WHERE date < '2024-01-01'",
        "SELECT * FROM t WHERE date >= '2024-01-01'",
    ])
    assert f.severity is Severity.OK


# --- overfit collapse (was only WARN below 0.95 in-sample) ---
def test_overfit_holdout_collapse_below_near_perfect_fails():
    assert OverfitFlagsCheck().run(in_sample=0.93, holdout=0.40, metric="acc").severity is Severity.FAIL
    assert OverfitFlagsCheck().run(in_sample=0.949, holdout=0.10, metric="acc").severity is Severity.FAIL


def test_overfit_good_model_still_passes():
    assert OverfitFlagsCheck().run(in_sample=0.79, holdout=0.57, metric="R2").severity is Severity.OK
