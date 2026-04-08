Review all changes against the plan using an independent sub-agent.

Arguments: $ARGUMENTS (optional: path to plan file)

## Steps

1. Find the latest plan in `plans/` (or use $ARGUMENTS if provided)
2. Run `git diff` to capture all changes since plan was written
3. Launch an independent reviewer sub-agent using Task:

**Sub-agent prompt (copy to Task):**
```
You are an independent code reviewer. You have NO context about the implementation process — only the plan and the diff.

Review the following diff against this plan. For each plan step:
- Verify a code change exists
- Check tests exist and are meaningful
- Check for unrelated changes
- Classify issues: P1 (must fix), P2 (should fix), P3 (nice to have), P4 (nitpick)

Plan: {plan content}
Diff: {git diff output}

Output format:
## Review Summary
- Steps completed: X/Y
- P1 issues: (list or "none")
- P2 issues: (list or "none")
- P3/P4 issues: (list or "none")
- Verdict: PASS or FAIL
```

4. Read the sub-agent's review output
5. Check file constraints:
   - [ ] No protected paths touched
   - [ ] No files outside writable paths
6. Output final review summary with verdict

## Best-Effort Isolation

The sub-agent receives ONLY the plan + diff. Main agent's implementation context (internal reasoning, false starts, etc.) is NOT shared. This provides best-effort isolation — complete context prevention is not guaranteed.

If FAIL: suggest going back to `/work` with specific fixes needed.
If PASS: suggest running `/h-verify`.
