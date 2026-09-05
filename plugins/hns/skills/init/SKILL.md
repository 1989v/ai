---
name: init
description: Use to initialize an hns harness in a project — scan the stack, write CLAUDE.md and the docs tree, install stack conventions as path-scoped rules, and set up hooks.
disable-model-invocation: true
argument-hint: "[--no-conventions] [--no-hooks]"
---

# /hns:init

행동 규칙: `hns:agent-behavior`. CLAUDE.md 만 필요하면 플랫폼 `/init` 이 더 가볍다(`CLAUDE_CODE_NEW_INIT=1` 이면 대화형).

## 1. 스캔
빌드 파일로 언어/프레임워크(`build.gradle.kts` `pom.xml` `package.json` `pyproject.toml` `go.mod` `Cargo.toml`), 모듈 구조(`settings.gradle.kts` includes · workspaces · 복수 `*/src/main`), 테스트 프레임워크, 빌드/테스트 명령, 기존 `.claude/` `CLAUDE.md` `AGENTS.md` `docs/`. 결과를 요약해 보여준다.

## 2. 질문 (한 번에 하나, `AskUserQuestion`)
1. 프로파일이 맞는가 (스캔 요약 첨부)
2. 아키텍처 패턴 (Clean / Layered / Monolith / Microservice / 기타)
3. (CLAUDE.md 가 있으면) 병합 / 새로 작성 / 유지

## 3. 컨벤션 → `.claude/rules/`
`templates/conventions/manifest.yml` 의 `detect` 로 번들을 매칭해 제안한다. 승인된 번들의 파일을 **`.claude/rules/{bundle}/{file}.md`** 로 복사하고 상단에 `paths:` 프론트매터(번들의 `rules_paths`)를 붙인다 — 그 경로의 파일을 읽을 때만 로드된다. 플레이스홀더 `{{base_package}}` `{{base_package_path}}` `{{service}}` `{{design_system}}` 을 치환한다. `performance` 번들은 명시 요청 시만.

## 4. 문서
템플릿(`templates/claude-md/`, `templates/docs-tree/`)으로 생성. 이미 있는 파일은 건드리지 않는다(`hns:doc-gen` 기본 동작).
- `CLAUDE.md` — 200줄 이하. 빌드/테스트 명령, 아키텍처 원칙, 규칙 위치 포인터, `/hns:start` 진입점.
- `docs/product/mission.md`, `docs/architecture/overview.md`(스택·레이어·**빌드/테스트 명령** — 여러 스킬이 여기서 읽는다), `docs/standards/agent-behavior.md`, `docs/adr/`, `docs/index.md`, `docs/index.yml`(doctor 용 문서 색인), `docs/specs/`.
- 생성 후 `hns:validate --docs`.

## 5. 훅
```
훅 수준: (A) reminder — 세션 복구·컴팩션 보존만  (B) feedback — + 커밋 전 컴파일·린트 알림  (C) enforce — + 실패 시 커밋 차단·완료 주장 증거 게이트
```
선택 후 `hns:setup-hooks` 에 위임(스크립트 복사 · settings 병합 · env 작성 · 빨간불 확인).

## 6. 멱등성
파일마다: 없으면 생성 / 같으면 건너뜀 / 다르면 diff 보여주고 병합·건너뜀·덮어쓰기 선택.

## 완료
```
hns initialized for {project}
- CLAUDE.md, docs/ (product · architecture · standards · adr · index)
- .claude/rules/ ({n} files, path-scoped)
- .claude/hooks/hns/ + settings hooks ({tier})
Next: /hns:start 로 첫 작업. /hns:doctor 로 상태 확인.
```
