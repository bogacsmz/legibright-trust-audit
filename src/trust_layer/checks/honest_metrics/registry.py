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
from .overfit_flags import OverfitFlagsCheck
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
        inputs=("roi_in_sample", "roi_holdout", "n_cells_scanned"),
        runner=OverfitFlagsCheck().run,
        catches="too-good in-sample ROI, in-sample≫holdout gap, multiple-testing luck",
    ),
    "calibration_bias": AuditSkill(
        id="calibration_bias",
        title="Calibration / favorite-longshot bias",
        inputs=("predicted", "outcomes"),
        runner=CalibrationBiasCheck().run,
        catches="systematic probability miscalibration a single accuracy/ROI number hides",
    ),
}


def list_skills() -> list[AuditSkill]:
    return list(AUDITOR_SKILLS.values())
