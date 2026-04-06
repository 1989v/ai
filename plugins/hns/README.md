# hns (Harness Scaffold) v0.2.0

AI 하네스 엔지니어링 완전체 플러그인.
하네스 3기둥(Context, Enforcement, Evolution)을 6레이어 아키텍처로 구현한다.

---

## Command Guide

### 프로젝트 초기화

| Command | Description |
|---------|-------------|
| `/hns:init` | 하네스 스캐폴딩 — auto-scan → doc-gen → hooks → context routing |

프로젝트에 처음 적용할 때 사용. CLAUDE.md, agent-os/, docs/, hooks를 한번에 생성한다.
이미 CLAUDE.md가 있는 프로젝트에도 사용 가능 (idempotency check로 병합/건너뛰기 선택).

### SDD 파이프라인

| Command | Description | When to use |
|---------|-------------|-------------|
| `/hns:feat` | shape→write→review→tasks 통합 | 새 기능 시작 시 (권장) |
| `/hns:shape-spec` | 요구사항 수집 + 스펙 폴더 초기화 | 파이프라인 없이 단계별로 할 때 |
| `/hns:write-spec` | spec.md 작성 | shape 후 스펙 문서화 |
| `/hns:spec-review` | 5차원 스펙 리뷰 | 스펙 품질 검증 |
| `/hns:create-tasks` | spec → task group 분해 | 스펙 승인 후 태스크 생성 |
| `/hns:implement-tasks` | task group 실행 (Ralph Loop) | 구현 시작 |
| `/hns:orchestrate-tasks` | 순차/병렬 오케스트레이션 | 여러 그룹 동시 실행 |
| `/hns:interview-capture` | 구현 전 게이트 인터뷰 | open-questions 해소 |

**일반적인 흐름:**
```
/hns:feat  →  /hns:implement-tasks  →  /hns:verify
```

또는 단계별:
```
/hns:shape-spec → /hns:write-spec → /hns:spec-review → /hns:create-tasks → /hns:implement-tasks
```

### 검증

| Command | Description | When to use |
|---------|-------------|-------------|
| `/hns:verify` | 표준 → 린트 → 빌드 → 테스트 | 구현 완료 후 |
| `/hns:verify-crosscheck` | 6레이어 교차 일관성 검증 | docs/specs/tasks/code 간 불일치 점검 |
| `/hns:drift-check` | 구현-스펙 불일치 감지 | 구현 중 스펙 변경 의심 시 |

**verify-crosscheck 6레이어:**
```
Layer 1: docs 내부 일관성
Layer 2: docs ↔ agent-os
Layer 3: product ↔ specs
Layer 4: standards ↔ specs
Layer 5: specs ↔ tasks
Layer 6: tasks ↔ code
```

### 문서 생성

| Command | Description | When to use |
|---------|-------------|-------------|
| `/hns:doc-gen` | CLAUDE.md + docs/ 트리 생성 (기본: 빈 곳만 채움, --full: 전체 재생성) | 프로젝트 문서 초기화/갱신 |
| `/hns:validate` | docs 일관성 + 코드 규칙 준수 검증 (dual-mode) | 문서/코드 정합성 점검 |
| `/hns:doc-html` | docs/ → HTML 사이트 생성 | 문서를 브라우저로 볼 때 |

### 하네스 자가관리 (Lifecycle)

| Command | Description | When to use |
|---------|-------------|-------------|
| `/hns:gc` | 가비지 컬렉션 | dead code, doc drift, stale rules 청소 |
| `/hns:evolve` | 실패 패턴 → 규칙 인코딩 | 같은 실수 반복 방지 |
| `/hns:diet` | 불필요한 규칙 제거 | 하네스 복잡도 점검 (Bitter Lesson) |
| `/hns:audit` | 외부 벤치마크 비교 | 다른 레포/포스트와 비교 개선 |
| `/hns:wrapup` | 세션 회고 (자동) | 세션 종료 시 evidence 기반 회고 + 리스크 분류 |

**Lifecycle 순환 사이클:**
```
audit (외부 비교) → evolve (규칙 추가) → diet (규칙 제거) → wrapup (회고) → ...
```

### 5차원 Spec Review

`/hns:spec-review` 실행 시 5개 리뷰어가 순차 실행:

| Reviewer | Focus | Skillsets |
|----------|-------|-----------|
| Architecture | 레이어 분리, 의존 방향, 포트/어댑터 | 3 |
| Domain | 바운디드 컨텍스트, 유비쿼터스 언어, Aggregate 불변식 | 3 |
| Implementation | 산술 검증, 동시성, NFR 안티패턴 | 3 |
| Test Strategy | AC→테스트 도출, Mock 경계, 테스트 레이어 | 3 |
| Usecase | 액터-목표, 시나리오 흐름, 예외/에지 케이스 | 2 |

각 리뷰어는 `skillsets/` 하위의 절차적 프로시저를 로딩하여 체크리스트를 수행한다.
판정: **SHIP** (통과) / **REVISE** (수정, max 2회) / **BLOCK** (중단, 사용자 확인)

---

## Architecture — 6 Layers

```
Layer 1: Core            — agent-behavior, session, compaction, spec-evolution
Layer 2: SDD             — spec-writing, task-planning, implementation
Layer 3: Review          — 5-dimension review + skillset procedures
Layer 4: Docs            — doc-gen, validate, doc-html
Layer 5: Lifecycle       — GC, evolve, diet, audit
Layer 6: Project-Adaptive — 프로젝트별 도메인 스킬 (init 시 생성)
```

### 하네스 3기둥 매핑

| Pillar | Concept | Layers |
|--------|---------|--------|
| **Context** | CLAUDE.md, docs, session, compaction, routing | Core + Docs |
| **Enforcement** | hooks, lints, verification gates, Ralph Loop | SDD + Review + Hooks |
| **Evolution** | GC, self-evolution, diet, benchmark | Lifecycle |

---

## Context Routing

전체 문서를 매번 스캔하지 않는다. 필요한 문서만 선택 로딩:

```
Level 0: CLAUDE.md (항상)
Level 1: command requires (커맨드별 선언)
Level 2: index.yml keyword match (자동, max 3개, threshold 2+)
```

`docs/index.yml`에 키워드 기반 라우팅 맵을 정의. 커맨드별 `requires:` frontmatter로 의존 문서를 선언.

---

## Enforcement Hooks — 3 Tiers

`/hns:init` 시 프로젝트 성격에 맞는 훅 수준을 선택:

| Tier | File | Behavior |
|------|------|----------|
| Light | `hnsf-hooks-reminder.json` | 체크리스트 리마인더만 |
| Medium | `hnsf-hooks-feedback.json` | 린트/컴파일 실패 시 피드백 (차단 안 함) |
| Strict | `hnsf-hooks-enforcement.json` | 실패 시 차단 + 자동 수정 루프 |

원칙: **성공은 조용히, 실패만 시끄럽게** (`onSuccess: silent`, `onFailure: feedback|block`)

---

## File Structure

```
harness-scaffold/
├── .claude-plugin/plugin.json      19 commands registered
├── skills/
│   ├── core/         (4)           agent-behavior, compaction, session, spec-evolution
│   ├── sdd/          (3)           spec-writing, task-planning, implementation
│   ├── review/       (5 + 14)      5 SKILL.md + 14 skillset procedures
│   ├── docs/         (3)           doc-gen, validate, doc-html
│   └── lifecycle/    (4)           gc, evolve, diet, audit
├── commands/         (19)
├── agents/           (10)
├── references/       (6)
├── templates/
│   ├── claude-md/                  CLAUDE.md templates (default, spring-kotlin)
│   ├── docs-tree/                  docs/ scaffolding templates
│   ├── hooks/                      3-tier hook templates
│   ├── docs-index.yml              context routing map template
│   ├── site-template.html          HTML doc site template
│   ├── agent-os/                   agent-os directory templates
│   ├── specs/                      spec/tasks templates
│   └── scripts/                    parallel-work.sh
└── docs/                           Knowledge Base
    ├── philosophy/   (4)           what-is-harness, three-pillars, bitter-lesson, evolution-model
    ├── decisions/    (3)           ADR-001~003
    ├── changelog/    (1)           harness-changelog.md
    ├── benchmarks/                 audit 결과 아카이브
    └── specs/        (3)           v1 design, v2 design, v2 plan
```

---

## Philosophy

> 에이전트가 실수를 할 때마다 그 실수가 다시는 반복되지 않도록 엔지니어링하는 것

자세한 내용은 `docs/philosophy/` 참조:

- **what-is-harness.md** — 하네스란? 말 비유, 모델 vs 하네스
- **three-pillars.md** — Context / Enforcement / Evolution
- **bitter-lesson.md** — 모델↑ → 하네스↓ (Richard Sutton 원칙)
- **evolution-model.md** — 실수→규칙 파이프라인, audit→evolve→diet 순환

---

## Installation

```bash
# 방법 1: --plugin-dir로 직접 로드 (개발/테스트)
claude --plugin-dir /path/to/ai/plugins/hns

# 방법 2: ai-common marketplace에서 설치
claude plugins install hns@ai-common

# 방법 3: settings.json에 직접 추가
# .claude/settings.json → "enabledPlugins": { "hns@ai-common": true }
```

플러그인 설치 후 `/hns:init`으로 프로젝트 하네스를 초기화하거나, 이미 하네스가 있는 프로젝트에서 바로 `/hns:feat`으로 기능 개발을 시작한다.

---

## Design Documents

- [v1 Design](docs/specs/2026-03-29-harness-scaffold-design.md) — 초기 4레이어 설계
- [v2 Design](docs/specs/2026-04-06-harness-v2-design.md) — 6레이어 완전체 설계
- [v2 Plan](docs/specs/2026-04-06-harness-v2-plan.md) — v2 구현 플랜 (9 tasks)
