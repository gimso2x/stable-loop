Execute the latest plan with scope discipline.

Arguments: $ARGUMENTS (optional: path to plan file)

## Steps

1. Find the latest plan file in `plans/` (sorted by date, or use $ARGUMENTS if path provided)
2. Read and parse the plan
3. Verify pre-existing test health: run `npm test`, report if already broken → STOP
4. For each step in order:
   a. Announce which step you're starting: "→ Step N: {description}"
   b. Check scope: does this step modify files listed in the plan? If not → STOP and report
   c. Write tests first (TDD)
   d. Implement minimum code to pass
   e. Run `npm test` to confirm
   f. If test fails: diagnose, fix, retry. Maximum 3 attempts per step. On 3rd failure → STOP, escalate.
   g. If step succeeds: commit with message like `feat(step N): {description}`
5. After all steps: announce completion, suggest `/h-review`

## Scope Discipline Rules

- Execute steps IN ORDER. No jumping ahead.
- Do NOT modify files outside the plan's file list.
- Do NOT touch protected paths (.env*, .github/, lockfiles).
- Do NOT "fix adjacent code" — see `rules/scope-discipline.md`
- If you discover a better approach mid-implementation → STOP, do not switch. Suggest a plan update instead.
- If a step seems unnecessary → complete it anyway. You can suggest plan updates AFTER the full workflow.

## Anti-Rationalization Check

Before each commit, verify:
- [ ] Only files in the plan's file list are modified
- [ ] No "while I'm here" changes
- [ ] No TODO/FIXME left in new code
- [ ] No console.log/debug in production code

If any check fails → revert the unrelated changes before committing.
