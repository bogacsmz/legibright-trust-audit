# Open-source contributions — ready to open

Two prepared "contribute back" PRs. Per the hackathon rules (RFCs, docs, and skill contributions
count independent of merge), each is a clickable OSS contribution.

| # | PR | Target repo | Type |
|---|---|---|---|
| 1 | `datahub-trust-audit` skill | `datahub-project/datahub-skills` | new skill |
| 2 | SQLite profiling docs note | `datahub-project/datahub` | docs fix |

> **`gh` CLI is not installed on this machine.** Two ways forward:
> - **Install it:** `brew install gh && gh auth login` — then use the `gh pr create` lines below.
> - **No install:** fork on github.com (one click), push, and open the PR from the web UI.
>
> I (Claude) prepared everything below and verified the target files/paths exist. You open the PRs.

---

## PR 1 — skill → `datahub-project/datahub-skills`

The skill lives in this repo at [`skills/datahub-trust-audit/`](../skills/datahub-trust-audit/) and its
`SKILL.md` frontmatter already matches the datahub-skills template exactly.

```bash
# 1. Fork datahub-project/datahub-skills on github.com (button, top-right)
# 2. Clone YOUR fork and add the skill:
git clone https://github.com/<your-username>/datahub-skills && cd datahub-skills
git checkout -b feat/datahub-trust-audit-skill
cp -r ~/Claude/Projects/hackathon/skills/datahub-trust-audit skills/
pip install pre-commit && pre-commit run --all-files || true   # prettier/markdownlint/ruff (optional)
git add skills/datahub-trust-audit
git commit -m "feat: add datahub-trust-audit skill (statistical honesty auditing)"
git push -u origin feat/datahub-trust-audit-skill
# 3. Open the PR:
#    - Web: GitHub shows a "Compare & pull request" button → paste pr1-datahub-skills/PR_DESCRIPTION.md
#    - gh:  gh pr create --repo datahub-project/datahub-skills \
#             --title "feat: add datahub-trust-audit skill (statistical honesty auditing)" \
#             --body-file ~/Claude/Projects/hackathon/contrib/pr1-datahub-skills/PR_DESCRIPTION.md
```
PR title MUST be a Conventional Commit (`feat:`) — the repo's CI enforces PR titles.

---

## PR 2 — docs fix → `datahub-project/datahub`

`datahub-project/datahub` is a large monorepo — the **web editor is the easiest path** for this
one-file change (no clone).

```
# 1. Open the file on github.com:
#    https://github.com/datahub-project/datahub/blob/master/metadata-ingestion/docs/sources/sqlalchemy/sqlalchemy_pre.md
# 2. Click the pencil (Edit) → GitHub forks automatically.
# 3. Replace the file with:  contrib/pr2-datahub-docs-sqlite/sqlalchemy_pre.md
#    (only change: one blockquote added after the "This plugin extracts" list)
# 4. Commit to a new branch:  docs: note SQLite profiling limitation (max_overflow/NullPool)
# 5. Open the PR → paste  contrib/pr2-datahub-docs-sqlite/PR_DESCRIPTION.md
```
Prefer a local clone/gh instead? Same file, branch `docs/sqlite-profiling-note`, title
`docs: note SQLite profiling limitation (max_overflow/NullPool)`.

---

## After opening
Paste the two PR URLs into `docs/SUBMISSION.md` (the **Open-source contributions** section has
placeholders) so the submission links to live, clickable "contribute back" evidence. Also drop them
back to me and I'll wire them in.
