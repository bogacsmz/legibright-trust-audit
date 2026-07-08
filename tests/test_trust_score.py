"""Trust Score (0-100) must band to the verdict."""
from trust_layer.agent import AuditReport
from trust_layer.checks.base import Finding, Severity


def _r(*sevs):
    r = AuditReport(target="x", findings=[Finding("c", s, "h") for s in sevs])
    r.compute_verdict()
    return r


def test_all_pass_is_100():
    assert _r(Severity.OK, Severity.OK).trust_score() == 100


def test_any_fail_is_not_trustworthy_band():
    assert _r(Severity.OK, Severity.FAIL).trust_score() <= 40


def test_warn_only_is_inconclusive_band():
    s = _r(Severity.OK, Severity.WARN).trust_score()
    assert 45 <= s <= 70


def test_empty_is_mid_inconclusive():
    assert AuditReport(target="x", findings=[]).trust_score() == 50


def test_more_fails_lower_score():
    assert _r(Severity.FAIL, Severity.FAIL).trust_score() < _r(Severity.FAIL).trust_score()
