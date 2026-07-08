"""Auditor skill registry — packaged so it can be lifted into a reusable DataHub skill.

The honest-metrics checks are the original contribution (DataHub ships freshness/volume
assertions and profiling; it does NOT ship statistical honesty: temporal leakage, overfit,
calibration). We keep them behind a small registry with declared inputs so they compose
and so the whole set can be extracted as a standalone `datahub-skill-honest-metrics`
package / upstream contribution (see docs/OSS_CONTRIBUTION.md).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..base import Finding
from .calibration_bias import CalibrationBiasCheck
from .group_leakage import GroupLeakageCheck
from .overfit_flags import OverfitFlagsCheck
from .target_leakage import TargetLeakageCheck
from .temporal_leakage import TemporalLeakageCheck


@dataclass(frozen=True)
class AuditSkill:
    id: str
    title: str
    inputs: tuple[str, ...]        # what the check needs from the graph/source
    runner: Callable[..., Finding]
    catches: str                   # the failure mode a plain ROI number hides


AUDITOR_SKILLS: dict[str, AuditSkill] = {
    "temporal_leakage": AuditSkill(
        id="temporal_leakage",
        title="Temporal leakage / random-split detector",
        inputs=("train_ts", "test_ts"),
        runner=TemporalLeakageCheck().run,
        catches="training data dated after the test cutoff — future leaks into the model",
    ),
    "overfit_flags": AuditSkill(
        id="overfit_flags",
        title="Overfit red-flag scanner",
        inputs=("in_sample", "holdout", "n_cells_scanned"),
        runner=OverfitFlagsCheck().run,
        catches="too-good in-sample ROI, in-sample≫holdout gap, multiple-testing luck",
    ),
    "calibration_bias": AuditSkill(
        id="calibration_bias",
        title="Calibration (Hosmer-Lemeshow, sample-size aware)",
        inputs=("predicted", "outcomes"),
        runner=CalibrationBiasCheck().run,
        catches="statistically-significant probability miscalibration a single score hides",
    ),
    "target_leakage": AuditSkill(
        id="target_leakage",
        title="Target leakage (single-feature separation)",
        inputs=("features", "outcomes"),
        runner=TargetLeakageCheck().run,
        catches="a feature that almost perfectly predicts the label (encodes the outcome)",
    ),
    "group_leakage": AuditSkill(
        id="group_leakage",
        title="Group leakage (entity overlap)",
        inputs=("train_groups", "test_groups"),
        runner=GroupLeakageCheck().run,
        catches="the same entity in train and test — the model memorizes it, not the pattern",
    ),
}


def list_skills() -> list[AuditSkill]:
    return list(AUDITOR_SKILLS.values())
