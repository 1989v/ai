# Claude Code 훅 참조 (2.1.261 기준)

`/hns:evolve` 가 실패를 훅으로 인코딩할 때, `/hns:setup-hooks` 가 설치할 때 보는 치트시트.
원본: https://code.claude.com/docs/en/hooks

## 설정 위치와 형태

`.claude/settings.json`(프로젝트) · `.claude/settings.local.json`(개인) · `~/.claude/settings.json`(전역) · 플러그인 `hooks/hooks.json` · 스킬/에이전트 프론트매터 `hooks:`.

```json
{ "hooks": { "<Event>": [ { "matcher": "<regex|name|omit>", "hooks": [ { "type": "command", "command": "...", "timeout": 10 } ] } ] } }
```

핸들러 5종: `command`(셸) · `http`(POST) · `mcp_tool` · `prompt`(빠른 모델 판정) · `agent`(서브에이전트 검증).
공통 필드: `type` `if`(권한 규칙 필터, 예 `"Bash(git commit *)"`) `timeout` `statusMessage` `once`(스킬/에이전트 훅만).
command 필드: `command` `args`(있으면 exec 형) `async` `asyncRewake` `shell`.
경로 변수: `${CLAUDE_PROJECT_DIR}` `${CLAUDE_PLUGIN_ROOT}` `${CLAUDE_PLUGIN_DATA}`.

## 자주 쓰는 이벤트

| 이벤트 | matcher | 차단 | 입력 주요 필드 | 출력 |
|---|---|---|---|---|
| `SessionStart` | `startup\|resume\|clear\|compact\|fork` | 불가 | `start_reason` | `additionalContext` |
| `UserPromptSubmit` | — | exit 2 | `prompt` | `additionalContext` |
| `PreToolUse` | 도구명 | deny / exit 2 | `tool_name` `tool_input` | `permissionDecision`(`allow\|deny`) `permissionDecisionReason` `additionalContext` `updatedInput` |
| `PostToolUse` | 도구명 | **불가** | `tool_input` `tool_output` | `additionalContext` `updatedToolOutput` |
| `PostToolUseFailure` | 도구명 | 불가 | 실패 정보 | `additionalContext` |
| `Stop` / `SubagentStop` | — | `decision: block` / exit 2 / prompt `ok:false` | `last_assistant_message` `stop_hook_active` | `reason` |
| `PreCompact` | `manual\|auto` | exit 2 | `trigger` `custom_instructions` | `additionalContext` |
| `PostCompact` | — | 불가 | — | — |
| `TaskCreated` / `TaskCompleted` | — | exit 2 | 태스크 정보 | — |
| `InstructionsLoaded` | — | 불가 | 어떤 CLAUDE.md/rules 가 왜 로드됐는지 | 관측용 |
| `WorktreeCreate` / `WorktreeRemove` | — | — | 워크트리 경로 | — |

전체 32종: Setup · UserPromptExpansion · PermissionRequest · PermissionDenied · PostToolBatch · Notification · MessageDisplay · SubagentStart · StopFailure · TeammateIdle · ConfigChange · CwdChanged · DirectoryAdded · FileChanged · PreModelSwitch · PostModelSwitch · Elicitation · ElicitationResult 포함.

## 출력 규약

- exit 0 + stdout JSON → 구조화 판정. exit 2 → 차단(차단 가능한 이벤트에서), stderr 가 사유. 그 외 exit → 비차단 오류.
- command 훅 JSON:
  ```json
  { "hookSpecificOutput": { "hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "…", "additionalContext": "…" }, "systemMessage": "사용자에게 보이는 줄" }
  ```
- prompt/agent 훅 JSON: `{"ok": true}` 또는 `{"ok": false, "reason": "…"}` (+ `additionalContext`).
- Stop 훅에서 루프를 막으려면 `stop_hook_active == true` 일 때 통과시킨다.

## 무엇을 어디에

| 필요 | 수단 |
|---|---|
| "항상 이렇게 해" (사실·관례) | CLAUDE.md (200줄 이하) |
| 특정 경로에서만 적용되는 규칙 | `.claude/rules/*.md` + `paths:` |
| 다단계 절차 | 스킬 (`disable-model-invocation` 로 트리거 통제) |
| 사용자의 교정·선호 | auto memory (`feedback`) — Claude 가 스스로 적는다 |
| 특정 시점에 **반드시** 실행/차단 | 훅 (`PreToolUse` deny, `Stop` 게이트, `PreCompact`) |
| 도구·명령 자체를 금지 | `permissions.deny`, 샌드박스 |

CLAUDE.md 와 memory 는 컨텍스트이지 강제가 아니다. 반드시 막아야 하면 훅이나 permissions 로 간다.

## 검증 규칙

훅은 **실패 입력을 주입해 빨간불을 본 뒤에만** "켰다" 고 말한다. stdin 에 훅 입력 JSON 을 넣어 스크립트를 직접 실행하고, 세션에서는 `claude --debug` 로 발화 여부를 본다.
