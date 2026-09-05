# hns 훅 템플릿

Claude Code 2.1 실제 훅 스키마로 짠 4 스크립트 + Stop 게이트 1개. `/hns:setup-hooks` 가
`scripts/*.sh` 를 프로젝트 `.claude/hooks/hns/` 로, `settings.hooks.json` 을 `.claude/settings.json` 의
`hooks` 에 병합하고, `hns-hooks.env.example` 을 `.claude/hns-hooks.env` 로 복사한다.

| 이벤트 | 스크립트 | tier | 동작 |
|---|---|---|---|
| `SessionStart` (startup·resume·compact·clear) | `session-start-recover.sh` | 전부 | 최신 `docs/specs/*/context/progress.md` + key-decisions + 열린 pre-impl 수 + 최근 커밋을 `additionalContext` 로 주입. 진행 노트가 없으면 침묵 |
| `PreCompact` | `precompact-preserve.sh` | 전부 | 요약이 보존할 5항목과 progress 파일 경로를 지시 |
| `PreToolUse` Bash, `if: Bash(git commit *)` | `commit-gate.sh` | feedback / enforce | `HNS_COMPILE_CMD` 실행. 실패 시 feedback=알림, enforce=`permissionDecision: deny` |
| `PostToolUse` Write\|Edit | `edit-lint.sh` | feedback / enforce | 바뀐 파일만 `HNS_LINT_CMD`. 실패 시 알림(PostToolUse 는 차단 불가) |
| `Stop` | (prompt 훅, settings 안) | enforce | `last_assistant_message` 가 완료·통과를 주장하는데 명령과 결과 줄이 없으면 `{"ok": false}` 로 종료 차단. `stop_hook_active` 면 통과(루프 방지) |

원칙: 성공은 조용히(출력 없음, exit 0), 실패만 시끄럽게(컨텍스트 또는 차단).
플러그인 레벨 `hooks/hooks.json` 으로 자동 활성하지 않는다 — hns 는 사용자 전역에서 켜져 있어 다른 레포에서도 발화하기 때문. 프로젝트마다 `setup-hooks` 로 설치한다.

## 검증 방법 (배포 전 필수)

스크립트는 stdin 으로 훅 입력 JSON 을 받는다. 실패 입력을 주입해 빨간불을 먼저 본다:

```bash
cd <project>
echo '{"tool_input":{"command":"git commit -m x"}}' | HNS_HOOK_TIER=enforce HNS_COMPILE_CMD=false .claude/hooks/hns/commit-gate.sh
# → {"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny",...}}
echo '{"tool_input":{"command":"git commit -m x"}}' | HNS_HOOK_TIER=enforce HNS_COMPILE_CMD=true  .claude/hooks/hns/commit-gate.sh
# → (출력 없음, exit 0)
```

세션 안에서는 `claude --debug` 또는 `--include-hook-events` 로 발화를 확인한다.
