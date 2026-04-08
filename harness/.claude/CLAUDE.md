# Harness Rules for Claude Code

This file is the SSOT. Claude Code reads this on every session.
AGENTS.md at project root is a mirror — keep them in sync.

## Workflow: Plan → Work → Review → Verify

Every task MUST follow this sequence. No skipping steps.

### 1. Plan (`/plan`)
- Analyze the requirement (from user, PRD.md, or issue)
- Write plan to `plans/YYYY-MM-DD-topic.md`
- Plan MUST include:
  - Objective (one sentence)
  - Files to create/modify/delete
  - Implementation steps (numbered, ordered)
  - Test strategy (which tests, what they verify)
  - Risks and edge cases
- Do NOT start implementation during plan phase
- If requirement is ambiguous, ask before writing the plan

### 2. Work (`/work`)
- Read the latest plan from `plans/`
- Execute steps one by one, in order
- For each step:
  1. Write the test first (if applicable)
  2. Implement the minimum code to pass
  3. Run tests to confirm
  4. Commit with meaningful message
- Do NOT jump ahead. Do NOT skip tests.
- If a step fails, stop and diagnose. Do not paper over.

### 3. Review (`/review`)
- Diff all changes since the plan was written
- Check each plan step is addressed
- Check against DoD (below)
- If issues found, go back to Work. Do not proceed to Verify.

### 4. Verify (`/verify`)
- Run ALL verification commands in order:
  1. `npm run format` (if exists)
  2. `npm run lint` (if exists)
  3. `npm run typecheck` (if exists)
  4. `npm test`
- ALL must pass. Any failure = go back to Work.
- On success, write task-proof to `.harness/task-{id}/proof.md`

## Hard Constraints

- **No files outside writable paths.** Default writable: `src/**`, `tests/**`, `app/**`, `lib/**`, `components/**`, `utils/**`, `config/**`, `public/**`, `plans/**`, `package.json`, `tsconfig.json`, `next.config.*`, `tailwind.config.*`, `middleware.*`
- **Protected paths never touched without explicit approval:** `.env*`, `.github/`, `prisma/migrations/`, lockfiles, `docker-compose.*`
- **No destructive commands:** `rm -rf`, `git reset --hard`, `git clean`, `DROP TABLE`, etc.
- **Pre-existing failures are not your problem.** If repo is already broken before you start, report it and stop. Do not fix unrelated issues.
- **Model completion declarations are not trusted.** Always verify with actual commands, not self-assessment.

## Definition of Done

A task is COMPLETE only when ALL of:
- [ ] All plan steps are implemented
- [ ] All verification commands pass (format, lint, typecheck, test)
- [ ] Task-proof written to `.harness/task-{id}/proof.md`
- [ ] No protected paths touched
- [ ] No unresolved risks in review
- [ ] Git commit exists with all changes

## File Conventions

| Path | Purpose |
|------|---------|
| `plans/*.md` | Implementation plans |
| `.harness/task-*/proof.md` | Task completion evidence |
| `AGENTS.md` | Root-level mirror of this file |
| `PRD.md` | Product requirements (if exists) |

## Context Loading

On session start:
1. Read this file (CLAUDE.md)
2. Read AGENTS.md (root) — should match
3. Check for active plan in `plans/`
4. Check `.harness/` for in-progress tasks
5. Read `PRD.md` if exists

## Escalation

Stop and ask the user when:
- Requirement is ambiguous (after one clarification attempt)
- Protected path modification is needed
- Pre-existing test failures detected
- Plan step cannot be completed as designed
- 3+ failed attempts on the same step
