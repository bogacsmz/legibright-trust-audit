# feat: add datahub-trust-audit skill (statistical honesty auditing)

**Target:** `datahub-project/datahub-skills`
**Adds:** `skills/datahub-trust-audit/` (`SKILL.md` + `references/mcp-tools.md` + `templates/audit-workflow.md`)
**PR title (Conventional Commits):** `feat: add datahub-trust-audit skill (statistical honesty auditing)`

## What
A new skill, **`datahub-trust-audit`**, that audits whether a metric/model built on DataHub data is
statistically **trustworthy** — temporal/target/group leakage, overfit, and calibration — and writes the
verdict back to the graph (Assertion + Incident + Tag + a 0–100 Trust Score structured property).

It sits alongside the existing five skills and **composes** them rather than duplicating: it defers plain
catalog search to `/datahub-search` and standard freshness/volume assertions to `/datahub-quality`, and
adds the one layer they don't ship — statistical honesty.

## Why
The shipped skills answer *"is the DATA correct?"* (freshness, volume, profiling, incidents). Nothing
answers *"is the NUMBER trustworthy?"* — the failure mode that ships overfit models and leaky backtests.
This skill extends the canonical Data Quality Agent pattern with that check, using DataHub's own query
history/schema as input and its native Assertion/Incident/Tag entities as output.

## Conformance to this repo
- `SKILL.md` frontmatter matches the repo template exactly: `name`, `description: |`, `user-invocable: true`,
  `min-cli-version: 1.4.0`, `allowed-tools`.
- Includes `references/` and `templates/` like the other skills; documents Open-Source vs Cloud tiers.
- Ran `pre-commit run --all-files` (prettier / markdownlint / ruff) before pushing.

## Try it
The skill is backed by a working, tested engine (52 unit tests + a 16-check adversarial suite):
```bash
git clone https://github.com/bogacsmz/legibright-trust-audit && cd legibright-trust-audit
pip install -e '.[dev]' && python scripts/fetch_data.py && python scripts/verify_all.py
```

---
*Built for the **Build with DataHub: The Agent Hackathon** as
[Legibright](https://github.com/bogacsmz/legibright-trust-audit). Contributing the skill back upstream so
it installs beside the official five.*
