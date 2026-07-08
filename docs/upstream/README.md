# Upstream contributions (bonus criterion)

Three well-formed, submittable artifacts. Per the hackathon rules ("RFCs, documentation
improvements also count"), these qualify as open-source contributions independent of merge.

| Artifact | Target repo | Type | Status |
|---|---|---|---|
| `datahub-trust-audit` skill | `datahub-project/datahub-skills` | **New skill** (SKILL.md + references + templates) | prepared, submittable — see `../../skills/datahub-trust-audit/` |
| `RFC-statistical-honesty-assertions.md` | `datahub-project/datahub` (RFC / discussion) | **RFC** | prepared |
| `docs-sqlite-profiling-fix.md` | `datahub-project/datahub` (docs) | **Docs fix** | prepared, includes reproducer |

## Why these are legitimate
- The **skill** conforms to the real datahub-skills format (YAML frontmatter, `references/`,
  `templates/`, multi-agent compatibility section) and adds a capability the repo lacks:
  statistical trust auditing. It is the primary deliverable AND directly submittable.
- The **RFC** proposes recognizing statistical-honesty checks (temporal leakage, calibration)
  as a first-class CUSTOM assertion pattern — extends DataHub's assertion model, doesn't rebuild it.
- The **docs fix** is a real rough edge we hit: SQLite ingestion fails under profiling because
  the profiler passes `max_overflow` to a NullPool engine. We include a minimal reproducer and
  the working recipe.

## How to submit (when ready — not required for the hackathon)
1. Skill: PR `skills/datahub-trust-audit/` into datahub-skills.
2. RFC: open a GitHub Discussion / RFC PR referencing this doc.
3. Docs fix: PR the ingestion-SQLite doc page with the reproducer + note.
