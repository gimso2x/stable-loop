# Project Harness

> This file mirrors `.claude/CLAUDE.md`. Keep them in sync.
> This file is for non-Claude agents (Cursor, Gemini, Copilot).

## Workflows

| Workflow | Commands | Use When |
|----------|----------|----------|
| Full pipeline | `/plan` → `/work` → `/h-review` → `/h-verify` | New features, multi-file changes |
| Quick fix | `/fix` → `/h-review` → `/h-verify` | Bug fix, typo, config (≤3 files) |

### Quick Fix (`/fix`)
- 1~3 files only. Beyond that → `/plan`
- 5-Why root cause analysis required
- TDD exempt for: typos, config values, import paths, pure refactors

### Full Pipeline
- `/plan`: Write plan to `plans/YYYY-MM-DD-topic.md`. Do NOT implement.
- `/work`: Execute steps in order. TDD: test first, implement minimum, verify, commit.
- `/h-review`: Diff changes vs plan. Check DoD.
- `/h-verify`: Run format→lint→typecheck→test. Write proof.

## Hard Constraints

- **Writable paths**: `src/**`, `tests/**`, `app/**`, `lib/**`, `components/**`, `utils/**`, `config/**`, `public/**`, `plans/**`, `package.json`, `tsconfig.json`, `next.config.*`, `tailwind.config.*`, `middleware.*`
- **Protected paths**: `.env*`, `.github/`, `prisma/migrations/`, lockfiles, `docker-compose.*`
- **No destructive commands**: `rm -rf`, `git reset --hard`, `git clean`, `git push --force`, `git branch -D`, `DROP TABLE`, `npm publish`
- **Pre-existing failures**: Report and stop
- **Verify with commands, not self-assessment**

## Escalation (P0)

| Condition | Action |
|-----------|--------|
| >3 files to change | Redirect to `/plan` |
| Protected path access | Require user approval |
| Pre-existing test failures | Stop and report |
| 3+ failures on same step | Escalate, suggest different approach |
| Ambiguous requirement | Ask with ≤3 focused questions |
| Complex root cause | Redirect to `/plan` |

## Definition of Done

- [ ] All plan steps implemented
- [ ] All verification commands pass
- [ ] Task-proof written to `.harness/task-{id}/proof.md`
- [ ] No protected paths touched
- [ ] No unresolved risks
- [ ] Git commit exists

## Anti-Rationalization

Core: **"I don't know" → ask. Guessing = bugs.**
Red flags: "it's simple", "later", "already opened", "roughly".

See `rules/anti-rationalization.md` for full table.
