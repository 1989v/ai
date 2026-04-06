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

## 2. Command 파일 작성 규칙

### frontmatter에 `name` 필드를 넣지 않는다

```yaml
# BAD — name이 있으면 prefix 없이 /init으로 등록됨
---
name: init
description: "Initialize harness"
---

# GOOD — name 없으면 파일명 기반 + plugin prefix → /hns:init
---
description: "Initialize harness"
---
```

**이유**: `name` 필드가 있으면 plugin prefix가 붙지 않아 다른 플러그인과 충돌할 수 있고, 자동완성에서 플러그인 소속을 구분할 수 없다.

### plugin.json의 `commands` 배열에 등록한다

```json
{
  "name": "hns",
  "commands": [
    "./commands/init.md",
    "./commands/new-feature.md"
  ]
}
```

**주의**: `commands/` 디렉토리 안의 .md 파일은 `plugin.json` 등록 여부와 무관하게 **자동 발견되어 자동완성에 노출**된다. 자동완성에서 숨기려면 `commands/` 밖으로 이동해야 한다 (예: `internal/`, `deprecated/`).

### description은 간결하고 검색 가능하게

```yaml
description: "Initialize AI harness for any project — auto-scan + doc-gen + hooks + routing"
```

- 250자 이내 (초과 시 잘림)
- 사용자가 검색할 키워드를 앞쪽에 배치

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

| Plugin | Prefix | Commands | Skills | Agents |
|--------|--------|----------|--------|--------|
| **hns** | `/hns:` | 19 | 12 (background) | 10 |
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

## Quick Reference

```
새 커맨드 추가:
1. commands/{name}.md 생성 (frontmatter에 name 없이 description만)
2. plugin.json commands[] 배열에 추가
3. version bump
4. marketplace.json 확인
5. commit + push
6. claude plugins uninstall + install (또는 --plugin-dir로 테스트)

새 백그라운드 스킬 추가:
1. skills/{name}/SKILL.md 생성 (user-invocable: false)
2. version bump
3. commit + push

새 플러그인 추가:
1. plugins/{name}/ 디렉토리 생성
2. .claude-plugin/plugin.json 매니페스트 작성
3. .claude-plugin/marketplace.json에 등록
4. commit + push + claude plugins install
```
