"""Sentinel check: schema drift vs a baseline schema.

EXTEND, not rewrite: DataHub stores each dataset's SchemaMetadata (and schema history). This
check reads two schema snapshots (baseline vs current — straight from DataHub) and diffs them
for the changes that silently break downstream code and models:

  * dropped column      — hard break (FAIL)
  * type change         — hard break (FAIL): e.g. a numeric feature became a string
  * added column        — informational (OK), unless it collides with expectations

DataHub shows you the schema; this adds the "did it change in a breaking way vs what
downstream depends on" verdict.
"""
from __future__ import annotations

from typing import Mapping

from .base import Check, Finding, Severity


class SchemaDriftCheck(Check):
    id = "schema_drift"

    def run(
        self,
        baseline: Mapping[str, str],   # {field_name: type}
        current: Mapping[str, str],
        *,
        dataset: str = "dataset",
    ) -> Finding:
        dropped = [c for c in baseline if c not in current]
        added = [c for c in current if c not in baseline]
        retyped = [f"{c}: {baseline[c]}→{current[c]}"
                   for c in baseline if c in current and _norm(baseline[c]) != _norm(current[c])]

        breaking = []
        if dropped:
            breaking.append(f"dropped {dropped}")
        if retyped:
            breaking.append(f"type change {retyped}")

        if breaking:
            return Finding(
                self.id, Severity.FAIL,
                f"{dataset} SCHEMA DRIFT — breaking change to downstream contracts",
                detail="; ".join(breaking) + (f"; added {added}" if added else ""),
                metrics={"dropped": len(dropped), "retyped": len(retyped), "added": len(added)},
                suggested_tags=["schema-drift"], suggested_incident=True,
            )
        if added:
            return Finding(self.id, Severity.OK, f"{dataset} schema compatible (added {added})",
                           metrics={"added": len(added)})
        return Finding(self.id, Severity.OK, f"{dataset} schema unchanged")


def _norm(t: str) -> str:
    """Collapse equivalent SQL/DataHub type spellings so INT==integer, etc."""
    t = (t or "").lower().strip()
    if t.startswith(("int", "bigint", "smallint")):
        return "int"
    if t.startswith(("float", "double", "real", "numeric", "decimal")):
        return "float"
    if t.startswith(("varchar", "char", "text", "string")):
        return "str"
    return t
