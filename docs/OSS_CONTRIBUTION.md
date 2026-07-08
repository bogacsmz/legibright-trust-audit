# Open-Source Contribution (bonus criterion) — DELIVERED

The Auditor + Sentinel are packaged as a standalone, liftable capability with zero coupling to
our betting demo, plus a DataHub-format skill, plus submittable upstream artifacts.

## 1. Packaged skill (primary)
`skills/datahub-trust-audit/` — conforms to the real `datahub-project/datahub-skills` format:
- `SKILL.md` with YAML frontmatter (`name`, `description` + triggers, `user-invocable`,
  `min-cli-version`, `allowed-tools`), a Multi-Agent Compatibility section, setup, workflow,
  and judgment rules — modelled on the repo's `datahub-search` / `datahub-quality` skills.
- `references/mcp-tools.md` — the engine's MCP tool signatures.
- `templates/audit-workflow.md` — a worked audit.

The engine is a real installable package: `pip install -e .` exposes the `trust-layer` CLI and
`python -m trust_layer.mcp_server` (MCP). The statistical core is domain-agnostic (proven on
betting + Bike Sharing + Titanic) so the skill is genuinely reusable, not demo-bound.

**Installable as a Claude Code plugin.** `.claude-plugin/plugin.json` + `marketplace.json` match
the `datahub-project/datahub-skills` schema, so the skill installs as a 6th skill alongside the
official five (setup / search / lineage / enrich / quality). It composes `datahub-search` and
`datahub-quality` and adds the statistical-honesty layer they don't ship — extend, not rewrite.

## 2. Submittable upstream artifacts (`docs/upstream/`)
- **New skill** → `datahub-project/datahub-skills` (the `datahub-trust-audit/` folder as-is).
- **RFC** `RFC-statistical-honesty-assertions.md` — proposes statistical-honesty checks as a
  documented CUSTOM/EXTERNAL assertion pattern. Extends the assertion model, no new entity type.
- **Docs fix** `docs-sqlite-profiling-fix.md` — a real rough edge we hit (SQLite + profiling
  `max_overflow`), with a reproducer and suggested doc text.

Per hackathon rules, RFCs and documentation improvements count independent of merge. The skill
and docs-fix are open, live PRs (see `docs/SUBMISSION.md`); the RFC is a prepared, well-formed
design doc.

## Why this is "extend", not "rebuild"
DataHub ships freshness/volume/profiling assertions, schema history, and incidents. We:
- **read** DataHub's profiling, schema, and query history (Sentinel + split inference),
- **add** the statistical layer DataHub lacks (Auditor: leakage/overfit/calibration; Sentinel:
  PSI/KS drift, null-spike, schema-drift diff),
- **write** results back through DataHub's own Assertion + Incident + Tag entities.
