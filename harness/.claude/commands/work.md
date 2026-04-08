Execute the latest plan.

Steps:
1. Find the latest plan file in `plans/` (sorted by date, or use $ARGUMENTS if path provided)
2. Read and parse the plan
3. For each step in order:
   a. Announce which step you're starting
   b. Write tests first (TDD)
   c. Implement minimum code to pass
   d. Run `npm test` to confirm
   e. If test fails: diagnose, fix, retry. Do NOT skip.
   f. If step succeeds: commit with message like `feat(step N): {description}`
4. After all steps: run full verification suite
5. If all pass: announce completion, suggest `/review`
6. If any fail: report which step failed and why, suggest fix

Rules:
- Execute steps IN ORDER. No jumping ahead.
- Do NOT modify files outside the plan's file list.
- Do NOT touch protected paths (.env*, .github/, lockfiles).
- If pre-existing test failures detected before starting: STOP and report.
