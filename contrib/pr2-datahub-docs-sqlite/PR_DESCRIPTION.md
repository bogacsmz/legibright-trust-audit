# docs: note SQLite profiling limitation (max_overflow / NullPool)

**Target:** `datahub-project/datahub`
**File:** `metadata-ingestion/docs/sources/sqlalchemy/sqlalchemy_pre.md`
**PR title (Conventional Commits):** `docs: note SQLite profiling limitation (max_overflow/NullPool)`

## What
Adds a one-paragraph caveat to the SQLAlchemy source docs: ingesting a **SQLite** database with
`profiling.enabled: true` fails, and points users to the working recipe (`profiling.enabled: false`).

## Why
Real rough edge hit while building on DataHub. On `acryl-datahub` 1.6, profiling a SQLite source errors:

```
TypeError: Invalid argument(s) 'max_overflow' sent to create_engine(), using configuration
SQLiteDialect_pysqlite/NullPool/Engine.
```

Root cause: the profiler requests a sized connection pool (passes `max_overflow`) for parallel column
profiling, but SQLite uses `NullPool`, which rejects pool-sizing arguments. Schema and lineage ingest
fine; only profiling fails. A one-line note on the source page saves users a failed run and a confusing
stack trace.

## Reproducer
```yaml
source:
  type: sqlalchemy
  config:
    platform: sqlite
    connect_uri: "sqlite:///data.db"
    profiling: { enabled: true }   # <- errors; set false to ingest cleanly
sink: { type: datahub-rest, config: { server: "http://localhost:8080" } }
```

## Change
A single blockquote added after the "This plugin extracts" list (see the full edited file in this
folder: `sqlalchemy_pre.md`). No code changes.

---
*Found while building [Legibright](https://github.com/bogacsmz/legibright-trust-audit), a statistical
trust-audit agent for DataHub (Build with DataHub hackathon). We ingest public SQLite demo data and hit
this profiling error firsthand.*
