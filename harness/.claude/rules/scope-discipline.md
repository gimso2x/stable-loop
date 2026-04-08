# Scope Discipline

작업 범위를 통제하는 규칙.

## Core Rule

**태스크에 명시된 파일/함수만 수정한다. 인접 코드에서 문제를 발견해도, 범위 밖이면 절대 수정하지 않는다.**

## NOTICED BUT NOT TOUCHING Pattern

```
발견: utils/helper.ts에 미사용 import가 있음
→ // TODO: [관찰됨] 미사용 import 제거 필요 — scope-out
→ 해당 파일 수정 안 함, 현재 태스크 계속 진행
```

## Rationalization Prevention

| Thought | Reality |
|---------|---------|
| "이거 고치면서 같이 정리하면 되지" | 한 번에 두 가지 하면 둘 다 버그가 난다. |
| "인접 코드 수정은 5분이면 돼" | 5분이 30분이 되고 regression이 생긴다. |
| "이미 파일을 열었으니까" | 파일을 열었다고 수정 권한이 생기지 않는다. |

## When Scope Expansion is Allowed

수정이 정말 필요한 경우:
1. 태스크를 즉시 중지
2. 사용자에게 보고 ("인접 코드에서 X를 발견했는데, 이것도 수정할까요?")
3. 승인 시에만 진행
4. 범위 확장이 3파일 초과면 → `/plan`으로 리다이렉트

## /fix Scope Limit

- 최대 3파일 수정 허용
- fix_scope_guard.py 훅이 PostToolUse에서 Write/Edit 카운트
- 4번째 파일 수정 시도 시 경고 출력 (물리적 차단은 불가, 프롬프트 규율 수준)
