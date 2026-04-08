# Plan: stable-loop v0.3 (Revised after Codex Review)

## Objective

stable-loop v0.2에 6가지 개선을 반영하여 실전 사용 가능한 수준으로 끌어올린다. Codex 리뷰에서 도출된 12개 이슈를 모두 반영.

## Codex Review 시정사항 (12건)

| # | 이슈 | 조치 |
|---|------|------|
| 1 | pretool_guard가 Bash만 차단하면 Write/Edit/Task/MCP로 우회 | 모든 툴 경로 차단으로 확장 |
| 2 | /fix "3파일 초과 자동 리다이렉트" 불가 | PostToolUse 훅으로 파일 수정 카운트 + 리다이렉트 |
| 3 | 에스컬레이션 P2→P0으로 승격 | P0으로 변경 |
| 4 | 훅 테스트 빈약 | JSON fixture 기반 이벤트별 테스트 추가 |
| 5 | SessionStart/SessionEnd는 차단 불가 | 정보 출력용으로 한정, 명시 |
| 6 | PostToolUse는 성공 후만 실행 | 한계 명시, 실패 추적은 PreToolUse 로그로 보완 |
| 7 | Sub-agent "편향 차단" 과장 | best-effort isolation로 명시 |
| 8 | skills/ 빈 디렉토리 위험 | v0.3에서 제외, v0.4로 연기 |
| 9 | 훅 병렬 실행 레이스 | 원자적 append (timestamp + pid) 사용 |
| 10 | 커스텀/내장 커맨드 충돌 | /h-review, /h-verify로 프리픽스 |
| 11 | install.sh에 chmod/shebang/path 검증 누락 | DoD에 추가 |
| 12 | 보장 범위 과장 문구 | 현실적 표현으로 수정 |

## 개선 항목

### 1. Hooks 추가 (P0)

**현실적 한계**: Claude Code 훅은 PreToolUse/UserPromptSubmit/Stop만 exit code 2로 차단 가능. SessionStart/SessionEnd는 정보 출력용.

| 훅 | 이벤트 | 동작 | 차단가능 |
|---|---|---|---|
| `pretool_guard.py` | PreToolUse | Bash(rm -rf, git push --force 등) + Write(protected 경로) + Edit(protected 경로) 차단. stdin JSON에서 tool_name과 tool_input.file_path/command 읽어 패턴 매칭. exit 2로 차단. | O |
| `fix_scope_guard.py` | PostToolUse | /fix 실행 중 Write/Edit 카운트. 3파일 초과 시 additionalContext로 "/plan으로 리다이렉트" 경고 출력 (차단은 불가, 프롬프트 규율 수준). | X (경고만) |
| `posttool_log.py` | PostToolUse | Write/Edit/Bash 성공 시 .harness/audit.log에 원자적 append. 실패 추적은 pretool_guard.py에서 별도 로그. | X (로깅만) |
| `feedback_capture.py` | UserPromptSubmit | "잘못됐어", "아닌데", "고쳐" 같은 피드백 패턴 감지 → additionalContext로 캡처 안내. | X (컨텍스트만) |
| `session_start.py` | SessionStart | 진행중 plan/task 상태 출력. 차단 목적 아님. | X (정보만) |
| `session_end.py` | SessionEnd | 미커밋 변경 경고. 차단 목적 아님. | X (정보만) |

### 2. /fix 명령 추가 (P0)

워크플로우: FIX → H-REVIEW → H-VERIFY
- 1~3파일 수정에만 허용 (fix_scope_guard.py가 PostToolUse로 카운트)
- 3파일 초과 시 fix_scope_guard.py가 경고, 에이전트가 /plan으로 리다이렉트
- systematic-debugging 5-Step 강제
- 5-Why 분석 필수
- TDD 면제 조건: 오타, 설정값, import 경로, 순수 리팩토링

### 3. 에스컬레이션 구체화 (P0 ← P2 승격)

| 조건 | 동작 | 강제수준 |
|------|------|---------|
| 3파일 초과 변경 | /plan 리다이렉트 | 훅 경고 + 마크다운 규칙 |
| 보호경로 수정 | 사용자 승인 요구 | pretool_guard.py 차단 |
| 기존 테스트 실패 | 작업 중단 + 보고 | 마크다운 규칙 |
| 같은 단계 3회 실패 | 에스컬레이션 + 접근법 변경 제안 | 마크다운 규칙 |
| 요구사항 모호 | 빈칸 3개 이하로 좁혀서 질문 | 마크다운 규칙 |
| 근본원인 복잡 | /plan으로 리다이렉트 | 마크다운 규칙 |

### 4. Anti-Rationalization (P1)

- 합리화 방지 테이블 (생각 vs 현실)
- Iron Law: "모르면 물어라. 추측은 버그다."
- Red Flags 패턴: "간단해서", "나중에", "이미 열었으니까"
- Confusion Management: 모호함 시 빈칸 3개 이하로 좁혀서 질문

### 5. Sub-agent 분리 리뷰 (P1)

**현실적 한계**: Task(sub-agent)는 독립 세션이지만, "메인 에이전트 컨텍스트 완전 차단"은 불가. best-effort isolation.

/h-review 개선:
- Task로 독립 reviewer sub-agent 생성 (best-effort isolation)
- reviewer에게 diff + plan만 주고, 메인 구현 컨텍스트는 최소화
- P1/P2/P3/P4 우선순위 분류

/h-verify 개선:
- sub-agent로 독립 verifier (best-effort isolation)

### 6. 규칙 분리 구조 (P1)

```
.claude/
├── CLAUDE.md              # 핵심 규칙 + 워크플로우 개요 (80줄 이하)
├── rules/
│   ├── anti-rationalization.md
│   ├── confusion-management.md
│   ├── scope-discipline.md
│   └── verification-protocol.md
├── commands/
│   ├── plan.md
│   ├── work.md
│   ├── h-review.md        # renamed from review.md (충돌 방지)
│   ├── h-verify.md        # renamed from verify.md (충돌 방지)
│   └── fix.md             # NEW
├── hooks/
│   ├── pretool_guard.py
│   ├── fix_scope_guard.py
│   ├── posttool_log.py
│   ├── feedback_capture.py
│   ├── session_start.py
│   └── session_end.py
├── templates/
│   └── plan-template.md
└── settings.json
```

참고: skills/는 v0.3에서 제외. 실제 스킬 콘텐츠가 없으면 빈 껍데기만 늘어남. v0.4에서 도입 검토.

## Files

| Action | Path | Reason |
|--------|------|--------|
| modify | harness/.claude/CLAUDE.md | 80줄 이하 다이어트, P0 에스컬레이션 반영 |
| create | harness/.claude/rules/anti-rationalization.md | 합리화 방지 |
| create | harness/.claude/rules/confusion-management.md | 모호함 대응 |
| create | harness/.claude/rules/scope-discipline.md | 범위 통제 |
| create | harness/.claude/rules/verification-protocol.md | 검증 프로토콜 |
| create | harness/.claude/hooks/pretool_guard.py | 전 툴 경로 차단 |
| create | harness/.claude/hooks/fix_scope_guard.py | /fix 파일 카운트 |
| create | harness/.claude/hooks/posttool_log.py | 감사 로그 |
| create | harness/.claude/hooks/feedback_capture.py | 피드백 캡처 |
| create | harness/.claude/hooks/session_start.py | 세션 시작 정보 |
| create | harness/.claude/hooks/session_end.py | 세션 종료 요약 |
| create | harness/.claude/commands/fix.md | 빠른 수정 |
| rename | harness/.claude/commands/review.md → h-review.md | 내장 커맨드 충돌 방지 |
| rename | harness/.claude/commands/verify.md → h-verify.md | 내장 커맨드 충돌 방지 |
| modify | harness/.claude/commands/work.md | scope discipline 반영 |
| modify | harness/.claude/settings.json | hooks 등록 + 권한 |
| modify | harness/AGENTS.md | 동기화 |
| create | harness/tests/hooks/ | JSON fixture 훅 테스트 |
| modify | install.sh | 전체 구조 설치 + chmod/shebang/path 검증 |
| modify | README.md | v0.3 반영 |

## Steps

### Phase 1: 규칙 분리 (CLAUDE.md 다이어트)
1. CLAUDE.md에서 상세 규칙을 rules/로 분리
2. CLAUDE.md 80줄 이하로 축소
3. AGENTS.md 미러 업데이트

### Phase 2: Hooks (P0)
4. pretool_guard.py — Bash + Write + Edit 경로 차단, stdin JSON 파싱
5. fix_scope_guard.py — PostToolUse로 Write/Edit 카운트, 3파일 초과 경고
6. posttool_log.py — 원자적 append 로깅
7. feedback_capture.py — 피드백 패턴 감지
8. session_start.py — 정보 출력
9. session_end.py — 종료 요약
10. settings.json에 hooks 등록

### Phase 3: /fix 명령 (P0)
11. fix.md 작성
12. CLAUDE.md에 /fix 워크플로우 반영

### Phase 4: 에스컬레이션 P0 통합
13. CLAUDE.md에 에스컬레이션 테이블 반영

### Phase 5: 커맨드 리네임 + 개선 (P1)
14. review.md → h-review.md (sub-agent best-effort isolation)
15. verify.md → h-verify.md (sub-agent best-effort isolation)
16. work.md에 scope discipline 반영

### Phase 6: 테스트 + 통합
17. tests/hooks/에 JSON fixture 테스트 (이벤트별 stdin, matcher 분기, exit code/output 검증)
18. install.sh 업데이트 (chmod +x, shebang, $CLAUDE_PROJECT_DIR, python3 체크)
19. 빈 프로젝트에 설치 테스트
20. git commit + push

## Test Strategy

- [ ] CLAUDE.md 80줄 이하
- [ ] install.sh 후 디렉토리 구조 일치
- [ ] install.sh이 python3, chmod +x, shebang 검증
- [ ] pretool_guard.py: Bash deny 패턴 10개 exit 2 확인
- [ ] pretool_guard.py: Write to protected path → exit 2 확인
- [ ] pretool_guard.py: Edit to protected path → exit 2 확인
- [ ] pretool_guard.py: 정상 Write/Edit → exit 0 (통과) 확인
- [ ] fix_scope_guard.py: Write 3회까지 경고 없음
- [ ] fix_scope_guard.py: Write 4회 시 additionalContext 출력
- [ ] posttool_log.py: append 로그 형식 검증
- [ ] feedback_capture.py: 피드백 패턴 감지 + additionalContext
- [ ] session_start/session_end: 정상 출력 (exit code 무관)
- [ ] JSON fixture: 이벤트별 stdin 파싱 6종 (PreToolUse Bash, PreToolUse Write, PostToolUse, UserPromptSubmit, SessionStart, SessionEnd)
- [ ] AGENTS.md = CLAUDE.md 구조 일치

## Risks

- **훅 의존성**: Python 3 필요 → install.sh에서 체크 + 경고
- **fix_scope_guard 한계**: PostToolUse는 차단 불가, 경고만 → 프롬프트 규율 수준
- **Sub-agent isolation**: best-effort, 완전 차단 불가 → 문서에 명시
- **커맨드 프리픽스**: /h-review, /h-verify가 사용자가 익숙해지는 데 시간 필요 → README에 명확히 안내
- **훅 병렬 실행 레이스**: 로그 append 시 timestamp + pid로 원자성 보장
- **과도한 규칙**: CLAUDE.md 80줄 하드 리미트로 방어, rules/는 필요시에만 읽도록

## Definition of Done

- [ ] CLAUDE.md 80줄 이하
- [ ] rules/에 4개 규칙 파일
- [ ] hooks/에 6개 훅 스크립트
- [ ] /fix 명령 추가
- [ ] /h-review, /h-verify에 sub-agent (best-effort) 명시
- [ ] 에스컬레이션 P0 반영
- [ ] tests/hooks/에 JSON fixture 테스트
- [ ] install.sh: chmod +x, shebang, python3, $CLAUDE_PROJECT_DIR 검증
- [ ] 빈 프로젝트 설치 테스트 통과
- [ ] git push 완료
