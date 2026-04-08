Run the full verification suite.

Steps:
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
3. For each command, report: PASS or FAIL (with relevant output)
4. If ALL pass:
   - Generate task ID: `task-{timestamp}`
   - Create `.harness/task-{id}/proof.md` with:
     ```markdown
     # Task Proof

     ## Task
     {objective from plan}

     ## Evidence
     - format: PASS
     - lint: PASS
     - typecheck: PASS
     - test: PASS (X tests, Y assertions)

     ## Files Changed
     - {list from git diff --name-only}

     ## Completed At
     {ISO timestamp}
     ```
   - Output: "Task COMPLETE. Proof written to .harness/task-{id}/proof.md"
5. If ANY fail:
   - Report which command failed and why
   - Suggest: go back to `/work` and fix
   - Do NOT write task-proof on failure
