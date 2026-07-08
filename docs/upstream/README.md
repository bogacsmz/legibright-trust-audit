# Upstream contributions (bonus criterion)

Three well-formed, submittable artifacts. Per the hackathon rules ("RFCs, documentation
improvements also count"), these qualify as open-source contributions independent of merge.

| Artifact | Target repo | Type | Status |
|---|---|---|---|
| `datahub-trust-audit` skill | `datahub-project/datahub-skills` | **New skill** (SKILL.md + references + templates) | **open PR** [#30](https://github.com/datahub-project/datahub-skills/pull/30) — see `../../skills/datahub-trust-audit/` |
| `RFC-statistical-honesty-assertions.md` | `datahub-project/datahub` (RFC / discussion) | **RFC** | prepared |
| `docs-sqlite-profiling-fix.md` | `datahub-project/datahub` (docs) | **Docs fix** | **open PR** [#18272](https://github.com/datahub-project/datahub/pull/18272), includes reproducer |

## Why these are legitimate
- The **skill** conforms to the real datahub-skills format (YAML frontmatter, `references/`,
  `templates/`, multi-agent compatibility section) and adds a capability the repo lacks:
  statistical trust auditing. It is the primary deliverable AND directly submittable.
- The **RFC** proposes recognizing statistical-honesty checks (temporal leakage, calibration)
  as a first-class CUSTOM assertion pattern — extends DataHub's assertion model, doesn't rebuild it.
- The **docs fix** is a real rough edge we hit: SQLite ingestion fails under profiling because
  the profiler passes `max_overflow` to a NullPool engine. We include a minimal reproducer and
  the working recipe.

## Remaining: the RFC (not required for the hackathon)
The skill and docs-fix are already open as PRs (linked above). The RFC has no PR-shaped target
(it's a design discussion, not a file diff) — submit it as a GitHub Discussion or RFC issue
referencing this doc, whenever there's a suitable venue in the datahub-project repo.
