# Docs fix: SQLite ingestion fails when profiling is enabled

Proposed addition to the DataHub ingestion docs (SQL / SQLAlchemy source, SQLite usage).

## Problem (reproducible on acryl-datahub 1.6)
Ingesting a SQLite database with `profiling.enabled: true` fails during profiling with:

```
TypeError: Invalid argument(s) 'max_overflow' sent to create_engine(), using configuration
SQLiteDialect_pysqlite/NullPool/Engine. Please check that the keyword arguments are appropriate
for this combination of components.
```

Root cause: the profiler requests a connection pool (passing `max_overflow`) for parallel
column profiling, but SQLite uses `NullPool`, which does not accept pool-sizing arguments.

## Reproducer
```yaml
# fails:
source:
  type: sqlalchemy
  config:
    platform: sqlite
    connect_uri: "sqlite:///data.db"
    profiling: { enabled: true }
sink: { type: datahub-rest, config: { server: "http://localhost:8080" } }
```

## Workaround / recommended docs note
Disable profiling for SQLite sources (schema + lineage still ingest cleanly):
```yaml
source:
  type: sqlalchemy
  config:
    platform: sqlite
    connect_uri: "sqlite:///data.db"
    profiling: { enabled: false }
```
If column distributions are needed, compute them out-of-band, or profile against a database
whose driver supports connection pooling. A one-line caveat on the SQLite ingestion page would
save users the failed run.

## Suggested doc text
> **SQLite + profiling.** DataHub's profiler uses a connection pool; SQLite's `NullPool` rejects
> pool-sizing arguments (`max_overflow`), so `profiling.enabled: true` will error. Ingest SQLite
> with profiling disabled (schema and lineage are unaffected).
