"""Infer how a train/test split was built, by reading the SQL from DataHub query history.

This is what a senior reviewer actually does when auditing a backtest: "show me how you
split." The methodology is encoded in the SQL that produced the train/test sets. We classify
each split query as:

  * TEMPORAL — a time/date column with an inequality (WHERE date < '2024-01-01'). Clean IF the
               train cutoff does not overlap the test window.
  * RANDOM   — RANDOM()/RAND()/NEWID(), ORDER BY RANDOM(), TABLESAMPLE, or hash/mod sampling.
               This is the leakage fingerprint: no temporal ordering → future leaks into train.
  * UNKNOWN  — couldn't determine → surface for a human.

Powered by sqlglot (already a DataHub dependency). Pure + unit-testable; no DataHub coupling.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

import sqlglot
from sqlglot import exp

_TIME_HINTS = ("date", "dteday", "day", "time", "ts", "timestamp", "fetched_at",
               "start_ts", "season", "year", "yr", "month", "created")
_RANDOM_FUNCS = ("rand", "random", "newid", "uuid")


class SplitKind(str, Enum):
    TEMPORAL = "TEMPORAL"
    RANDOM = "RANDOM"
    UNKNOWN = "UNKNOWN"


@dataclass
class SplitInfo:
    kind: SplitKind
    detail: str
    time_column: str | None = None
    cutoff: str | None = None


def classify_sql(sql: str) -> SplitInfo:
    sql_l = sql.lower()

    # fast textual signals first (robust even if parsing is partial)
    if "tablesample" in sql_l:
        return SplitInfo(SplitKind.RANDOM, "uses TABLESAMPLE — non-deterministic row sampling")
    if re.search(r"order\s+by\s+(rand|random|newid|uuid)\s*\(", sql_l):
        return SplitInfo(SplitKind.RANDOM, "ORDER BY RANDOM() — shuffles rows, destroys time order")
    if re.search(r"\b(mod|abs)\s*\(\s*(hash|md5|farm_fingerprint)", sql_l):
        return SplitInfo(SplitKind.RANDOM, "hash/mod bucketing — pseudo-random split, no time order")

    try:
        tree = sqlglot.parse_one(sql)
    except Exception:
        # parsing failed; fall back to keyword scan
        if any(f"{fn}(" in sql_l for fn in _RANDOM_FUNCS):
            return SplitInfo(SplitKind.RANDOM, "random function present (unparsed SQL)")
        return SplitInfo(SplitKind.UNKNOWN, "could not parse SQL")

    # any random function anywhere?
    for fn in tree.find_all(exp.Anonymous, exp.Func):
        name = (fn.name or getattr(fn, "sql_name", lambda: "")() or "").lower()
        if any(r in name for r in _RANDOM_FUNCS):
            return SplitInfo(SplitKind.RANDOM, f"random function {name}() in split query")

    # look for a time-column inequality in WHERE
    where = tree.find(exp.Where)
    if where:
        for cmp in where.find_all(exp.LT, exp.LTE, exp.GT, exp.GTE):
            col = cmp.find(exp.Column)
            lit = cmp.find(exp.Literal)
            if col is not None and _looks_temporal(col.name):
                cutoff = lit.this if lit is not None else None
                return SplitInfo(SplitKind.TEMPORAL, f"temporal predicate on `{col.name}`",
                                 time_column=col.name, cutoff=cutoff)

    # order-by a time column with a limit is also a temporal split
    if tree.find(exp.Order):
        for o in tree.find_all(exp.Ordered):
            c = o.find(exp.Column)
            if c is not None and _looks_temporal(c.name):
                return SplitInfo(SplitKind.TEMPORAL, f"ordered by time column `{c.name}`",
                                 time_column=c.name)

    return SplitInfo(SplitKind.UNKNOWN, "no temporal predicate and no random marker found")


def _looks_temporal(name: str | None) -> bool:
    if not name:
        return False
    n = name.lower()
    return any(h in n for h in _TIME_HINTS)


def finding_from_queries(queries: list[str]):
    """Turn the split SQL found in DataHub query history into a leakage Finding.

    This is the auto-fed path: the agent no longer needs hand-supplied timestamps — it
    reads how the split was actually built and judges the METHODOLOGY at the source.
    """
    from .checks.base import Finding, Severity  # local import: bridge, keep checks pure

    infos = [(q, classify_sql(q)) for q in queries]
    randoms = [(q, i) for q, i in infos if i.kind is SplitKind.RANDOM]
    temporals = [(q, i) for q, i in infos if i.kind is SplitKind.TEMPORAL]

    if randoms:
        _, info = randoms[0]
        return Finding(
            "temporal_leakage", Severity.FAIL,
            "TEMPORAL LEAKAGE — split built by a RANDOM query (from DataHub query history)",
            detail=f"{info.detail}. A random split has no time order, so future rows leak into "
                   f"training. Detected from the SQL that produced the train/test sets.",
            metrics={"n_queries": len(queries), "random_queries": len(randoms)},
            suggested_tags=["audit-failed", "temporal-leakage"],
            suggested_incident=True,
        )
    if temporals:
        _, info = temporals[0]
        return Finding(
            "temporal_leakage", Severity.OK,
            "clean temporal split (verified from query history)",
            detail=f"{info.detail}" + (f", cutoff {info.cutoff}" if info.cutoff else ""),
            metrics={"n_queries": len(queries)},
        )
    return Finding(
        "temporal_leakage", Severity.WARN,
        "split methodology UNVERIFIABLE from query history — human review",
        detail="no temporal predicate and no random marker found in the split SQL.",
        metrics={"n_queries": len(queries)},
        suggested_tags=["audit-warn"],
    )
