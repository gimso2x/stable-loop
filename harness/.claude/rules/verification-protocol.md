# Verification Protocol

검증 명령어와 절차 상세.

## Verification Sequence

```
1. npm run format    (if script exists)
2. npm run lint      (if script exists)
3. npm run typecheck (if script exists)
4. npm test
```

모든 명령은 순서대로 실행. 하나라도 실패하면 즉시 중지 → `/work`로 돌아간다.

## Pre-Existing Failure Check

검증 시작 전, 반드시 먼저 `npm test`를 실행해서 기존 실패 여부 확인:
- 기존 실패가 있으면 → 즉시 중지, 사용자에게 보고
- 기존 실패 없음 → 전체 시퀀스 실행

## Task Proof

모든 검증 통과 시 `.harness/task-{id}/proof.md` 작성:

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

## What Counts as Verification

| O (검증으로 인정) | X (검증으로 불인정) |
|-------------------|---------------------|
| `npm test` 실행 결과 | "코드를 보면 잘 된 것 같다" |
| `npm run lint` 실행 결과 | "이전에 테스트 통과했었다" |
| 실제 런타임 실행 | "로직상 문제없을 것 같다" |
| `git diff`로 변경 확인 | 자기 자신의 판단 |

## Sub-agent Verification (/h-verify)

- Claude Code의 Task(sub-agent)로 독립 verifier 실행 (best-effort isolation)
- 메인 에이전트의 "다 됐어요"와 별개로 검증
- 단, 완전한 컨텍스트 차단은 불가 → best-effort 수준임을 인지
