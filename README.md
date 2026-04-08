# stable-loop

Claude Code용 하네스 템플릿. 프로젝트에 설치하면 Claude Code가 Plan→Work→Review→Verify 흐름을 자동으로 따른다.

## 설치

```bash
git clone https://github.com/gimso2x/stable-loop.git
cd stable-loop
./install.sh /path/to/your/project
```

## 구조

설치되면 대상 프로젝트에 이런 구조가 생김:

```
your-project/
├── .claude/
│   ├── CLAUDE.md          # SSOT - 하네스 규칙 (Claude Code가 자동 읽음)
│   ├── commands/
│   │   ├── plan.md        # /plan <요구사항>
│   │   ├── work.md        # /work [plan경로]
│   │   ├── review.md      # /review
│   │   ├── verify.md      # /verify
│   │   └── init.md        # /init (재설치)
│   └── settings.json      # 툴 권한 (허용/거부)
├── AGENTS.md               # 루트 미러 (Cursor/Gemini/Copilot 호환)
├── plans/                  # 구현 계획서
└── .harness/               # 작업 증거 (gitignore)
```

## 워크플로우

```
/plan "유저 로그인 기능 추가"
  → plans/2026-04-08-user-login.md 생성

/work
  → 계획서 읽고 TDD로 단계별 구현
  → 각 단계마다 테스트 → 구현 → 커밋

/review
  → 변경사항 vs 계획서 대조
  → DoD 체크

/verify
  → format → lint → typecheck → test 전체 실행
  → 통과하면 .harness/task-{id}/proof.md 생성
```

## 핵심 원칙

- 계획 없이 구현 금지
- 테스트 없이 커밋 금지
- 검증 통과 없이 완료 선언 금지
- 모델의 "다 했어요"는 신뢰하지 않음
- 보호 경로(.env, .github, lockfile) 무단 수정 금지
- 기존 실패는 내 문제 아님 (보고 후 중단)
