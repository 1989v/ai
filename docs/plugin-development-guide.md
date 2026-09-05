# Claude Code Plugin Development Guide

> ai-common marketplace 플러그인 개발/수정 시 반드시 따라야 하는 규칙.

---

## 1. Plugin 구조 규칙

```
plugins/{plugin-name}/
├── .claude-plugin/
│   └── plugin.json              # 매니페스트 (name, description, version, commands[])
├── commands/                    # 사용자가 /로 호출하는 커맨드 (자동완성에 표시)
│   └── {command-name}.md        # 플랫 파일, frontmatter에 name 없어야 함
├── skills/                      # 백그라운드 스킬 (Claude가 내부적으로 로드)
│   └── {skill-name}/
│       └── SKILL.md             # user-invocable: false 권장
├── agents/                      # 서브에이전트 정의
│   └── {agent-name}.md
├── references/                  # 커맨드/스킬이 참조하는 프로토콜 문서
├── templates/                   # 프로젝트 생성 템플릿
└── hooks/                       # 훅 설정
```

### commands/ vs skills/ 핵심 차이

| | commands/ | skills/ |
|---|---|---|
| **용도** | 사용자가 `/plugin:name`으로 직접 호출 | Claude가 내부적으로 로드하는 백그라운드 지식 |
| **자동완성** | `/` 메뉴에 표시됨 | 표시 안 됨 (`user-invocable: false`) |
| **파일 형식** | `commands/name.md` (플랫 파일) | `skills/name/SKILL.md` (디렉토리) |
| **prefix** | `plugin.json`의 `name`이 prefix가 됨 | `plugin-name:skill-name`으로 참조 |

---

## 2. 스킬 파일 작성 규칙

### 2.1 프론트매터

```yaml
---
name: start                       # 표시용. 호출명은 디렉토리명이 정한다
description: Use to … — 언제 쓰는지만. 절차를 요약하지 않는다
when_to_use: 새 기능, 기능 추가, new feature      # 트리거 문구 (description 과 합쳐 1,536자에서 잘린다)
argument-hint: "[request] [--feat]"
disable-model-invocation: true    # 또는 user-invocable: false. 둘 다 없으면 양쪽 호출
---
```

- `description` 이 절차를 요약하면 모델이 본문을 읽지 않고 요약대로 움직인다. "언제" 만 쓴다.
- 본문은 호출된 뒤 세션 내내 컨텍스트에 남는다. 짧게. 무거운 참조는 같은 폴더의 보조 파일로.
- `$ARGUMENTS`, `$0`/`$1`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_SKILL_DIR}` 치환을 쓸 수 있다.
- 그 밖의 필드: `allowed-tools` `model` `effort` `context: fork` + `agent` `hooks` `paths`.

### 2.2 plugin.json 에 `commands` 배열을 두지 않는다

`skills/` 는 자동 발견된다. `commands` 필드는 legacy 평면 `.md` 용이며 기본 탐색을 대체하므로 쓰지 않는다.

### 2.3 훅은 실제 스키마로

이벤트 32종 · 핸들러 `command` `http` `mcp_tool` `prompt` `agent` · 차단은 exit 2 또는 `permissionDecision: deny` · 피드백은 `additionalContext`. 치트시트: `plugins/hns/references/hooks-reference.md`. **실패 입력을 주입해 빨간불을 본 뒤에만 켰다고 말한다** — hns 의 옛 템플릿은 존재하지 않는 필드(`type: reminder` `PrePrompt` `condition`)로 5개월간 무동작이었다.

플러그인 레벨 `hooks/hooks.json` 은 그 플러그인이 켜진 **모든** 프로젝트에서 발화한다. 전역 활성 플러그인이면 프로젝트별 설치(settings 병합)를 택한다.

---

## 3. Skill 파일 작성 규칙

### 백그라운드 스킬에는 `user-invocable: false`

```yaml
---
name: session
description: "Load project context and key decisions at session start"
user-invocable: false
---
```

### description에 "Use when..." 패턴

```yaml
description: "Use when starting a new session or recovering from compaction to load project context"
```

Claude가 이 description을 보고 자동 로드 여부를 판단한다.

### 지원 파일 활용

```
skills/review-architecture/
├── SKILL.md              # 메인 지침 (500줄 이하)
├── skillsets/             # 절차적 서브스킬 (필요 시 로드)
│   ├── dependency-direction-analysis.md
│   └── port-adapter-compliance-audit.md
└── reference.md           # 상세 참조 (필요 시 로드)
```

SKILL.md에서 `[reference.md](reference.md)` 형식으로 참조하면 Claude가 필요할 때만 로드.

---

## 4. marketplace.json 등록 필수

새 플러그인을 만들거나 플러그인 이름/경로를 변경하면 **반드시** `.claude-plugin/marketplace.json` 업데이트:

```json
{
  "plugins": [
    {
      "name": "hns",
      "source": "./plugins/hns",
      "description": "Universal AI harness engineering"
    }
  ]
}
```

**이 파일이 없으면 `claude plugins install`이 실패한다.** marketplace CLI는 이 인덱스로 플러그인을 발견한다.

---

## 5. 버전 관리

### plugin.json version 필드

```json
{ "version": "0.3.1" }
```

- MAJOR: 호환성 깨지는 변경
- MINOR: 새 커맨드/스킬 추가
- PATCH: 버그 수정, 문서 개선

**version을 올리지 않으면 기존 사용자의 캐시가 갱신되지 않는다.**

### 설치/업데이트 후 캐시 반영

```bash
# marketplace 리프레시
cd ~/.claude/plugins/marketplaces/ai-common && git pull origin main

# 재설치 (캐시 강제 갱신)
claude plugins uninstall {plugin}@ai-common
claude plugins install {plugin}@ai-common

# 세션 내 리로드
/reload-plugins
```

---

## 6. 테스트

### 개발 중 로컬 테스트

```bash
claude --plugin-dir ./plugins/hns
```

marketplace 설치 없이 직접 로드. 변경 시 `/reload-plugins`로 핫 리로드.

### 자동완성 확인

1. `/` 입력 후 커맨드 이름 타이핑
2. `(plugin-name)` prefix와 함께 목록에 나오는지 확인
3. 안 나오면: frontmatter에 `name` 필드가 있는지 확인 (있으면 제거)

---

## 7. 현재 플러그인 목록

| Plugin | Prefix | Skills (user) | Skills (model-only) | Agents |
|--------|--------|---------------|---------------------|--------|
| **hns** | `/hns:` | 15 | 8 | 5 |
| **ai-debugger** | `/ai-debugger:` | 2 | 6 | 1 |
| **private-repo** | `/private-repo:` | 1 | 1 | 0 |
| **content-analyzer** | `/content-analyzer:` | 1 | 3 | 1 |

---

## 8. 플러그인 간 스킬 격리 규칙

플러그인이 자체 파이프라인(연속된 커맨드/스킬 체인)을 갖는 경우, 외부 플러그인 스킬과의 충돌을 방지해야 한다.

### 원칙

- **파이프라인 활성 중에는 해당 플러그인 스킬만 사용**
- 기능이 겹치는 외부 스킬은 자동 invoke하지 않음
- 외부 스킬이 필요한 경우 사용자에게 질의 후 승인 시만 활용

### 스킬 작성 시 적용

파이프라인을 갖는 플러그인의 agent-behavior 또는 core 스킬에 다음을 명시:

```markdown
## External Skill Isolation

본 플러그인 파이프라인 실행 중:
- 플러그인 내부 스킬만 사용
- 겹치는 외부 스킬(superpowers 등)은 자동 invoke 금지
- 외부 스킬 필요 시 → 사용자 질의 후 승인 시만 사용
- 파이프라인 비활성(일반 작업) 시 → 외부 스킬 자유 사용
```

### 이유

- 외부 스킬이 파이프라인 중간에 끼어들면 하네스 제어 흐름이 깨짐
- 동일 기능의 이중 실행으로 컨텍스트 낭비 및 충돌 발생
- 플러그인별 검증 루프·증거 기록 등의 일관성 훼손

### 예시: HNS + Superpowers 충돌 방지

| 겹치는 영역 | HNS (파이프라인 우선) | Superpowers (승인 시만) |
|------------|---------------------|----------------------|
| 브레인스토밍 | shape-spec | brainstorming |
| 플랜 작성 | write-spec + create-tasks | writing-plans |
| 구현 실행 | implement-tasks | executing-plans |
| 검증 | verify | verification-before-completion |

---

## 9. Troubleshooting

### 9.1 자동완성 목록 갱신 안 되는 경우

**증상**: plugin.json의 commands[]를 수정했는데 `/reload-plugins` 후에도 이전 커맨드가 계속 보임.

**원인**: `hns@ai-common`처럼 marketplace에서 설치된 플러그인은 **`~/.claude/plugins/cache/`에 캐시**된다. 로컬 소스(`ai/plugins/hns/`)를 수정해도 캐시가 갱신되지 않으면 이전 버전이 로드됨.

**해결 순서**:

```bash
# 1. plugin.json version bump (필수)
"version": "0.3.1" → "0.4.0"

# 2. commit + push (marketplace 소스 갱신)
git add -A && git commit -m "chore: version bump" && git push

# 3. marketplace 소스 pull (force push 이력이 있으면 reset --hard 필요)
cd ~/.claude/plugins/marketplaces/ai-common && git pull origin main
# diverge 에러 발생 시:
cd ~/.claude/plugins/marketplaces/ai-common && git reset --hard origin/main

# 4. 재설치 (캐시 강제 갱신)
claude plugins uninstall hns@ai-common
claude plugins install hns@ai-common

# 5. 반드시 새 세션 시작 (현재 세션은 이전 캐시 유지)
```

### 9.2 스킬이 목록에 없다

**증상**: `skills/` 에 파일을 두었는데 모델도 `/` 메뉴도 그 스킬을 모른다.

**원인 1**: 2단계 이하 디렉토리(`skills/group/name/SKILL.md`). 플러그인 `skills/` 는 한 단계만 탐색한다. → `skills/name/SKILL.md` 로 올린다.
**원인 2**: `disable-model-invocation: true` 인데 모델에게 시켰다. 그 스킬은 사용자가 `/name` 으로만 실행한다.
**원인 3**: 프론트매터 `name:` 으로 호출명을 바꾸려 했다. 호출명은 디렉토리명이다.

확인 방법(설치본을 끄고 워킹카피만 로드):
```bash
claude -p --plugin-dir ./plugins/{name} --settings '{"enabledPlugins":{"{name}@ai-common":false}}' --model haiku --max-turns 1 \
  "List every skill name starting with '{name}:' available via the Skill tool, one per line."
```

### 9.3 marketplace diverge 에러

**증상**: `git pull origin main` 시 "divergent branches" 에러.

**원인**: `git filter-repo` 등으로 force push한 이력이 있으면 marketplace 로컬 캐시와 remote가 diverge.

**해결**:
```bash
cd ~/.claude/plugins/marketplaces/ai-common && git reset --hard origin/main
```

### 9.4 현재 세션에서 변경사항 미반영

**증상**: 플러그인 재설치 + `/reload-plugins` 후에도 이전 스킬 목록이 보임.

**원인**: Claude Code 세션은 시작 시점에 스킬 목록을 메모리에 올려놓고, 세션 중에는 갱신하지 않음. `/reload-plugins`도 marketplace 캐시를 교체하지 못함.

**해결**: **반드시 새 터미널에서 새 세션 시작**. 현재 세션에서는 확인 불가.

### 9.5 실제 적용 사례: hns v0.3.1 → v0.4.0 (2026-04-06)

20개 커맨드를 8개로 축소하면서 겪은 전체 슈팅 과정:

| 단계 | 시도 | 결과 |
|------|------|------|
| 1 | plugin.json에서 commands[] 12개 제거 | ❌ commands/ 디렉토리 자동 스캔으로 여전히 노출 |
| 2 | `commands/_deprecated/`, `commands/_internal/`로 하위 이동 | ❌ 재귀 스캔으로 여전히 발견 |
| 3 | 플러그인 루트 밖(`hns-internal/`)으로 이동 | ❌ 여전히 발견 + feat 내부 호출 체인 끊김 우려 |
| 4 | frontmatter(description) 제거 | ❌ 파일명 기반으로 여전히 발견 |
| 5 | `skills/commands/{name}/SKILL.md`로 전환 + `user-invocable: false` | ✅ 자동완성에서 숨겨짐 |
| 6 | 새 세션에서도 이전 목록 보임 | ❌ marketplace 캐시(v0.3.1)가 갱신 안 됨 |
| 7 | `~/.claude/plugins/cache/` 수동 삭제 | ❌ marketplace 소스 자체가 오래됨 |
| 8 | version bump(0.4.0) + marketplace git reset --hard + uninstall/install | ✅ 최종 해결 |

**핵심 교훈**: marketplace 설치 플러그인은 로컬 소스 수정이 **자동 반영되지 않는다**. 반드시 version bump → push → marketplace pull → uninstall/install 순서를 거쳐야 한다.

---

## Quick Reference

```
새 스킬 추가:
1. skills/{name}/SKILL.md 생성 (한 단계, description 은 "언제" 만, 호출 주체 프론트매터)
2. `claude plugin validate ./plugins/{plugin} --strict`
3. 탐색 확인 (§9.2 명령) + 동작 확인 (`claude -p "/{plugin}:{name} …"`)
4. version bump
5. marketplace.json 확인
6. commit + push
7. claude plugin uninstall + install (또는 --plugin-dir 로 테스트)

훅 추가:
1. 실제 스키마로 작성 (`plugins/hns/references/hooks-reference.md`)
2. 실패 입력 주입 → 빨간불, 정상 입력 → 침묵 확인
3. `claude -p --settings <hooks.json> --output-format stream-json --include-hook-events` 로 발화 확인

새 플러그인 추가:
1. plugins/{name}/ 디렉토리 생성
2. .claude-plugin/plugin.json 매니페스트 작성
3. .claude-plugin/marketplace.json에 등록
4. commit + push + claude plugins install
```

---

## 10. AI 에이전트용 메모리 등록 권장

플러그인을 사용하는 프로젝트에서 AI 에이전트(Claude Code 등)가 커맨드/스킬을 추가할 때 배포 절차를 빠뜨리는 문제가 반복된다. 이를 방지하기 위해 **프로젝트별 피드백 메모리 등록을 권장**한다.

### 등록할 메모리 내용

```markdown
---
name: plugin-command-checklist
description: 플러그인에 새 커맨드 추가 시 반드시 따라야 하는 배포 체크리스트
type: feedback
---

새 커맨드(commands/*.md) 추가 시 배포 절차를 빠뜨리지 말 것.

**How to apply:** 커맨드 파일 작성 완료 후 반드시:
1. commands/{name}.md (frontmatter에 name 없이 description만)
2. plugin.json commands[] 추가
3. plugin.json version bump (MINOR)
4. marketplace.json 확인
5. commit + push
6. 사용자에게 캐시 갱신 안내 (uninstall + install + 새 세션)
```

### 왜 메모리인가

- PostToolUse hook: 매 Write/Edit마다 토큰 소비
- gc-protocol: 실행 시에만 검증
- **피드백 메모리**: 세션 시작 시 로드되어 토큰 비용 없이 에이전트 행동에 반영

### 등록 위치

각 프로젝트의 Claude Code 메모리 디렉터리:
```
.claude/projects/{project}/memory/feedback_plugin_command_checklist.md
```
