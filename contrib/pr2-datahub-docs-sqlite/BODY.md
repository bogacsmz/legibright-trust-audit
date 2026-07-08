## What

Adds a one-paragraph caveat to the SQLAlchemy source docs: ingesting a **SQLite** database with
`profiling.enabled: true` fails, and points users to the working recipe (`profiling.enabled: false`).

## Why

A real rough edge. On `acryl-datahub` 1.6, profiling a SQLite source errors:

```
TypeError: Invalid argument(s) 'max_overflow' sent to create_engine(), using configuration
SQLiteDialect_pysqlite/NullPool/Engine.
```

Root cause: the profiler requests a sized connection pool (passes `max_overflow`) for parallel column
profiling, but SQLite uses `NullPool`, which rejects pool-sizing arguments. Schema and lineage ingest
fine; only profiling fails. A one-line note saves users a failed run and a confusing stack trace.

## Reproducer

```yaml
source:
  type: sqlalchemy
  config:
    platform: sqlite
    connect_uri: "sqlite:///data.db"
    profiling: { enabled: true } # errors; set false to ingest cleanly
sink: { type: datahub-rest, config: { server: "http://localhost:8080" } }
```

## Change

A single blockquote added after the "This plugin extracts" list. No code changes.

---

Found while building [Legibright](https://github.com/bogacsmz/legibright-trust-audit) for the Build
with DataHub hackathon — we ingest public SQLite demo data and hit this firsthand.
