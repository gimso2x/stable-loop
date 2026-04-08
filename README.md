# Stable Loop Harness

Plan → Work → Review → Verify 파이프라인으로 Claude Code의 자율 코딩을 가드레일 있는 구조로 제한하는 하네스.

## 철학

- **계획 먼저, 구현은 그 다음** — 뛰기 전에 걷기
- **3파일 이상은 무조건 `/plan`** — 작은 변경이라도 구조적 접근
- **TDD 강제** — 테스트 없는 코드는 커밋 불가
- **훅 기반 가드레일** — 위험 명령어 자동 차단, 스코프 이탈 감지
- **DoD 기반 완료** — "다 했어요"가 아니라 검증된 증거로 증명

## 구조

```
harness/
├── AGENTS.md                    # 프로젝트 규칙 (SSOT)
├── .claude/
│   ├── settings.json            # Claude Code 설정 + 훅 등록
│   ├── hooks/                   # 6개 가드레일 훅
│   │   ├── pretool_guard.py     # 위험 명령어/경로 차단 (PreToolUse)
│   │   ├── fix_scope_guard.py   # /fix 파일 수 제한 (PostToolUse)
│   │   ├── posttool_log.py      # 변경 감사 로그 (PostToolUse)
│   │   ├── session_start.py     # 세션 시작 컨텍스트 (SessionStart)
│   │   ├── session_end.py       # 세션 종료 요약 (SessionEnd)
│   │   └── feedback_capture.py  # 사용자 피드백 감지 (UserPromptSubmit)
│   ├── commands/                # 6개 슬래시 명령
│   │   ├── init.md              # /init — 프로젝트 초기 설정
│   │   ├── plan.md              # /plan — 구현 계획 작성
│   │   ├── work.md              # /work — 계획 실행 (TDD)
│   │   ├── fix.md               # /fix — 빠른 수정 (≤3파일)
│   │   ├── h-review.md          # /h-review — 변경 리뷰
│   │   └── h-verify.md          # /h-verify — 검증 파이프라인
│   └── rules/                   # 4개 규칙 파일
│       ├── scope-discipline.md  # 스코프 이탈 방지
│       ├── anti-rationalization.md  # 합리화 감지
│       ├── verification-protocol.md # 검증 프로토콜
│       └── confusion-management.md  # 혼란 관리
└── install.sh                   # 프로젝트에 설치
```

## 워크플로우

### 풀 파이프라인 (새 기능, 다중 파일 변경)
```
/plan → /work → /h-review → /h-verify
```
1. `/plan` — 요구사항 분석, `plans/YYYY-MM-DD-topic.md`에 계획 작성
2. `/work` — 단계별 TDD 실행 (테스트 먼저 → 최소 구현 → 검증 → 커밋)
3. `/h-review` — 변경사항 vs 계획 비교, DoD 체크
4. `/h-verify` — format → lint → typecheck → test, 증거 작성

### 퀵 픽스 (버그, 오타, 설정, ≤3파일)
```
/fix → /h-review → /h-verify
```

## 설치

```bash
git clone https://github.com/gimso2x/stable-loop-harness.git
cd stable-loop-harness
./install.sh /path/to/your/project
```

또는 기존 프로젝트에서:
```bash
curl -sL https://raw.githubusercontent.com/gimso2x/stable-loop-harness/main/install.sh | bash -s /path/to/your/project
```

설치 후 Claude Code를 열고 `/init`으로 시작.

## 가드레일 훅

| 훅 | 트리거 | 역할 |
|----|--------|------|
| `pretool_guard` | Bash/Write/Edit 사용 전 | `rm -rf`, `git push --force`, `.env*` 쓰기 등 차단 |
| `fix_scope_guard` | Write/Edit 사용 후 | `/fix` 중 3파일 초과 시 경고/알럿 |
| `posttool_log` | Write/Edit/Bash 사용 후 | `.harness/audit.log`에 변경 기록 |
| `session_start` | 세션 시작 | 진행 중 계획, 브랜치 상태 표시 |
| `session_end` | 세션 종료 | 변경된 파일, 커밋 상태 요약 |
| `feedback_capture` | 사용자 입력 전 | "잘못됐어", "아닌데" 등 피드백 감지 |

## 테스트

```bash
cd stable-loop-harness
python3 -m pytest tests/hooks/ -v
python3 -m unittest tests.install.test_install -v
```

설치 검증은 빈 프로젝트에 `install.sh`를 실제로 실행한 뒤, 필수 파일 복사 여부와 설치된 훅의 기본 동작까지 확인한다.

## 라이선스

MIT
