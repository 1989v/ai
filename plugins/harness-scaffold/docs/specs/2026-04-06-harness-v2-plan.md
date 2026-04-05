# Harness Scaffold v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** harness-scaffold 플러그인을 6레이어 완전체로 확장 — doc-scaffolding 흡수, 5차원 Review, Lifecycle(GC/Evolve/Diet/Audit), Enforcement 훅, 컨텍스트 라우팅, Knowledge Base

**Architecture:** 기존 4레이어(Core/SDD/Review/Project-Adaptive)에 Docs, Lifecycle 레이어를 추가. 모든 파일은 `ai/plugins/harness-scaffold/` 하위에 위치하며, msa 프로젝트가 서브모듈로 참조.

**Tech Stack:** Markdown prompt files, JSON (hooks/plugin config), YAML (templates), HTML (site template)

**Base Path:** `/Users/gideok-kwon/IdeaProjects/ai/plugins/harness-scaffold`

---

## Task 1: Knowledge Base — Philosophy Documents

하네스 엔지니어링 철학 문서 4개 + changelog 초기화. 이후 모든 커맨드/스킬이 이 문서를 참조함.

**Files:**
- Create: `docs/philosophy/what-is-harness.md`
- Create: `docs/philosophy/three-pillars.md`
- Create: `docs/philosophy/bitter-lesson.md`
- Create: `docs/philosophy/evolution-model.md`
- Create: `docs/changelog/harness-changelog.md`
- Create: `docs/decisions/001-layer-architecture.md`
- Create: `docs/decisions/002-gc-three-modes.md`
- Create: `docs/decisions/003-doc-scaffolding-merge.md`

- [ ] **Step 1: Create `docs/philosophy/what-is-harness.md`**

```markdown
# What is Harness Engineering?

## Origin
Mitchell Hashimoto (2026-02): AI 에이전트가 같은 실수를 반복하는 문제를 해결하기 위해 명명.

> 에이전트가 실수를 할 때마다 그 실수가 다시는 반복되지 않도록 엔지니어링하는 것

## The Horse Metaphor
- AI 모델 = 야생말 (힘은 있지만 방향 없음)
- 하네스 = 마구 (고삐, 안장, 끈)
- 마구를 채워도 말이 느려지지 않음 → 오히려 올바른 방향으로 집중

## Model ≠ Harness
모델이 아닌 것이 모두 하네스:
- CLAUDE.md, AGENTS.md
- MCP servers
- Skills, Commands
- Hooks
- docs/, agent-os/

## Harness vs Prompt

| | Prompt | Harness |
|---|---|---|
| 방식 | "이거 하지 마" 부탁 | 실수 불가능한 구조 설계 |
| 성격 | 부탁 | 강제 |
| 비유 | 안전모 쓰라고 말하기 | 안전모 없으면 출입문 안 열림 |

## References
- [하네스 엔지니어링 분석](/docs/harness-engineering-analysis.md)
- Mitchell Hashimoto's agents.md approach
- OpenAI: 3 engineers, 5 months, zero code written
- LangChain: 30위 → 5위 (model unchanged, harness improved)
```

- [ ] **Step 2: Create `docs/philosophy/three-pillars.md`**

```markdown
# The Three Pillars of Harness Engineering

## Pillar 1: Context Files (컨텍스트)
AI가 작업 시작 시 가장 먼저 읽는 파일.

**원칙**: 1,000페이지 설명서가 아니라 지도를 줘야 한다.
- CLAUDE.md: 60줄 이하, 보편적으로 항상 적용되는 내용만
- 세부 내용은 다른 파일에 나눠서 필요할 때만 로딩
- 컨텍스트 부패 해결: 새 세션마다 항상 읽히는 파일

**harness-scaffold 매핑**: Core 레이어 + Docs 레이어
- `core/session` — 세션 시작/복구 시 컨텍스트 로딩
- `core/compaction` — 컨텍스트 부패 시 전략적 압축
- `docs/doc-gen` — CLAUDE.md + docs/ 생성
- Context Routing — index.yml 기반 선택적 로딩

## Pillar 2: Auto-Enforcement (자동 강제)
"좋은 코드를 작성해 줘"가 아니라 기계적으로 강제.

**원칙**: 성공은 조용히, 실패만 시끄럽게.
- 린터가 빨간 불 → 에이전트가 자체 수정 → 사람 개입 불필요
- 통과한 테스트 4,000줄을 다 보여주면 AI가 할 일을 잃어버림

**harness-scaffold 매핑**: SDD 레이어 + Review 레이어 + Hook 체계
- `sdd/implementation` — Ralph Loop (BUILD→TEST→FIX, max 3)
- `review/*` — 5차원 스펙 리뷰
- `hooks/enforcement` — 컴파일 실패 시 커밋 차단

**3단계 훅:**
| 단계 | 성격 | 용도 |
|------|------|------|
| Light (reminder) | 체크리스트 | 신규 프로젝트 |
| Medium (feedback) | 실패 알림 | 개발 중 |
| Strict (enforcement) | 실패 차단 | 안정 운영 |

## Pillar 3: Evolution (진화)
에이전트가 실수할 때마다 하네스가 더 정교해지는 구조.

**핵심**: 나쁜 패턴이 있으면 AI가 따라하므로, 주기적으로 청소(GC).
- 실수 → 새 규칙 → 린트/테스트/제약 추가
- 하네스가 시간이 지날수록 점점 더 정교해짐

**harness-scaffold 매핑**: Lifecycle 레이어
- `harness-gc` — 주기적 청소 (dead code, doc drift, rule violation)
- `harness-evolve` — 실수→규칙 자동화 파이프라인
- `harness-diet` — 모델↑ → 하네스↓ 감량
- `harness-audit` — 외부 벤치마크 비교
```

- [ ] **Step 3: Create `docs/philosophy/bitter-lesson.md`**

```markdown
# The Bitter Lesson — Harness Simplification

> 모델이 똑똑해질수록 하네스는 더 단순해져야 한다 — Richard Sutton

## Principle
모델 업그레이드마다 하드코딩 규칙을 추가하고 있다면 흐름을 거슬러 가는 것.
에이전트가 스스로 판단할 수 있는 걸 억지로 제약하는 건 역효과.

## Decision Framework
각 규칙에 대해 물어볼 것:

| 질문 | YES → | NO → |
|------|-------|------|
| 이 규칙 없이 모델이 올바르게 동작하는가? | diet 후보 | 유지 |
| 이 규칙이 최근 3개월 내 트리거된 적 있는가? | 유지 | diet 후보 |
| 모델 내장 능력과 중복되는가? | diet 후보 | 유지 |
| 다른 규칙의 하위 규칙인가? | 통합/제거 | 유지 |

## harness-diet 연계
- `/hnsf:harness-diet` 실행 시 이 프레임워크로 판단
- 제거된 규칙은 `docs/changelog/harness-changelog.md`에 기록
- 제거 후 문제 발생 시 `harness-evolve`로 복원 가능

## Complexity Tracking
하네스 토큰 수를 주기적으로 측정:
- CLAUDE.md 토큰
- 스킬 파일 총 토큰
- 에이전트 파일 총 토큰
- 훅 설정 토큰
- → 시간에 따른 추세를 changelog에 기록

## Future Direction
- 에이전트가 스스로 하네스 엔지니어링을 할 것
- "작업 환경 설정부터 먼저 풀고, 그 다음 작업을 시작"하는 방식
- 하네스가 서비스 템플릿처럼 제공될 것
```

- [ ] **Step 4: Create `docs/philosophy/evolution-model.md`**

```markdown
# Harness Evolution Model

## The Cycle

```
실수 발생
  → 패턴 분류 (코딩/아키텍처/스펙/도구)
  → 규칙 생성 (lint/hook/constraint/skillset)
  → 하네스 반영
  → changelog 기록
  → 하네스가 더 정교해짐
```

## Evolution Sources

| 소스 | 감지 방법 | 반영 대상 |
|------|----------|----------|
| 테스트 실패 | Ralph Loop 기록 | lint rule / hook |
| spec-review BLOCK | review 판정 | skillset 강화 |
| Ralph Loop 3회 초과 | implementation 기록 | agent-behavior 규칙 |
| verify 실패 | verify 보고서 | hook enforcement |
| 사용자 피드백 | 직접 입력 | CLAUDE.md constraint |

## Audit → Evolve → Diet Cycle

```
harness-audit (외부 비교)
  → 누락된 패턴 식별
  → harness-evolve (규칙 추가)
  → 시간 경과
  → harness-diet (불필요 규칙 제거)
  → harness-audit (다시 비교)
```

이 사이클이 자동 또는 수동으로 반복되면서 하네스가 최적 상태를 유지.

## Anti-Pattern
- Garbage In, Garbage Out — 문제/기획이 나쁘면 하네스로 해결 불가
- 검증되지 않은 아이디어에 하네스 구축보다 빠른 결과물이 먼저
```

- [ ] **Step 5: Create `docs/changelog/harness-changelog.md`**

```markdown
# Harness Changelog

> evolve/diet/audit에 의한 하네스 변경 자동 기록

| Date | Type | Change | Rationale |
|------|------|--------|-----------|
| 2026-04-06 | init | v2 initial release | 6-layer architecture, doc-scaffolding merge, lifecycle layer |
```

- [ ] **Step 6: Create ADR decision documents**

Create `docs/decisions/001-layer-architecture.md`:
```markdown
# ADR-001: 6-Layer Architecture

## Status: Accepted (2026-04-06)

## Context
harness-scaffold v0.1.0은 4레이어(Core/SDD/Review/Project-Adaptive). 하네스 엔지니어링 3기둥(Context/Enforcement/Evolution) 중 Evolution이 완전 부재. doc-scaffolding이 별도 플러그인으로 분리되어 init과 기능 중복.

## Decision
Docs, Lifecycle 레이어를 추가하여 6레이어로 확장.

## Consequences
- (+) 3기둥 완전 구현
- (+) doc-scaffolding 흡수로 단일 플러그인 관리
- (-) 커맨드 10→19, 에이전트 7→10, 스킬 10→20+ 으로 증가
```

Create `docs/decisions/002-gc-three-modes.md`:
```markdown
# ADR-002: GC Three Execution Modes

## Status: Accepted (2026-04-06)

## Context
GC는 하네스 3기둥 중 Evolution의 핵심. 수동만 지원하면 실행 빈도가 낮고, 자동만 지원하면 과도한 개입.

## Decision
수동(/hnsf:harness-gc) + 이벤트(hook) + 스케줄(cron) 3모드 지원.

## Consequences
- (+) 프로젝트 성격에 맞는 모드 선택 가능
- (-) 3가지 트리거 경로 관리 필요
```

Create `docs/decisions/003-doc-scaffolding-merge.md`:
```markdown
# ADR-003: doc-scaffolding Merge into harness-scaffold

## Status: Accepted (2026-04-06)

## Context
doc-scaffolding과 harness-scaffold의 init이 CLAUDE.md 생성 기능 중복. 두 플러그인을 동시에 관리하는 비용.

## Decision
doc-scaffolding의 doc-gen, doc-validate, doc-site(→doc-html)를 harness-scaffold의 Docs 레이어로 흡수. doc-scaffolding:scaffold는 제거하고 init이 역할 대체.

## Consequences
- (+) 단일 플러그인으로 전체 하네스 관리
- (+) init → doc-gen 자연스러운 흐름
- (-) doc-scaffolding 플러그인 폐기 필요 (migration)
```

- [ ] **Step 7: Commit**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai
git add plugins/harness-scaffold/docs/philosophy/ plugins/harness-scaffold/docs/changelog/ plugins/harness-scaffold/docs/decisions/
git commit -m "docs(harness-v2): add knowledge base — philosophy, changelog, ADRs"
```

---

## Task 2: References — New Protocol Documents

신규 참조 문서 3개 생성. 커맨드/스킬에서 `@references/`로 참조됨.

**Files:**
- Create: `references/gc-protocol.md`
- Create: `references/harness-philosophy.md`
- Create: `references/diet-criteria.md`

- [ ] **Step 1: Create `references/gc-protocol.md`**

```markdown
# GC Protocol

## Scan Modes

### Light Scan (이벤트 트리거)
커밋 후 자동 실행. 빠르게 끝나야 함 (30초 이내).
- 변경된 파일 범위에서만 doc drift 체크
- CLAUDE.md에 언급된 모듈/경로가 아직 유효한지 spot check

### Full Scan (수동/스케줄)
프로젝트 전체 순회.
1. **Dead code**: 미사용 import, 빈 파일, 호출 없는 public 함수
2. **Doc drift**: CLAUDE.md/docs 내용 vs 실제 코드 구조 비교
3. **Rule violation**: agent-os/standards/의 규칙 vs 코드 위반 탐지
4. **Stale harness**: 3개월 이상 트리거 안 된 규칙/훅 식별

## Report Format

```markdown
# GC Report — {date}

## Summary
| Category | Found | Auto-fixed | Manual Required |
|----------|-------|------------|-----------------|

## Dead Code
- [ ] {file:line} — {description}

## Doc Drift
- [ ] {doc-path} vs {code-path} — {drift description}

## Rule Violations
- [ ] {rule} — {violation in file:line}

## Stale Harness
- [ ] {rule/hook} — last triggered: {date or never}
```

## Auto-fix Policy
- Dead imports → auto-remove
- Doc path typos → auto-correct
- 나머지 → 사용자 확인 필요
```

- [ ] **Step 2: Create `references/harness-philosophy.md`**

```markdown
# Harness Philosophy Reference

이 문서는 harness-scaffold의 모든 커맨드/스킬이 따르는 근본 원칙을 요약.
상세 내용은 `docs/philosophy/` 참조.

## Core Principles

1. **구조 > 부탁**: 프롬프트로 부탁하지 말고, 구조적으로 강제
2. **성공은 조용히, 실패만 시끄럽게**: onSuccess: silent, onFailure: feedback/block
3. **점진적 진화**: 한번에 완벽하게가 아니라 실패마다 한 줄씩 추가
4. **모델↑ → 하네스↓**: 불필요해진 규칙은 제거 (Bitter Lesson)
5. **지도 > 설명서**: CLAUDE.md는 60줄 이하, 나머지는 필요할 때 로딩

## Context Routing Contract

```
Level 0: CLAUDE.md (항상)
Level 1: command requires (커맨드별)
Level 2: index.yml keyword match (자동, max 3, threshold 2+)
```
```

- [ ] **Step 3: Create `references/diet-criteria.md`**

```markdown
# Diet Criteria

## 감량 후보 판별 기준

| # | Criterion | Signal | Action |
|---|-----------|--------|--------|
| 1 | 3개월 이상 미트리거 | changelog에 해당 규칙 트리거 기록 없음 | 후보 |
| 2 | 모델 내장 능력 중복 | 규칙 없이도 모델이 올바르게 동작 (샘플 테스트) | 후보 |
| 3 | 상위 규칙에 포함 | 다른 규칙이 이미 동일 범위를 커버 | 통합/제거 |
| 4 | 프로젝트 해당 없음 | 현재 프로젝트 기술 스택과 무관한 규칙 | 제거 |

## 감량 프로세스
1. 후보 목록 생성 → 사용자 승인 → 제거/아카이브
2. changelog에 기록: `[date] [diet] [removed rule] [reason]`
3. 제거 후 문제 발생 시: `harness-evolve`로 즉시 복원

## 절대 제거 불가 항목
- CLAUDE.md 자체
- core/session 스킬 (세션 관리)
- core/compaction 스킬 (컨텍스트 관리)
- references/harness-philosophy.md (원칙 문서)
```

- [ ] **Step 4: Commit**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai
git add plugins/harness-scaffold/references/gc-protocol.md plugins/harness-scaffold/references/harness-philosophy.md plugins/harness-scaffold/references/diet-criteria.md
git commit -m "docs(harness-v2): add references — gc-protocol, philosophy, diet-criteria"
```

---

## Task 3: Docs Layer — Absorb doc-scaffolding

doc-scaffolding의 스킬/커맨드/에이전트/템플릿을 harness-scaffold로 이동.

**Files:**
- Create: `skills/docs/doc-gen/SKILL.md` (copy from doc-scaffolding, update Integration section)
- Create: `skills/docs/doc-validate/SKILL.md` (copy, update)
- Create: `skills/docs/doc-html/SKILL.md` (copy doc-site, rename)
- Create: `commands/doc-gen.md` (copy, update skill reference)
- Create: `commands/doc-validate.md` (copy, update)
- Create: `commands/doc-html.md` (copy doc-site.md, rename)
- Create: `agents/doc-gen-agent.md` (copy scaffolding-agent.md, rename, update references)
- Copy: `templates/claude-md/spring-kotlin.md` (from doc-scaffolding)
- Copy: `templates/docs-tree/` directory (from doc-scaffolding)
- Copy: `templates/site-template.html` (from doc-scaffolding)

- [ ] **Step 1: Create `skills/docs/doc-gen/SKILL.md`**

Copy content from `/Users/gideok-kwon/IdeaProjects/ai/plugins/doc-scaffolding/skills/doc-gen/SKILL.md`.
Change the Integration section at the bottom to:

```markdown
## Integration

- **Called by:** harness-scaffold:init (Phase 3)
- **Standalone:** `/hnsf:doc-gen`으로 직접 호출 가능
- **Calls:** 없음 (최종 생성 스킬)
```

- [ ] **Step 2: Create `skills/docs/doc-validate/SKILL.md`**

Copy from doc-scaffolding/skills/doc-validate/SKILL.md.
Change Integration section:

```markdown
## Integration

- **Called by:** harness-scaffold:init, harness-scaffold:harness-gc
- **Standalone:** `/hnsf:doc-validate`로 직접 호출 가능
- **Calls:** 없음 (검증 전용 스킬)
```

- [ ] **Step 3: Create `skills/docs/doc-html/SKILL.md`**

Copy from doc-scaffolding/skills/doc-site/SKILL.md.
Change `name: doc-site` → `name: doc-html`.
Change Integration section:

```markdown
## Integration

- **Called by:** 없음 (독립 실행)
- **Standalone:** `/hnsf:doc-html`로 직접 호출 가능
- **Calls:** 없음 (최종 생성 스킬)
- **Template:** `templates/site-template.html` 참조
```

- [ ] **Step 4: Create `commands/doc-gen.md`**

```markdown
---
name: doc-gen
description: "Generate CLAUDE.md and docs/ tree for the current project"
requires:
  - agent-os/product/tech-stack.md
auto_reference: false
---

# /hnsf:doc-gen

## Purpose
프로젝트에 CLAUDE.md와 docs/ 트리를 생성한다.

## Required Inputs
- Access to project root directory

## Expected Outputs
- CLAUDE.md
- docs/ directory tree

---

Delegate to `harness-scaffold:doc-gen-agent` with `harness-scaffold:doc-gen` skill loaded.
```

- [ ] **Step 5: Create `commands/doc-validate.md`**

```markdown
---
name: doc-validate
description: "Validate CLAUDE.md and docs/ against actual codebase"
requires: []
auto_reference: false
---

# /hnsf:doc-validate

## Purpose
CLAUDE.md와 docs/가 실제 코드 구조와 일치하는지 검증한다.

## Required Inputs
- CLAUDE.md and docs/ must exist

## Expected Outputs
- Validation report (PASS/WARN/FAIL per check)

---

Load `harness-scaffold:doc-validate` skill and execute all checks.
Output report to terminal.
```

- [ ] **Step 6: Create `commands/doc-html.md`**

```markdown
---
name: doc-html
description: "Generate navigable HTML documentation site from docs/"
requires: []
auto_reference: false
---

# /hnsf:doc-html

## Purpose
docs/ 디렉터리를 단일 index.html 문서 사이트로 변환한다.

## Required Inputs
- docs/ directory must exist

## Expected Outputs
- docs-site/index.html

---

Load `harness-scaffold:doc-html` skill and execute.
```

- [ ] **Step 7: Create `agents/doc-gen-agent.md`**

```markdown
---
name: doc-gen-agent
description: |
  Use this agent to generate CLAUDE.md and docs/ tree.
  Analyzes project structure, collects custom requirements,
  generates documentation, and validates against codebase.
model: inherit
---

# Doc Generation Agent

당신은 문서 생성 에이전트입니다.
프로젝트에 표준화된 AI 작업 문서를 생성합니다.

## 실행 순서

### 1. 프로젝트 분석
- 빌드 파일로 언어/프레임워크 감지
- 모듈 구조 감지
- 기존 CLAUDE.md, docs/ 존재 여부 확인

### 2. 커스텀 요구사항 수집
사용자에게 한 번에 하나씩 질문:
1. 프로젝트의 핵심 목적
2. 아키텍처 원칙
3. 테스트 규칙
4. API 포맷 컨벤션
5. 비즈니스 정책

### 3. 문서 생성
harness-scaffold:doc-gen 스킬의 지침에 따라 CLAUDE.md + docs/ 트리를 생성.

### 4. 검증
harness-scaffold:doc-validate 스킬의 지침에 따라 검증.

## MSA 멀티 모듈 처리
settings.gradle.kts에 서비스 모듈이 여러 개 포함된 경우:
- 루트에 공통 docs/ (adr, architecture, plans)
- 각 서비스 모듈에 개별 docs/ (policies 중심)
```

- [ ] **Step 8: Copy templates from doc-scaffolding**

Copy these files from doc-scaffolding to harness-scaffold:
- `templates/claude-md/spring-kotlin.md` (already exists as `templates/claude-md/default.md`, add spring-kotlin alongside)
- `templates/docs-tree/index.md`
- `templates/docs-tree/architecture/overview.md`
- `templates/docs-tree/adr/_template.md`
- `skills/docs/doc-html/site-template.html` (from doc-scaffolding root `skills/doc-site/`)

Note: Read each file from doc-scaffolding source, then Write to harness-scaffold destination.

- [ ] **Step 9: Commit**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai
git add plugins/harness-scaffold/skills/docs/ plugins/harness-scaffold/commands/doc-gen.md plugins/harness-scaffold/commands/doc-validate.md plugins/harness-scaffold/commands/doc-html.md plugins/harness-scaffold/agents/doc-gen-agent.md plugins/harness-scaffold/templates/
git commit -m "feat(harness-v2): absorb doc-scaffolding into Docs layer"
```

---

## Task 4: Review Layer — 5-Dimension + Skillsets

기존 3 리뷰어에 domain + test-strategy 추가. 기존 3개에도 skillsets 디렉토리 추가.

**Files:**
- Create: `skills/review/domain/SKILL.md`
- Create: `skills/review/domain/skillsets/bounded-context-leakage-check.md`
- Create: `skills/review/domain/skillsets/ubiquitous-language-drift-scan.md`
- Create: `skills/review/domain/skillsets/aggregate-invariant-trace.md`
- Create: `skills/review/test-strategy/SKILL.md`
- Create: `skills/review/test-strategy/skillsets/ac-to-test-case-derivation.md`
- Create: `skills/review/test-strategy/skillsets/mock-boundary-decision.md`
- Create: `skills/review/test-strategy/skillsets/test-layer-assignment.md`
- Create: `skills/review/architecture/skillsets/dependency-direction-analysis.md`
- Create: `skills/review/architecture/skillsets/port-adapter-compliance-audit.md`
- Create: `skills/review/architecture/skillsets/module-boundary-impact-scan.md`
- Create: `skills/review/implementation/skillsets/arithmetic-verification.md`
- Create: `skills/review/implementation/skillsets/concurrent-write-simulation.md`
- Create: `skills/review/implementation/skillsets/nfr-anti-pattern-scan.md`
- Create: `skills/review/usecase/skillsets/ac-to-scenario-traceability.md`
- Create: `skills/review/usecase/skillsets/exception-edge-case-expansion.md`
- Modify: `commands/spec-review.md` (3→5 reviewers)

- [ ] **Step 1: Create `skills/review/domain/SKILL.md`**

```markdown
---
name: review-domain
description: Use when reviewing specs for domain model integrity - checks bounded contexts, ubiquitous language, aggregate invariants
---

# Domain Review

## Seed Discovery Protocol
Apply `@references/review-protocol.md` stages 1-4.

## Checklist
- [ ] Bounded context boundaries clearly defined? No leakage across contexts?
- [ ] Ubiquitous language consistent between spec and existing codebase?
- [ ] Aggregate invariants explicitly stated and enforceable?
- [ ] Domain events properly scoped to owning aggregate?
- [ ] No cross-aggregate direct references? (API only)
- [ ] Value Objects vs Entities correctly classified?

For each check item, load the corresponding skillset from `skillsets/` if available.

## Verdict
- **SHIP**: All checks passed
- **REVISE**: Non-blocking issues (max 2 rounds)
- **BLOCK**: Critical domain model violation → escalate

## Output
`docs/specs/{feature}/context/engineer-review-domain.md`

## NEVER
- Start review without Seed Discovery Protocol
- Return verdict without evidence (cite file:line)
- Mix reviewer types
```

- [ ] **Step 2: Create domain skillsets**

Create `skills/review/domain/skillsets/bounded-context-leakage-check.md`:
```markdown
# Bounded Context Leakage Check

## Procedure
1. Spec에서 정의된 바운디드 컨텍스트 경계를 식별
2. 해당 컨텍스트의 패키지/모듈 경계를 코드에서 확인
3. 경계를 넘는 직접 참조가 있는지 Grep으로 탐지:
   - 다른 컨텍스트의 Entity/Repository 직접 import
   - 다른 컨텍스트의 DB 테이블 직접 접근
4. 발견 시 file:line 증거와 함께 보고

## Pass Criteria
- 컨텍스트 간 통신은 API/이벤트만 사용
- 직접 import/DB 공유 없음
```

Create `skills/review/domain/skillsets/ubiquitous-language-drift-scan.md`:
```markdown
# Ubiquitous Language Drift Scan

## Procedure
1. Spec에서 사용된 도메인 용어 목록을 추출
2. 코드베이스에서 해당 용어가 동일하게 사용되는지 Grep으로 확인
3. 동의어/약어/불일치 패턴 탐지:
   - spec: "주문 취소" vs code: "orderCancel" (OK)
   - spec: "환불" vs code: "refund" + "cancel" (drift)
4. 클래스명, 메서드명, 변수명에서 용어 일관성 확인

## Pass Criteria
- spec 용어와 코드 용어 1:1 매핑 가능
- 동일 개념에 다른 이름 없음
```

Create `skills/review/domain/skillsets/aggregate-invariant-trace.md`:
```markdown
# Aggregate Invariant Trace

## Procedure
1. Spec에서 정의된 Aggregate와 불변식(invariant) 식별
2. 해당 Aggregate의 코드 구현 찾기
3. 불변식이 생성자/팩토리/커맨드 메서드에서 검증되는지 확인
4. 불변식 위반 가능 경로가 있는지 탐지:
   - setter로 직접 상태 변경
   - 불변식 체크 없는 상태 전이

## Pass Criteria
- 모든 불변식이 코드에서 강제됨
- 외부에서 Aggregate 내부 상태 직접 변경 불가
```

- [ ] **Step 3: Create `skills/review/test-strategy/SKILL.md`**

```markdown
---
name: review-test-strategy
description: Use when reviewing specs for test strategy adequacy - checks AC-to-test derivation, test layer assignment, mock boundaries
---

# Test Strategy Review

## Seed Discovery Protocol
Apply `@references/review-protocol.md` stages 1-4.

## Checklist
- [ ] Every Acceptance Criterion has at least one test case derived?
- [ ] Test layer assignment appropriate? (unit/integration/component/e2e)
- [ ] Mock boundaries clearly defined? No over-mocking?
- [ ] Test data strategy specified? (fixtures, factories, builders)
- [ ] Negative/edge cases covered in test plan?
- [ ] Test naming convention consistent with project standards?

For each check item, load the corresponding skillset from `skillsets/` if available.

## Verdict
- **SHIP**: All checks passed
- **REVISE**: Non-blocking issues (max 2 rounds)
- **BLOCK**: Critical test coverage gap → escalate

## Output
`docs/specs/{feature}/context/engineer-review-test-strategy.md`

## NEVER
- Start review without Seed Discovery Protocol
- Return verdict without evidence
- Mix reviewer types
```

- [ ] **Step 4: Create test-strategy skillsets**

Create `skills/review/test-strategy/skillsets/ac-to-test-case-derivation.md`:
```markdown
# AC to Test Case Derivation

## Procedure
1. Spec의 모든 Acceptance Criteria 목록 추출
2. 각 AC에 대해 최소 1개의 테스트 케이스가 tasks.md에 있는지 확인
3. AC → test 매핑 매트릭스 생성
4. 매핑 없는 AC를 gap으로 보고

## Pass Criteria
- 모든 AC에 최소 1개 테스트 매핑
- 매핑 매트릭스에 빈 행 없음
```

Create `skills/review/test-strategy/skillsets/mock-boundary-decision.md`:
```markdown
# Mock Boundary Decision

## Procedure
1. Spec에서 외부 의존성(DB, API, 메시징) 식별
2. 각 의존성의 mock 여부 판단:
   - Domain 테스트: mock 금지 (순수 단위)
   - Application 테스트: Outbound Port만 mock
   - Integration 테스트: 외부 API만 mock, DB는 실제
3. Over-mocking 패턴 탐지:
   - 내부 서비스를 mock하는 경우
   - 테스트 대상 자체를 mock하는 경우

## Pass Criteria
- mock 경계가 레이어별로 일관
- 과도한 mock 없음
```

Create `skills/review/test-strategy/skillsets/test-layer-assignment.md`:
```markdown
# Test Layer Assignment

## Procedure
1. Tasks에 정의된 각 테스트의 레이어 확인
2. 테스트 대상에 적합한 레이어인지 판단:
   - 순수 로직 → unit
   - Port/Adapter 연동 → integration
   - API 전체 흐름 → component/e2e
3. 레이어 불일치 보고:
   - DB 쿼리 테스트가 unit으로 분류된 경우
   - 순수 계산 테스트가 e2e로 분류된 경우

## Pass Criteria
- 테스트 레이어와 대상의 성격이 일치
- 불필요하게 무거운 레이어 사용 없음
```

- [ ] **Step 5: Create architecture skillsets**

Create `skills/review/architecture/skillsets/dependency-direction-analysis.md`:
```markdown
# Dependency Direction Analysis

## Procedure
1. Spec에서 새로 추가/변경되는 모듈 간 의존 관계 식별
2. import 문 분석으로 의존 방향 확인:
   - domain → infrastructure (위반)
   - application → infrastructure (위반)
   - infrastructure → domain (정상)
3. 위반 경로 file:line 증거 수집

## Pass Criteria
- 의존 방향이 항상 안쪽(domain) 방향
- 역방향 의존 없음
```

Create `skills/review/architecture/skillsets/port-adapter-compliance-audit.md`:
```markdown
# Port-Adapter Compliance Audit

## Procedure
1. Application 레이어의 Outbound Port(인터페이스) 목록 확인
2. Infrastructure 레이어에 대응하는 Adapter(구현체) 존재 여부 확인
3. Application이 Adapter를 직접 참조하는 경우 탐지
4. Port 없이 직접 Repository/Client를 사용하는 경우 보고

## Pass Criteria
- 모든 외부 의존은 Port 인터페이스를 통해 접근
- Application → Adapter 직접 참조 없음
```

Create `skills/review/architecture/skillsets/module-boundary-impact-scan.md`:
```markdown
# Module Boundary Impact Scan

## Procedure
1. Spec에서 변경되는 모듈 경계 식별
2. 해당 모듈의 public API(controller, port) 변경 사항 확인
3. 다른 모듈에서 해당 API를 사용하는 곳 Grep
4. Breaking change 여부 판단

## Pass Criteria
- 모듈 경계 변경 시 영향 받는 곳 모두 식별
- Breaking change 시 마이그레이션 계획 존재
```

- [ ] **Step 6: Create implementation skillsets**

Create `skills/review/implementation/skillsets/arithmetic-verification.md`:
```markdown
# Arithmetic Verification

## Procedure
1. Spec에서 금액, 수량, 비율 등 산술 연산이 포함된 요구사항 식별
2. 구현 코드에서 해당 연산 찾기
3. 경계 조건 확인: 0, 음수, overflow, 소수점 정밀도
4. BigDecimal 사용 여부 (금액 연산 시 필수)

## Pass Criteria
- 금액 연산에 BigDecimal 사용
- 경계 조건 처리 존재
```

Create `skills/review/implementation/skillsets/concurrent-write-simulation.md`:
```markdown
# Concurrent Write Simulation

## Procedure
1. Spec에서 동시 쓰기가 발생할 수 있는 시나리오 식별
2. 해당 코드의 동시성 제어 메커니즘 확인:
   - Optimistic locking (@Version)
   - Pessimistic locking
   - Redis distributed lock
3. Race condition 가능 경로 분석

## Pass Criteria
- 동시 쓰기 시나리오에 적절한 locking 존재
- Lost update 방지 메커니즘 확인
```

Create `skills/review/implementation/skillsets/nfr-anti-pattern-scan.md`:
```markdown
# NFR Anti-Pattern Scan

## Procedure
1. N+1 쿼리 패턴 탐지 (loop 내 DB 조회)
2. 무제한 리스트 반환 (페이지네이션 없음)
3. 동기 호출 체인이 과도하게 긴 경우
4. 캐시 미적용 빈번 조회
5. 트랜잭션 범위가 과도하게 넓은 경우

## Pass Criteria
- 위 안티패턴 없음 또는 의도적 사유 명시
```

- [ ] **Step 7: Create usecase skillsets**

Create `skills/review/usecase/skillsets/ac-to-scenario-traceability.md`:
```markdown
# AC to Scenario Traceability

## Procedure
1. Spec의 User Story별 Acceptance Criteria 추출
2. 각 AC에 대응하는 시나리오(main/alt/exception flow) 매핑
3. 시나리오 없는 AC, AC 없는 시나리오를 gap으로 보고
4. 매트릭스 출력

## Pass Criteria
- AC ↔ 시나리오 1:N 매핑 완전
- 고아 AC/시나리오 없음
```

Create `skills/review/usecase/skillsets/exception-edge-case-expansion.md`:
```markdown
# Exception & Edge Case Expansion

## Procedure
1. Spec의 정상 흐름에서 실패 가능 지점 식별
2. 각 지점에 예외/에지 케이스가 명시되어 있는지 확인
3. 누락된 예외 시나리오 제안:
   - 네트워크 실패, 타임아웃
   - 데이터 불일치, 부분 실패
   - 권한 부족, 인증 만료
4. 리커버리 전략 존재 여부 확인

## Pass Criteria
- 주요 실패 지점에 예외 처리 명시
- 리커버리 또는 롤백 전략 존재
```

- [ ] **Step 8: Update `commands/spec-review.md` for 5 dimensions**

Modify the existing file to add domain and test-strategy reviewers:

```markdown
---
name: spec-review
description: "Multi-perspective spec review: architecture, implementation, usecase, domain, test-strategy"
requires: []
auto_reference: true
---

# /hnsf:spec-review

## Purpose
Review a spec from 5 perspectives to catch issues before implementation.

## Required Inputs
- Spec folder with spec.md

## Expected Outputs
- `context/engineer-review-{type}.md` per reviewer (5 files)
- Overall verdict

---

## PHASE 1: Resolve Spec

1. Resolve spec folder (user-provided or most recent)
2. Read spec.md

## PHASE 2: Run Reviews

Execute 5 reviewers sequentially. Each applies the Seed Discovery Protocol from `@references/review-protocol.md`.

### Review 1: Architecture
Load `harness-scaffold:review-architecture` skill.
Focus: layer separation, dependency direction, module boundaries, patterns.

### Review 2: Domain
Load `harness-scaffold:review-domain` skill.
Focus: bounded contexts, ubiquitous language, aggregate invariants.

### Review 3: Implementation
Load `harness-scaffold:review-implementation` skill.
Focus: feasibility, code conflicts, complexity, NFR anti-patterns.

### Review 4: Test Strategy
Load `harness-scaffold:review-test-strategy` skill.
Focus: AC→test derivation, test layer assignment, mock boundaries.

### Review 5: Usecase
Load `harness-scaffold:review-usecase` skill.
Focus: actor-goal pairs, flows, AC traceability, edge cases.

## PHASE 3: Verdict Progression

- If any reviewer returns **BLOCK** → halt remaining reviews → report
- If **REVISE** → continue remaining reviews → collect all issues
- If all **SHIP** → proceed

## PHASE 4: Summary

Output verdict table:
```
| Reviewer | Verdict | Issues |
|----------|---------|--------|
| Architecture | SHIP | 0 |
| Domain | SHIP | 0 |
| Implementation | REVISE | 2 |
| Test Strategy | SHIP | 0 |
| Usecase | SHIP | 0 |

Overall: REVISE
Action: Address implementation issues, then re-review
```

Save individual reports to `context/engineer-review-{type}.md`.

## Mode Behavior
- **Quality mode**: Run all 5 reviewers always
- **Efficient mode**: Ask user which reviewers to run
```

- [ ] **Step 9: Commit**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai
git add plugins/harness-scaffold/skills/review/ plugins/harness-scaffold/commands/spec-review.md
git commit -m "feat(harness-v2): expand review to 5 dimensions with skillset procedures"
```

---

## Task 5: Lifecycle Layer — Skills + Commands + Agents

GC, Evolve, Diet, Audit 스킬/커맨드/에이전트 생성.

**Files:**
- Create: `skills/lifecycle/gc/SKILL.md`
- Create: `skills/lifecycle/evolve/SKILL.md`
- Create: `skills/lifecycle/diet/SKILL.md`
- Create: `skills/lifecycle/audit/SKILL.md`
- Create: `commands/harness-gc.md`
- Create: `commands/harness-evolve.md`
- Create: `commands/harness-diet.md`
- Create: `commands/harness-audit.md`
- Create: `agents/gc-agent.md`
- Create: `agents/harness-auditor.md`

- [ ] **Step 1: Create `skills/lifecycle/gc/SKILL.md`**

```markdown
---
name: gc
description: Use when performing garbage collection on the project — detects dead code, doc drift, rule violations, stale harness rules
---

# Garbage Collection

## Protocol
Follow `@references/gc-protocol.md` for scan modes and report format.

## Scan Checklist
- [ ] Dead code: 미사용 import, 빈 파일, 호출 없는 public 함수
- [ ] Doc drift: CLAUDE.md/docs 내용 vs 실제 코드 괴리
- [ ] Rule violation: agent-os/standards/ 규칙 vs 코드 위반
- [ ] Stale harness: 불필요한 규칙/스킬/훅 (→ diet 연계)

## Auto-fix Policy
- Dead imports → auto-remove (사용자 확인 불필요)
- Doc path typos → auto-correct
- 나머지 → 사용자 확인 필요

## Output
`harness-gc-report.md` in project root (overwritten each run)

## NEVER
- Auto-fix rule violations without user approval
- Delete files without explicit user confirmation
- Run full scan in light mode (light = changed files only)
```

- [ ] **Step 2: Create `skills/lifecycle/evolve/SKILL.md`**

```markdown
---
name: evolve
description: Use when a failure pattern is detected and needs to be encoded as a new harness rule to prevent recurrence
---

# Harness Evolution

## Trigger Sources
- 테스트 실패 (Ralph Loop 기록)
- spec-review BLOCK 판정
- Ralph Loop 3회 초과
- verify 실패
- 사용자 피드백 ("이거 하지 마")

## Classification → Target

| Failure Type | Target |
|-------------|--------|
| 코딩 실수 (반복 패턴) | lint rule 또는 hook enforcement 추가 |
| 아키텍처 위반 | CLAUDE.md constraint 추가 |
| 스펙 부족/모호 | review skillset 강화 |
| 도구 오용 | agent-behavior 규칙 추가 |

## Process
1. 실패 패턴을 사용자에게 설명
2. 분류 제안 → 사용자 확인
3. 적절한 하네스 계층에 규칙 생성
4. `docs/changelog/harness-changelog.md`에 기록:
   `[date] [evolve] [변경 내용] [근거: {failure description}]`

## NEVER
- 사용자 확인 없이 CLAUDE.md 수정
- 검증 안 된 패턴을 규칙으로 추가
- 한 번의 실패로 과도한 규칙 추가 (최소한의 제약)
```

- [ ] **Step 3: Create `skills/lifecycle/diet/SKILL.md`**

```markdown
---
name: diet
description: Use when reviewing harness complexity to remove unnecessary rules — models improve, harness should simplify
---

# Harness Diet

## Philosophy
See `@references/diet-criteria.md` and `docs/philosophy/bitter-lesson.md`.

## Process
1. **Measure**: 하네스 토큰 수 측정
   - CLAUDE.md
   - skills/ 전체
   - agents/ 전체
   - hooks/ 전체
   - templates/ 전체

2. **Identify**: 감량 후보 식별
   - `@references/diet-criteria.md` 기준 적용
   - changelog에서 각 규칙의 마지막 트리거 일자 확인

3. **Propose**: 후보 목록을 사용자에게 제시
   - 각 후보의 현재 역할
   - 제거 시 예상 영향
   - 제거 근거

4. **Execute**: 사용자 승인된 항목만 제거/아카이브

5. **Record**: changelog에 기록:
   `[date] [diet] [removed: {rule}] [reason: {criterion}]`

## Protected Items (절대 제거 불가)
- CLAUDE.md
- core/session
- core/compaction
- references/harness-philosophy.md

## NEVER
- 사용자 승인 없이 규칙 제거
- protected items 제거 제안
```

- [ ] **Step 4: Create `skills/lifecycle/audit/SKILL.md`**

```markdown
---
name: audit
description: Use when comparing current harness against external benchmarks — repos, posts, best practices
---

# Harness Audit

## Process
1. **Source**: 외부 소스 지정 (URL, repo path, or "자동 검색")
   - 레포: 해당 프로젝트의 CLAUDE.md/AGENTS.md/.claude/ 구조 분석
   - 포스트: 하네스 엔지니어링 관련 내용 추출
   - 자동: 최신 하네스 엔지니어링 트렌드 웹 검색

2. **Compare**: 현재 harness-scaffold 구조와 비교
   - 있는데 우리에겐 없는 패턴
   - 우리에겐 있는데 다른 곳엔 없는 패턴 (과잉?)
   - 구조적 차이점

3. **Report**: `docs/benchmarks/YYYY-MM-DD-{source-name}.md` 생성
   - 비교 요약
   - 채택 권장 항목
   - 미채택 사유

4. **Adopt**: 사용자가 채택 결정 → `harness-evolve`로 반영

## NEVER
- 자동으로 외부 패턴 적용 (항상 사용자 결정)
- 비교 없이 "좋아 보이니까" 추가
```

- [ ] **Step 5: Create `commands/harness-gc.md`**

```markdown
---
name: harness-gc
description: "Run garbage collection — detect dead code, doc drift, rule violations, stale harness"
requires:
  - agent-os/standards/global/conventions.md
auto_reference: true
---

# /hnsf:harness-gc

## Purpose
프로젝트의 코드/문서/하네스를 청소한다.

## Required Inputs
- Access to project root

## Expected Outputs
- harness-gc-report.md

---

## Execution

1. Load `harness-scaffold:gc` skill
2. Delegate to `harness-scaffold:gc-agent`
3. Agent performs full scan per `@references/gc-protocol.md`
4. Report generated at project root
5. User reviews and approves auto-fixes
```

- [ ] **Step 6: Create `commands/harness-evolve.md`**

```markdown
---
name: harness-evolve
description: "Encode a failure pattern as a new harness rule to prevent recurrence"
requires: []
auto_reference: false
---

# /hnsf:harness-evolve

## Purpose
실패 패턴을 하네스 규칙으로 인코딩하여 재발 방지.

## Required Inputs
- Failure description (user provides or detected from recent session)

## Expected Outputs
- New rule added to appropriate harness layer
- Entry in docs/changelog/harness-changelog.md

---

## Execution

1. Load `harness-scaffold:evolve` skill
2. Ask user to describe the failure (or detect from recent session)
3. Classify failure type
4. Propose rule addition with target location
5. User approves → create rule → record changelog
```

- [ ] **Step 7: Create `commands/harness-diet.md`**

```markdown
---
name: harness-diet
description: "Review harness complexity and remove unnecessary rules — Bitter Lesson applied"
requires: []
auto_reference: false
---

# /hnsf:harness-diet

## Purpose
하네스 복잡도를 점검하고 불필요한 규칙을 제거한다.

## Required Inputs
- Access to harness files (CLAUDE.md, skills/, agents/, hooks/)

## Expected Outputs
- Diet proposal (candidate list)
- Updated harness (after user approval)
- Entry in docs/changelog/harness-changelog.md

---

## Execution

1. Load `harness-scaffold:diet` skill
2. Measure current harness token count
3. Apply `@references/diet-criteria.md`
4. Present candidates to user
5. User selects items to remove → execute → record changelog
```

- [ ] **Step 8: Create `commands/harness-audit.md`**

```markdown
---
name: harness-audit
description: "Compare current harness against external benchmarks — repos, posts, best practices"
requires: []
auto_reference: false
---

# /hnsf:harness-audit

## Purpose
외부 소스와 비교하여 하네스 개선 기회를 식별한다.

## Required Inputs
- External source (URL, repo path, or "auto" for web search)

## Expected Outputs
- docs/benchmarks/YYYY-MM-DD-{source}.md

---

## Execution

1. Load `harness-scaffold:audit` skill
2. Ask user for source (or use "auto" for web search)
3. Analyze source's harness structure
4. Compare with current harness-scaffold
5. Generate benchmark report
6. User decides adoption → delegate to `/hnsf:harness-evolve`
```

- [ ] **Step 9: Create `agents/gc-agent.md`**

```markdown
---
name: gc-agent
description: Garbage collection agent — scans project for dead code, doc drift, rule violations, stale harness
tools: Read, Grep, Glob, Bash, Write
model: inherit
---

# GC Agent

당신은 가비지 컬렉션 에이전트입니다.
프로젝트의 코드, 문서, 하네스 규칙을 청소합니다.

## 실행 순서

### 1. CLAUDE.md 읽기
프로젝트의 CLAUDE.md를 읽어 모듈 구조, 규칙, 컨벤션을 파악.

### 2. Dead Code 탐지
- Glob으로 빈 파일 탐지
- Grep으로 미사용 import 탐지 (언어별)
- 호출 없는 public 함수 식별

### 3. Doc Drift 탐지
- CLAUDE.md에 나열된 모듈/경로가 실제로 존재하는지 확인
- docs/ 내 경로 참조가 유효한지 확인

### 4. Rule Violation 탐지
- agent-os/standards/의 규칙을 읽고 코드에서 위반 사례 탐지
- 아키텍처 제약 (의존 방향, 패키지 구조) 확인

### 5. Stale Harness 탐지
- docs/changelog/harness-changelog.md에서 각 규칙의 마지막 트리거 확인
- 3개월 이상 미트리거 규칙 식별

### 6. 보고서 작성
harness-gc-report.md를 프로젝트 루트에 작성.

## 제약
- Auto-fix는 dead imports와 doc path typos만
- 나머지는 보고만 (사용자 확인 필요)
```

- [ ] **Step 10: Create `agents/harness-auditor.md`**

```markdown
---
name: harness-auditor
description: Harness audit agent — compares current harness with external sources
tools: Read, Grep, Glob, WebFetch, WebSearch, Write
model: inherit
---

# Harness Auditor Agent

당신은 하네스 벤치마크 에이전트입니다.
외부 소스의 하네스 구조를 분석하고 현재 harness-scaffold와 비교합니다.

## 실행 순서

### 1. 소스 수집
- URL → WebFetch로 내용 수집
- 로컬 레포 → Read/Glob으로 .claude/, CLAUDE.md, AGENTS.md 분석
- 자동 → WebSearch로 최신 하네스 엔지니어링 포스트 검색

### 2. 구조 분석
- 컨텍스트 파일 구조 (CLAUDE.md, AGENTS.md, docs/)
- 자동 강제 체계 (hooks, CI gates, linters)
- 진화 메커니즘 (GC, feedback loop)
- 스킬/에이전트/커맨드 구조

### 3. 비교
현재 harness-scaffold와 항목별 비교 매트릭스 생성.

### 4. 보고서
docs/benchmarks/YYYY-MM-DD-{source}.md 작성.
```

- [ ] **Step 11: Commit**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai
git add plugins/harness-scaffold/skills/lifecycle/ plugins/harness-scaffold/commands/harness-*.md plugins/harness-scaffold/agents/gc-agent.md plugins/harness-scaffold/agents/harness-auditor.md
git commit -m "feat(harness-v2): add Lifecycle layer — GC, evolve, diet, audit"
```

---

## Task 6: New SDD Commands — spec-pipeline + verify-crosscheck

**Files:**
- Create: `commands/spec-pipeline.md`
- Create: `commands/verify-crosscheck.md`

- [ ] **Step 1: Create `commands/spec-pipeline.md`**

```markdown
---
name: spec-pipeline
description: "End-to-end spec pipeline: shape → write → review → create-tasks"
requires:
  - agent-os/product/mission.md
  - agent-os/product/tech-stack.md
auto_reference: true
---

# /hnsf:spec-pipeline

## Purpose
shape-spec → write-spec → spec-review → create-tasks를 한 번에 실행하는 통합 파이프라인.

## Required Inputs
- Feature description (user provides)

## Expected Outputs
- docs/specs/{date}-{name}/
  - planning/requirements.md
  - planning/test-quality.md
  - spec.md
  - context/engineer-review-*.md (5 files)
  - tasks.md
  - open-questions.yml

---

## PHASE 0: Context Loading

1. Read docs/index.yml (if exists) for auto-reference
2. Read agent-os/product/mission.md
3. Read agent-os/product/tech-stack.md

## PHASE 1: Shape Spec

Delegate to `/hnsf:shape-spec` flow:
1. spec-initializer → create spec folder
2. spec-shaper → requirements.md
3. Build test strategy → test-quality.md
4. Seed open-questions.yml

## PHASE 2: Write Spec

Delegate to `/hnsf:write-spec` flow:
1. Load open-questions context
2. spec-writer → spec.md

## PHASE 2.5: Open Questions Update

Update open-questions.yml with any new unknowns from spec writing.

## PHASE 3: Spec Review (5-Dimension)

Delegate to `/hnsf:spec-review` flow:
1. Run 5 reviewers sequentially
2. If BLOCK → return to PHASE 2 with feedback (max 2 iterations)
3. If REVISE → auto-revise spec.md (max 2 iterations)
4. If all SHIP → proceed

## PHASE 4: Create Tasks

Delegate to `/hnsf:create-tasks` flow:
1. tasks-list-creator → tasks.md

## PHASE 5: User Approval Gate

Present pipeline results summary:
```
Pipeline complete for: {feature-name}

Artifacts:
- requirements.md ✓
- spec.md ✓ (reviewed, {verdict})
- tasks.md ✓ ({N} task groups)
- open-questions.yml ({M} open, {K} closed)

Review the spec folder and approve to proceed with implementation.
```

Wait for user approval before suggesting `/hnsf:implement-tasks`.
```

- [ ] **Step 2: Create `commands/verify-crosscheck.md`**

```markdown
---
name: verify-crosscheck
description: "6-layer cross-consistency verification: docs ↔ code ↔ specs ↔ tasks"
requires:
  - agent-os/standards/global/conventions.md
auto_reference: true
---

# /hnsf:verify-crosscheck

## Purpose
프로젝트의 문서, 스펙, 태스크, 코드 간 교차 일관성을 6개 레이어에서 검증.

## Required Inputs
- docs/ directory
- agent-os/ directory (if exists)
- docs/specs/{feature}/ (if checking specific feature)

## Expected Outputs
- CROSSCHECK_REPORT.md in spec folder or project root

---

## Layer 1: SOT Internal Consistency

docs/ 내 문서들 간 모순 체크:
- docs/index.md에 나열된 문서가 실제로 존재하는지
- docs 내 상호 참조 링크가 유효한지
- CLAUDE.md와 docs/architecture/overview.md 간 모듈 목록 일치

## Layer 2: docs ↔ agent-os Sync

- agent-os/standards/의 규칙이 CLAUDE.md에도 반영되어 있는지
- agent-os/product/tech-stack.md와 CLAUDE.md 빌드 명령 일치
- agent-os/config.yml 설정과 실제 파일 구조 일치

## Layer 3: Product ↔ Specs

- agent-os/product/mission.md의 목표가 spec에 반영되어 있는지
- 스펙이 미션과 무관한 범위를 포함하지 않는지

## Layer 4: Standards ↔ Specs

- agent-os/standards/의 코딩 규칙이 spec의 기술 결정과 충돌하지 않는지
- spec에서 표준을 위반하는 결정이 있으면 ADR 존재 여부 확인

## Layer 5: Specs ↔ Tasks

- spec.md의 모든 SR(Specific Requirement)에 대응하는 task가 있는지
- tasks.md에 spec에 없는 과잉 task가 없는지
- AC → task 매핑 완전성

## Layer 6: Tasks ↔ Code

- tasks.md에서 완료 표시된 task의 실제 구현 존재 여부
- 미완료 task에 대응하는 코드가 이미 존재하지 않는지
- 코드 변경이 task에 매핑되지 않는 경우 탐지

## Output

```markdown
# Crosscheck Report — {date}

| Layer | Status | Issues |
|-------|--------|--------|
| 1. SOT Internal | PASS | 0 |
| 2. docs ↔ agent-os | WARN | 1 |
| 3. Product ↔ Specs | PASS | 0 |
| 4. Standards ↔ Specs | PASS | 0 |
| 5. Specs ↔ Tasks | FAIL | 2 |
| 6. Tasks ↔ Code | PASS | 0 |

Overall: FAIL

## Details
### Layer 2: docs ↔ agent-os
- ⚠ tech-stack.md lists Java 25 but CLAUDE.md says Java 21

### Layer 5: Specs ↔ Tasks
- ✗ SR-003 has no corresponding task
- ✗ Task Group 4 has no spec reference
```
```

- [ ] **Step 3: Commit**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai
git add plugins/harness-scaffold/commands/spec-pipeline.md plugins/harness-scaffold/commands/verify-crosscheck.md
git commit -m "feat(harness-v2): add spec-pipeline and verify-crosscheck commands"
```

---

## Task 7: Enforcement Hooks + Context Routing Template

**Files:**
- Rename: `templates/hooks/hnsf-automation.json` → `templates/hooks/hnsf-hooks-reminder.json`
- Create: `templates/hooks/hnsf-hooks-feedback.json`
- Create: `templates/hooks/hnsf-hooks-enforcement.json`
- Create: `templates/docs-index.yml`

- [ ] **Step 1: Rename existing hook template**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai/plugins/harness-scaffold
mv templates/hooks/hnsf-automation.json templates/hooks/hnsf-hooks-reminder.json
```

- [ ] **Step 2: Create `templates/hooks/hnsf-hooks-feedback.json`**

```json
{
  "description": "harness-scaffold feedback hooks — lint/compile checks, failure feedback (no blocking)",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "pattern": "**/*.kt",
        "hooks": [
          {
            "type": "command",
            "command": "ktlint --relative . 2>&1 | tail -5",
            "onSuccess": "silent",
            "onFailure": "feedback",
            "message": "Lint violations found — please fix"
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "pattern": "**/*.ts",
        "hooks": [
          {
            "type": "command",
            "command": "npx eslint --quiet 2>&1 | tail -5",
            "onSuccess": "silent",
            "onFailure": "feedback",
            "message": "ESLint violations found — please fix"
          }
        ]
      },
      {
        "matcher": "Write",
        "pattern": "**/spec.md",
        "hooks": [
          {
            "type": "reminder",
            "message": "Spec Checklist:\n  [ ] Overview 30s readable?\n  [ ] Sections independent?\n  [ ] open-questions.yml updated?\n  [ ] Under 400 lines?"
          }
        ]
      },
      {
        "matcher": "Write",
        "pattern": "**/tasks.md",
        "hooks": [
          {
            "type": "reminder",
            "message": "Tasks Checklist:\n  [ ] Dependencies specified?\n  [ ] Verification sub-tasks?\n  [ ] phase + required_skills metadata?\n  [ ] Under 600 lines?"
          }
        ]
      }
    ],
    "PrePrompt": [
      {
        "matcher": "Always",
        "hooks": [
          {
            "type": "reminder",
            "condition": "context.usage > 0.75",
            "message": "Context 75% — Consider strategic compaction at next task completion"
          },
          {
            "type": "reminder",
            "condition": "context.usage > 0.90",
            "message": "Context 90% — Compaction recommended (run Pre-Compact checklist)"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Create `templates/hooks/hnsf-hooks-enforcement.json`**

```json
{
  "description": "harness-scaffold enforcement hooks — compile/lint failures block actions",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "pattern": "git commit*",
        "hooks": [
          {
            "type": "command",
            "command": "{{COMPILE_COMMAND}}",
            "onFailure": "block",
            "message": "Compile failed — commit blocked. Fix compilation errors first."
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "pattern": "{{SOURCE_GLOB}}",
        "hooks": [
          {
            "type": "command",
            "command": "{{LINT_COMMAND}}",
            "onSuccess": "silent",
            "onFailure": "feedback",
            "message": "Lint violations found — please fix before continuing"
          }
        ]
      },
      {
        "matcher": "Write",
        "pattern": "**/spec.md",
        "hooks": [
          {
            "type": "reminder",
            "message": "Spec Checklist:\n  [ ] Overview 30s readable?\n  [ ] Sections independent?\n  [ ] open-questions.yml updated?\n  [ ] Under 400 lines?"
          }
        ]
      },
      {
        "matcher": "Write",
        "pattern": "**/tasks.md",
        "hooks": [
          {
            "type": "reminder",
            "message": "Tasks Checklist:\n  [ ] Dependencies specified?\n  [ ] Verification sub-tasks?\n  [ ] phase + required_skills metadata?\n  [ ] Under 600 lines?"
          }
        ]
      }
    ],
    "PrePrompt": [
      {
        "matcher": "Always",
        "hooks": [
          {
            "type": "reminder",
            "condition": "context.usage > 0.75",
            "message": "Context 75% — Consider strategic compaction at next task completion"
          },
          {
            "type": "reminder",
            "condition": "context.usage > 0.90",
            "message": "Context 90% — COMPACTION REQUIRED (run Pre-Compact checklist NOW)"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 4: Create `templates/docs-index.yml`**

```yaml
# Context Routing Map Template
# Replace {{PLACEHOLDER}} values during /hnsf:init
schema_version: 1

entries:
  - id: architecture
    path: docs/architecture/overview.md
    keywords: [architecture, layer, dependency, port, adapter, clean-architecture, module]

  - id: conventions
    path: agent-os/standards/global/conventions.md
    keywords: [convention, naming, style, format, coding-standard]

  - id: test-rules
    path: agent-os/standards/global/conventions.md
    section: "## Test"
    keywords: [test, testing, mock, bdd, spec, assertion]

  - id: mission
    path: agent-os/product/mission.md
    keywords: [mission, vision, goal, purpose, product]

  - id: tech-stack
    path: agent-os/product/tech-stack.md
    keywords: [build, gradle, maven, npm, dependency, version, toolchain]

  - id: harness-philosophy
    path: docs/philosophy/three-pillars.md
    keywords: [harness, gc, enforcement, evolution, diet, pillar]

auto_reference:
  threshold: 2
  max_docs: 3
  prefer_section: true
```

- [ ] **Step 5: Commit**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai
git add plugins/harness-scaffold/templates/hooks/ plugins/harness-scaffold/templates/docs-index.yml
git commit -m "feat(harness-v2): add enforcement hooks (3-tier) and context routing template"
```

---

## Task 8: Update Core — Session Routing + Init Extension + plugin.json

**Files:**
- Modify: `skills/core/session/SKILL.md` (add context routing)
- Modify: `commands/init.md` (add Phase 3-5 for doc-gen, hooks, index.yml)
- Modify: `.claude-plugin/plugin.json` (add 9 new commands)

- [ ] **Step 1: Update `skills/core/session/SKILL.md`**

Replace entire content:

```markdown
---
name: session
description: Use when starting a new session or recovering from compaction to load project context and key decisions
---

# Session Management

## Context Routing

### Level 0: Always Load
1. Read CLAUDE.md

### Level 1: Command-Specific
Each command declares `requires:` in frontmatter → load those files.

### Level 2: Keyword Matching
If `docs/index.yml` exists and command has `auto_reference: true`:
1. Extract keywords from current task description
2. Match against index.yml entries (threshold: 2+ keywords)
3. Load top 3 matched documents (prefer_section if available)
4. Load silently (no user notification)

## Session Start
1. Level 0: Read CLAUDE.md
2. Read agent-os/product/mission.md (if exists)
3. Check latest spec status in docs/specs/
4. Load active task context from tasks.md

## Post-Compaction Recovery
1. Level 0: Read CLAUDE.md
2. Read key-decisions.md
3. Read open-questions.yml
4. Check tasks.md checkboxes
5. git log recent commits

## Session End
- Ensure all changes committed
- Update status.md if applicable
```

- [ ] **Step 2: Update `commands/init.md`**

Replace entire content:

```markdown
---
name: init
description: "Initialize AI harness for any project — auto-scan + interactive setup + doc-gen + hooks + routing"
---

# /hnsf:init

Use the `harness-scaffold:session` skill context for this command.

## Purpose
Set up a complete AI harness environment for the current project.

## Required Inputs
- Access to project root directory

## Expected Outputs
- CLAUDE.md (project-customized)
- PLANS.md
- agent-os/ directory tree
- docs/ directory tree (architecture, adr, index)
- docs/index.yml (context routing map)
- .claude/hooks/ (selected tier)
- .claude/COMPACTION-GUIDE.md
- docs/specs/ directory
- (Optional) .claude/scripts/parallel-work.sh

---

## PHASE 1: Auto Scan

Analyze the project root to build a profile:

1. **Language/Framework**: Check build files
   - `build.gradle.kts` / `build.gradle` → Java/Kotlin + Gradle
   - `pom.xml` → Java + Maven
   - `package.json` → Node.js (check for TS, framework)
   - `pyproject.toml` / `requirements.txt` → Python
   - `go.mod` → Go
   - `Cargo.toml` → Rust

2. **Module Structure**: Check for monorepo/multi-module
   - `settings.gradle.kts` includes → multi-module
   - `workspaces` in package.json → monorepo
   - Multiple `*/src/main` patterns → multi-service

3. **Test Framework**: Detect from dependencies

4. **Existing AI Settings**: Check for `.claude/`, `CLAUDE.md`, `AGENTS.md`, `docs/`

5. **Build/Test Commands**: Extract from build config

Present scan results to user.

## PHASE 2: Interactive Setup (3-5 questions)

**Q1**: "프로젝트 프로파일이 맞나요?" + [scan results summary]
**Q2**: "아키텍처 패턴은?" (Clean Architecture / Layered / Monolith / Microservice / Other)
**Q3**: (If CLAUDE.md exists) "기존 CLAUDE.md와 병합할까요, 새로 만들까요?"
**Q4**: "모드 선택 — 품질 모드(기본) / 효율 모드(토큰 절약)?"
**Q5**: "병렬 실행(git worktree) 지원이 필요한가요?"

## PHASE 3: Doc Generation

Delegate to `harness-scaffold:doc-gen` skill:
1. Select CLAUDE.md template based on language/framework
2. Generate CLAUDE.md with scan results + user answers
3. Generate docs/ tree (index.md, architecture/, adr/, plans/)
4. Run `harness-scaffold:doc-validate` for validation

## PHASE 4: Hook Tier Selection

Ask user:
```
프로젝트에 적용할 훅 수준을 선택하세요:
  (A) Light  — 리마인더만 (신규 프로젝트, 탐색 단계)
  (B) Medium — 린트/컴파일 피드백 (개발 진행 중)
  (C) Strict — 실패 시 차단 (안정 운영 단계)
```

Copy selected template from `templates/hooks/hnsf-hooks-{tier}.json` to `.claude/hooks/`.

## PHASE 5: Context Routing Setup

1. Copy `templates/docs-index.yml` → `docs/index.yml`
2. Replace placeholders with scan results
3. Add project-specific entries based on detected structure

## PHASE 6: Generate Remaining Files

Using templates, generate:
- `PLANS.md` — from `templates/plans-md.md`
- `agent-os/config.yml` — mode + layer settings
- `agent-os/product/mission.md` — from user input
- `agent-os/product/tech-stack.md` — from scan results
- `agent-os/standards/agent-behavior/` — all 6 files
- `agent-os/standards/global/conventions.md` — from scan + user input
- `.claude/COMPACTION-GUIDE.md` — from template
- `docs/specs/` — empty directory
- (Conditional) `.claude/scripts/parallel-work.sh`

## PHASE 7: Idempotency Check

For each file:
- If not exists → create
- If exists and identical → skip
- If exists and different → show diff → ask: merge / skip / overwrite

## Completion

```
AI harness initialized for [project-name]!

Generated:
- CLAUDE.md (project configuration)
- PLANS.md (execution plan rules)
- agent-os/ (standards, product, config)
- docs/ (architecture, adr, index, routing)
- .claude/hooks/ ({tier} tier)
- docs/specs/ (SDD spec directory)

Harness philosophy: docs/philosophy/
Context routing: docs/index.yml

Next: Use /hnsf:shape-spec to start your first feature spec.
      Use /hnsf:harness-audit to compare with external benchmarks.
```
```

- [ ] **Step 3: Update `.claude-plugin/plugin.json`**

```json
{
  "name": "harness-scaffold",
  "description": "Universal AI harness engineering: 6-layer architecture with SDD pipeline, 5-dimension review, lifecycle (GC/evolve/diet/audit), enforcement hooks, context routing, and doc generation",
  "version": "0.2.0",
  "author": { "name": "gideok-kwon" },
  "license": "MIT",
  "keywords": ["harness", "sdd", "agent-os", "scaffolding", "spec-driven", "ai-harness", "gc", "enforcement", "evolution"],
  "commands": [
    "./commands/init.md",
    "./commands/shape-spec.md",
    "./commands/write-spec.md",
    "./commands/spec-pipeline.md",
    "./commands/spec-review.md",
    "./commands/create-tasks.md",
    "./commands/implement-tasks.md",
    "./commands/orchestrate-tasks.md",
    "./commands/interview-capture.md",
    "./commands/drift-check.md",
    "./commands/verify.md",
    "./commands/verify-crosscheck.md",
    "./commands/doc-gen.md",
    "./commands/doc-validate.md",
    "./commands/doc-html.md",
    "./commands/harness-gc.md",
    "./commands/harness-evolve.md",
    "./commands/harness-diet.md",
    "./commands/harness-audit.md"
  ]
}
```

- [ ] **Step 4: Commit**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai
git add plugins/harness-scaffold/skills/core/session/SKILL.md plugins/harness-scaffold/commands/init.md plugins/harness-scaffold/.claude-plugin/plugin.json
git commit -m "feat(harness-v2): update core session routing, extend init, bump to v0.2.0"
```

---

## Task 9: Final — Push + msa Submodule Update + Verify

**Files:**
- No new files

- [ ] **Step 1: Verify all files exist**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai/plugins/harness-scaffold
# Check new file counts
find skills/docs -name "*.md" | wc -l          # expect 3
find skills/lifecycle -name "*.md" | wc -l      # expect 4
find skills/review/domain -name "*.md" | wc -l  # expect 4
find skills/review/test-strategy -name "*.md" | wc -l  # expect 4
find skills/review/*/skillsets -name "*.md" | wc -l     # expect 14
find commands -name "*.md" | wc -l              # expect 19
find agents -name "*.md" | wc -l                # expect 10 (including existing)
find docs/philosophy -name "*.md" | wc -l       # expect 4
find docs/decisions -name "*.md" | wc -l        # expect 3
find references -name "*.md" | wc -l            # expect 6
```

- [ ] **Step 2: Push ai repo**

```bash
cd /Users/gideok-kwon/IdeaProjects/ai
git push origin main
```

- [ ] **Step 3: Update msa submodule**

```bash
cd /Users/gideok-kwon/IdeaProjects/msa/ai
git pull origin main
cd /Users/gideok-kwon/IdeaProjects/msa
git add ai
git commit -m "chore: update ai submodule to harness-scaffold v0.2.0"
```

- [ ] **Step 4: Remove doc-scaffolding from msa settings**

Edit `/Users/gideok-kwon/IdeaProjects/msa/.claude/settings.json`:
Remove `"doc-scaffolding@ai-common": true` line.

- [ ] **Step 5: Verify plugin loads**

Run `/hnsf:init` in a test context to verify the plugin is recognized with all 19 commands.
