"""Sentinel check: null-rate spike vs baseline.

EXTEND, not rewrite: DataHub's profiler already reports each column's null count. It does
NOT tell you that today's null rate is ABNORMAL — a sudden spike (an upstream join broke,
a source column got renamed) that quietly poisons downstream features. This check reads the
baseline null rate (from DataHub's profile history) and the current one, and flags a spike
with a two-proportion z-test so it fires on a real jump, not on normal wobble.
"""
from __future__ import annotations

import math

from .base import Check, Finding, Severity


class NullSpikeCheck(Check):
    id = "null_spike"

    def run(
        self,
        *,
        baseline_null_rate: float,
        current_null_rate: float,
        current_n: int,
        column: str = "value",
        abs_jump_warn: float = 0.05,
        abs_jump_fail: float = 0.20,
        z_alarm: float = 3.0,
    ) -> Finding:
        if current_n < 20:
            # can't assess a spike from an ~empty window — do NOT fabricate a z=1000 FAIL
            return Finding(self.id, Severity.WARN,
                           f"{column} null-spike NOT assessed — only {current_n} current rows",
                           metrics={"current_n": current_n})
        jump = current_null_rate - baseline_null_rate
        # two-proportion z (current vs baseline as the reference proportion)
        p0 = min(max(baseline_null_rate, 1e-6), 1 - 1e-6)
        se = math.sqrt(p0 * (1 - p0) / max(current_n, 1))
        z = jump / se if se > 0 else 0.0
        detail = (f"null rate {baseline_null_rate:.1%} → {current_null_rate:.1%} "
                  f"(+{jump:.1%}, z={z:.1f}, n={current_n})")

        if jump >= abs_jump_fail and z >= z_alarm:
            return Finding(
                self.id, Severity.FAIL, f"{column} NULL SPIKE — upstream likely broke",
                detail=detail, metrics={"jump": jump, "z": z},
                suggested_tags=["null-spike"], suggested_incident=True,
            )
        if jump >= abs_jump_warn and z >= z_alarm:
            return Finding(
                self.id, Severity.WARN, f"{column} elevated null rate",
                detail=detail, metrics={"jump": jump, "z": z},
                suggested_tags=["null-spike"],
            )
        return Finding(self.id, Severity.OK, f"{column} null rate stable ({detail})",
                       metrics={"jump": jump, "z": z})
