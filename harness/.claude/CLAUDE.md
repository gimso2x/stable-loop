# Harness Rules for Claude Code

This file is the SSOT. Claude Code reads this on every session.
AGENTS.md at project root is a mirror — keep them in sync.

## Workflows

| Workflow | Command | Use When |
|----------|---------|----------|
| Full pipeline | `/plan` → `/work` → `/h-review` → `/h-verify` | New features, multi-file changes, anything needing a plan |
| Quick fix | `/fix` → `/h-review` → `/h-verify` | Bug fix, typo, config change (≤3 files) |

Every task MUST follow one of these sequences. No skipping steps.

### Quick Fix (`/fix`)
- 1~3 files only. Beyond that → `/plan`
- 5-Why root cause analysis required before any change
- TDD exempt for: typos, config values, import paths, pure refactors

### Full Pipeline
- `/plan`: Write plan to `plans/YYYY-MM-DD-topic.md`. Do NOT implement.
- `/work`: Execute plan steps in order. TDD: test first, implement minimum, verify, commit.
- `/h-review`: Diff all changes vs plan. Check DoD. Sub-agent review (best-effort isolation).
- `/h-verify`: Run format→lint→typecheck→test. ALL must pass. Write proof to `.harness/task-{id}/proof.md`.

## Hard Constraints

- **Writable paths**: `src/**`, `tests/**`, `app/**`, `lib/**`, `components/**`, `utils/**`, `config/**`, `public/**`, `plans/**`, `package.json`, `tsconfig.json`, `next.config.*`, `tailwind.config.*`, `middleware.*`
- **Protected paths** (blocked by pretool_guard.py hook): `.env*`, `.github/`, `prisma/migrations/`, lockfiles, `docker-compose.*`
- **Destructive commands blocked by hook**: `rm -rf`, `git reset --hard`, `git clean`, `git push --force`, `git branch -D`, `DROP TABLE`, `npm publish`
- **Pre-existing failures**: Report and stop. Do not fix unrelated issues.
- **Verify with commands, not self-assessment.**

## Escalation (P0)

| Condition | Action | Enforcement |
|-----------|--------|-------------|
| >3 files to change | Redirect to `/plan` | Hook warning + rule |
| Protected path access | Require user approval | Hook blocks |
| Pre-existing test failures | Stop and report | Rule |
| 3+ failures on same step | Escalate, suggest different approach | Rule |
| Ambiguous requirement | Ask with ≤3 focused questions | Rule |
| Complex root cause | Redirect to `/plan` | Rule |

## Definition of Done

- [ ] All plan steps implemented
- [ ] All verification commands pass
- [ ] Task-proof written to `.harness/task-{id}/proof.md`
- [ ] No protected paths touched
- [ ] No unresolved risks
- [ ] Git commit exists

## File Conventions

| Path | Purpose |
|------|---------|
| `plans/*.md` | Implementation plans |
| `.harness/task-*/proof.md` | Task completion evidence |
| `.harness/audit.log` | Tool usage audit trail |
| `AGENTS.md` | Root-level mirror |
| `PRD.md` | Product requirements (if exists) |

## Anti-Rationalization

See `rules/anti-rationalization.md` for full table. Core rule: **"I don't know" → ask. Guessing = bugs.**

Red flags that indicate rationalization: "it's simple", "later", "already opened the file anyway".

## Detailed Rules

- `rules/anti-rationalization.md` — Common rationalization patterns and countermeasures
- `rules/confusion-management.md` — How to handle ambiguity
- `rules/scope-discipline.md` — Staying within task boundaries
- `rules/verification-protocol.md` — Verification command details
