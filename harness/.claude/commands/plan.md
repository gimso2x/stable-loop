Analyze the requirement and create an implementation plan.

Steps:
1. Read the requirement: $ARGUMENTS
2. If PRD.md exists, read it for context
3. Check `plans/` for existing plans on the same topic
4. Check git status for any uncommitted changes
5. Write plan to `plans/YYYY-MM-DD-topic.md` using this format:

```markdown
# Plan: {topic}

## Objective
{one sentence}

## Context
{why this is needed, what triggered it}

## Files
| Action | Path | Reason |
|--------|------|--------|
| create | ... | ... |
| modify | ... | ... |

## Steps
1. ...
2. ...

## Test Strategy
- ...

## Risks
- ...

## Definition of Done
- [ ] ...
```

6. Do NOT start implementation. Output the plan path and wait for user to say `/work`.
