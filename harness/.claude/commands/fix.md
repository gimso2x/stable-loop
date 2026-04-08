Quick fix for a specific bug or issue.

Arguments: $ARGUMENTS (description of what needs fixing)

## Workflow: FIX → /h-review → /h-verify

## Pre-conditions

1. Check: Is this ≤3 files? If more files might be needed → stop and suggest `/plan`
2. Check for pre-existing test failures (run test suite first)
3. State the fix scope: which files, what changes

## Step 1: Root Cause Analysis (MANDATORY)

Before writing any code, perform 5-Why analysis:

```
Problem: {what's broken}
Why 1: ...
Why 2: ...
Why 3: ...
Why 4: ...
Why 5: {root cause}
```

If you cannot reach a root cause in 5 whys → stop and suggest `/plan` (the problem is too complex for a quick fix).

## Step 2: Fix

Apply the minimum change to address the root cause:
1. Write a failing test that reproduces the bug (if TDD-applicable — see exemptions below)
2. Implement the fix
3. Run the test to confirm it passes
4. Run full test suite to confirm no regression

**TDD Exempt** (skip test-first, but still verify after):
- Typo fixes
- Configuration value changes
- Import path corrections
- Pure refactoring (no behavior change)

## Step 3: Scope Check

Before proceeding to review:
- Count files modified. If >3 → STOP, warn user, suggest `/plan`
- Verify no unrelated changes were made (anti-rationalization check)

## Rules

- Do NOT fix "adjacent" issues discovered while fixing the target bug
- Do NOT refactor code outside the fix scope
- Do NOT skip 5-Why analysis
- If the fix is getting complex (>15 min estimate) → suggest `/plan` instead
- If pre-existing test failures exist → STOP and report to user
