"""Sentinel registry — the supporting data-health suite that EXTENDS DataHub.

Parallel to honest_metrics/registry.py (the Auditor). Every Sentinel check reads what
DataHub already knows (profile, schema, freshness/write status) and adds the temporal /
baseline-comparison layer DataHub doesn't ship. Kept behind a registry so the suite is
coherent and liftable alongside the Auditor for the OSS contribution.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .base import Finding
from .distribution_drift import DistributionDriftCheck
from .freshness import FreshnessCheck
from .null_spike import NullSpikeCheck
from .schema_drift import SchemaDriftCheck


@dataclass(frozen=True)
class SentinelSkill:
    id: str
    title: str
    reads_from_datahub: str      # what DataHub output it consumes (the "extend" contract)
    adds: str                    # the layer DataHub doesn't ship
    runner: Callable[..., Finding]


SENTINEL_SKILLS: dict[str, SentinelSkill] = {
    "freshness": SentinelSkill(
        "freshness", "Silent-staleness / value freshness",
        reads_from_datahub="write-time freshness status + column stdev from profile",
        adds="value-dynamics: catches a feed that updates on schedule but whose values froze",
        runner=FreshnessCheck().run,
    ),
    "distribution_drift": SentinelSkill(
        "distribution_drift", "Distribution drift (PSI + KS)",
        reads_from_datahub="column distribution profiles (baseline vs current)",
        adds="the temporal drift verdict DataHub's point-in-time profile doesn't compute",
        runner=DistributionDriftCheck().run,
    ),
    "null_spike": SentinelSkill(
        "null_spike", "Null-rate spike",
        reads_from_datahub="per-column null counts from the profiler",
        adds="anomaly test: is today's null rate an abnormal spike vs baseline",
        runner=NullSpikeCheck().run,
    ),
    "schema_drift": SentinelSkill(
        "schema_drift", "Breaking schema drift",
        reads_from_datahub="SchemaMetadata (and schema history)",
        adds="diff verdict: dropped/retyped columns that break downstream contracts",
        runner=SchemaDriftCheck().run,
    ),
}


def list_sentinels() -> list[SentinelSkill]:
    return list(SENTINEL_SKILLS.values())
