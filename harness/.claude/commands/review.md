Self-review all changes against the plan.

Steps:
1. Find the latest plan in `plans/`
2. Run `git diff` (or `git diff HEAD~N`) to see all changes since plan was written
3. For each plan step, verify:
   - [ ] Code change exists for this step
   - [ ] Tests exist and pass
   - [ ] No unrelated changes mixed in
4. Check file constraints:
   - [ ] No protected paths touched
   - [ ] No files outside writable paths
5. Check DoD:
   - [ ] All plan steps addressed
   - [ ] No TODO/FIXME/HACK left in new code
   - [ ] No console.log/debug statements in production code
6. Output a review summary:
   - Steps completed: X/Y
   - Issues found: (list or "none")
   - Verdict: PASS or FAIL (with reasons)

If FAIL: suggest going back to `/work` with specific fixes needed.
If PASS: suggest running `/verify`.
