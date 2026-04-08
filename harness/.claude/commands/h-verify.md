Run the full verification suite using an independent sub-agent.

Arguments: $ARGUMENTS (optional: task ID)

## Steps

1. Check pre-existing failures first:
   - Run `npm test` and note any failures
   - If failures exist before your changes: STOP and report. These are pre-existing.
2. Run verification commands in order:
   ```
   npm run format    (if script exists)
   npm run lint      (if script exists)
   npm run typecheck (if script exists)
   npm test
   ```
3. Launch an independent verifier sub-agent using Task:

**Sub-agent prompt (copy to Task):**
```
You are an independent verifier. Verify that all changes are correct.

Run these verification commands and report results:
1. npm run format (if exists)
2. npm run lint (if exists)
3. npm run typecheck (if exists)
4. npm test

For each: report PASS or FAIL with relevant output.
Check for: debug statements, TODO/FIXME/HACK, console.log in production code.

Output format:
## Verification Results
- format: PASS/FAIL
- lint: PASS/FAIL
- typecheck: PASS/FAIL
- test: PASS/FAIL (X tests, Y assertions)
- Code quality issues: (list or "none")
- Verdict: PASS or FAIL
```

4. Read the verifier's output
5. If ALL pass:
   - Generate task ID: `task-{timestamp}`
   - Create `.harness/task-{id}/proof.md` with evidence
   - Output: "Task COMPLETE. Proof written to .harness/task-{id}/proof.md"
6. If ANY fail:
   - Report which command failed
   - Suggest: go back to `/work`
   - Do NOT write task-proof on failure

## Best-Effort Isolation

The verifier sub-agent independently runs commands and checks. Main agent's "I'm done" claims are not trusted — the verifier makes its own assessment.
