# Project Harness

> This file mirrors `.claude/CLAUDE.md`. Keep them in sync.
> This file is for non-Claude agents (Cursor, Gemini, Copilot).

## Workflow: Plan → Work → Review → Verify

### 1. Plan
- Analyze requirement from user, PRD.md, or issue
- Write plan to `plans/YYYY-MM-DD-topic.md`
- Include: objective, files, steps, test strategy, risks
- Do NOT implement during plan phase

### 2. Work
- Read latest plan from `plans/`
- Execute steps in order with TDD (test first)
- Commit after each logical unit
- Stop and diagnose on failure; do not skip

### 3. Review
- Diff all changes against plan
- Verify each step is addressed
- Check DoD compliance

### 4. Verify
- Run: format → lint → typecheck → test
- All must pass
- Write task-proof to `.harness/task-{id}/proof.md`

## Constraints
- Writable paths: `src/**`, `tests/**`, `app/**`, `lib/**`, `components/**`, `utils/**`, `config/**`, `public/**`, `plans/**`, `package.json`, `tsconfig.json`, `next.config.*`, `tailwind.config.*`, `middleware.*`
- Protected (never touch without approval): `.env*`, `.github/`, `prisma/migrations/`, lockfiles
- No destructive commands
- Pre-existing failures = report and stop
- Do not trust model completion claims; verify with commands

## Definition of Done
- [ ] All plan steps implemented
- [ ] All verification commands pass
- [ ] Task-proof written
- [ ] No protected paths touched
- [ ] No unresolved risks
- [ ] Git commit exists
