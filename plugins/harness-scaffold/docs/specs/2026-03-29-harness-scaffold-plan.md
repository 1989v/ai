# harness-scaffold (hnsf) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** mrt3-order의 검증된 AI 하네스 엔지니어링을 범용 Claude Code 플러그인으로 구현

**Architecture:** 단일 플러그인 내 4-Layer 모듈 구조 (Core/SDD/Review/Project-Adaptive). 각 레이어는 skills/, commands/, agents/로 구성. 프로젝트 스캔 → 대화형 셋업 → 산출물 생성의 `/harness-scaffold:init` 진입점.

**Tech Stack:** Markdown (commands, skills, agents), JSON (plugin.json, hooks), Bash (parallel-work.sh), YAML (templates)

---

## File Structure

```
plugins/harness-scaffold/
├── .claude-plugin/plugin.json
├── commands/
│   ├── init.md
│   ├── shape-spec.md
│   ├── write-spec.md
│   ├── create-tasks.md
│   ├── implement-tasks.md
│   ├── orchestrate-tasks.md
│   ├── drift-check.md
│   ├── interview-capture.md
│   ├── verify.md
│   └── spec-review.md
├── skills/
│   ├── core/
│   │   ├── agent-behavior/SKILL.md
│   │   ├── compaction/SKILL.md
│   │   ├── spec-evolution/SKILL.md
│   │   └── session/SKILL.md
│   ├── sdd/
│   │   ├── spec-writing/SKILL.md
│   │   ├── task-planning/SKILL.md
│   │   └── implementation/SKILL.md
│   └── review/
│       ├── architecture/SKILL.md
│       ├── implementation/SKILL.md
│       └── usecase/SKILL.md
├── agents/
│   ├── spec-initializer.md
│   ├── spec-shaper.md
│   ├── spec-writer.md
│   ├── tasks-list-creator.md
│   ├── implementer.md
│   ├── tester.md
│   └── verifier.md
├── templates/
│   ├── claude-md/default.md
│   ├── agent-os/config.yml
│   ├── agent-os/product/mission.md
│   ├── agent-os/product/tech-stack.md
│   ├── agent-os/standards/agent-behavior/core-rules.md
│   ├── agent-os/standards/agent-behavior/confirmation.md
│   ├── agent-os/standards/agent-behavior/self-review.md
│   ├── agent-os/standards/agent-behavior/compaction.md
│   ├── agent-os/standards/agent-behavior/session.md
│   ├── agent-os/standards/agent-behavior/doc-gardening.md
│   ├── agent-os/standards/global/conventions.md
│   ├── hooks/hnsf-automation.json
│   ├── specs/spec-template.md
│   ├── specs/tasks-template.md
│   ├── specs/open-questions-template.yml
│   ├── scripts/parallel-work.sh
│   ├── plans-md.md
│   └── compaction-guide.md
└── references/
    ├── command-execution-contract.md
    ├── worktree-protocol.md
    └── review-protocol.md
```

---

## Task Group 1: Plugin Skeleton & Marketplace

**Dependencies:** None
**Phase:** foundation

- [ ] **Step 1: Create plugin.json**

Create: `plugins/harness-scaffold/.claude-plugin/plugin.json`

```json
{
  "name": "harness-scaffold",
  "description": "Universal AI harness scaffolding: SDD pipeline, agent-OS, behavior standards, spec-review, hooks, and parallel execution for any project",
  "version": "0.1.0",
  "author": { "name": "gideok-kwon" },
  "license": "MIT",
  "keywords": ["harness", "sdd", "agent-os", "scaffolding", "spec-driven", "ai-harness"],
  "commands": [
    "./commands/init.md",
    "./commands/shape-spec.md",
    "./commands/write-spec.md",
    "./commands/create-tasks.md",
    "./commands/implement-tasks.md",
    "./commands/orchestrate-tasks.md",
    "./commands/drift-check.md",
    "./commands/interview-capture.md",
    "./commands/verify.md",
    "./commands/spec-review.md"
  ]
}
```

- [ ] **Step 2: Update marketplace.json**

Modify: `.claude-plugin/marketplace.json` — add harness-scaffold entry to plugins array

```json
{
  "name": "harness-scaffold",
  "source": "./plugins/harness-scaffold",
  "description": "Universal AI harness scaffolding: SDD pipeline, agent-OS, behavior standards, spec-review, hooks, and parallel execution for any project"
}
```

- [ ] **Step 3: Create design spec symlink in plugin**

Verify: `plugins/harness-scaffold/docs/specs/2026-03-29-harness-scaffold-design.md` already exists

- [ ] **Step 4: Commit skeleton**

```bash
git add plugins/harness-scaffold/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat(hnsf): add plugin skeleton and marketplace entry"
```

---

## Task Group 2: Templates (Base Layer)

**Dependencies:** Task Group 1
**Phase:** foundation

All templates use `{{PLACEHOLDER}}` syntax for `/harness-scaffold:init` to replace at generation time.

- [ ] **Step 1: Create CLAUDE.md template**

Create: `plugins/harness-scaffold/templates/claude-md/default.md`

```markdown
# CLAUDE.md
# {{PROJECT_NAME}} Project Configuration

---

## Unified Rules

- **AGENTS.md**: Shared baseline navigation (if exists)
- **CLAUDE.md**: Project-specific overrides (this file)
- **PLANS.md**: Complex work orchestration

**On conflict**: CLAUDE.md wins.

---

## Environment

### Build Commands

{{BUILD_COMMANDS}}

### Test Commands

{{TEST_COMMANDS}}

---

## Agent Behavior Standards

코드 수정/생성 작업 시 다음 표준을 적용하세요:

- **리스크 분류 & 검증 루프** → `agent-os/standards/agent-behavior/confirmation.md`
  - Level 1-3 분류, Ralph Loop (BUILD→TEST→FIX, max 3회), Level 3 승인 필수
- **구현 후 리뷰** → `agent-os/standards/agent-behavior/self-review.md`
  - Level 1-2: 자동 lint, Level 3: fresh context reviewer
- **문서 동기화** → `agent-os/standards/agent-behavior/doc-gardening.md`
  - 구현 성공 후 Doc Impact Scan 실행

**범용 행동 원칙**:
- **탐색 우선, 증거 기반** → `agent-os/standards/agent-behavior/core-rules.md`
- **컴팩션 복구** → `agent-os/standards/agent-behavior/compaction.md`
- **세션 관리** → `agent-os/standards/agent-behavior/session.md`

---

## Standards & Conventions

All rules are routed via `agent-os/standards/`.

---

## Active Commands

| Command | Purpose |
|---------|---------|
| `/harness-scaffold:shape-spec` | 요구사항 수집 및 스펙 폴더 초기화 |
| `/harness-scaffold:write-spec` | 스펙 문서 작성 |
| `/harness-scaffold:create-tasks` | 태스크 분해 |
| `/harness-scaffold:implement-tasks` | 구현 (워크트리 옵션) |
| `/harness-scaffold:orchestrate-tasks` | 순차/병렬 오케스트레이션 |
| `/harness-scaffold:drift-check` | 구현-스펙 불일치 감지 |
| `/harness-scaffold:interview-capture` | 구현 전 게이트 인터뷰 |
| `/harness-scaffold:verify` | 검증 (표준→린트→빌드→테스트) |
| `/harness-scaffold:spec-review` | 스펙 리뷰 (architecture/implementation/usecase) |

---

## Navigation Tips

- Feature-specific work → `docs/specs/`
- Standards → `agent-os/standards/`
- Product context → `agent-os/product/`
```

- [ ] **Step 2: Create agent-os templates**

Create the following template files:

`templates/agent-os/config.yml`:
```yaml
# harness-scaffold configuration
mode: {{MODE}}  # quality | efficient
layers:
  core: true
  sdd: true
  review: true
parallel_execution: {{PARALLEL_ENABLED}}
```

`templates/agent-os/product/mission.md`:
```markdown
# {{PROJECT_NAME}} Mission

## Vision
{{PROJECT_DESCRIPTION}}

## Target Users
{{TARGET_USERS}}

## Core Value
{{CORE_VALUE}}
```

`templates/agent-os/product/tech-stack.md`:
```markdown
# Tech Stack

## Language & Framework
{{LANG_FRAMEWORK}}

## Build Tool
{{BUILD_TOOL}}

## Test Framework
{{TEST_FRAMEWORK}}

## Module Structure
{{MODULE_STRUCTURE}}

## Build Commands
{{BUILD_COMMANDS}}

## Test Commands
{{TEST_COMMANDS}}
```

- [ ] **Step 3: Create agent-behavior standard templates**

Create 6 files under `templates/agent-os/standards/agent-behavior/`:

`core-rules.md`:
```markdown
# Core Rules

## Explore First, Evidence Based
- 코드나 문서를 먼저 읽고, 추론하지 말 것
- 가정 대신 증거 기반 접근
- 불확실하면 질문

## Pre-Work Checklist (모든 코드 수정 전)
1. Read `docs/specs/{feature}/context/key-decisions.md` (있을 경우)
2. Read `docs/specs/{feature}/spec.md`
3. Read `docs/specs/{feature}/tasks.md` → confirm current task
4. Check `agent-os/standards/` → matching standard
5. If unclear → ask "Please confirm: [specific question]"
```

`confirmation.md`:
```markdown
# Risk Classification & Confirmation

## Risk Levels

| Level | Task Type | Action |
|-------|-----------|--------|
| **L1** | 리팩토링, 포맷, 주석, 문서 | Auto-proceed + build check |
| **L2** | 신규 파일, 메서드 시그니처, 테스트 추가 | Auto-proceed + Ralph Loop |
| **L3** | 비즈니스 로직, 도메인 개념, 아키텍처 변경 | **WAIT for human approval** |

## Ralph Loop (L2/L3)

```
MAX_RETRIES = 3
LOOP:
  1. BUILD   → fail → FIX
  2. TEST    → pass → EXIT (success)
  3. ANALYZE → identify root cause
  4. FIX     → different approach
  5. ITERATION++ → if >= 3 → EXIT (escalate)
```

Failure Classification:
- **Execution Failure** (Mock 누락, 파싱 오류) → 루프 내 수정
- **Implementation Failure** (404, 500, spec 불일치) → 즉시 STOP

## L3 Approval Request Format
```
## Work Confirmation Request
**Task**: [what]  **Reason**: [why]  **Impact**: [files/features]
**Evidence**: [docs/code referenced]
Proceed?
```
```

`self-review.md`:
```markdown
# Self-Review Protocol

## L1/L2: Automated Review
- 프로젝트 린터 실행 → 위반 시 수정

## L3: Fresh Context Review (품질 모드)
- 서브에이전트로 fresh context reviewer 호출
- git diff + spec + standards만 제공
- 구현 히스토리 제외 (편향 방지)

## L3: Inline Checklist (효율 모드)
- [ ] spec.md 요구사항 전부 반영?
- [ ] 기존 코드 패턴 일관?
- [ ] 에러 핸들링 누락 없음?
- [ ] 테스트 약화/삭제 없음?

## Verdict
- **SHIP** → BUILD 진행
- **REVISE** → 재구현 (max 2회)
- **BLOCK** → 에스컬레이션
```

`compaction.md`:
```markdown
# Compaction Rules

## 컴팩션 실행 권장 시점
- Task Group 완료 시
- Spec 문서 작성 완료 시
- 구현 완료 후 테스트 작성 전
- Phase 전환 시

## 컴팩션 실행 금지 시점
- 구현 도중
- 테스트 디버깅 중
- 중요한 의사결정 논의 중

## Pre-Compact Checklist
- [ ] 현재 작업을 git commit으로 저장
- [ ] 중요 의사결정을 key-decisions.md에 기록
- [ ] 다음 Task 계획 확인
- [ ] 현재 작업이 완전히 종료되었는지 확인

## Post-Compact Recovery
1. CLAUDE.md 읽기
2. key-decisions.md 읽기
3. open-questions.yml 확인
4. tasks.md 체크박스 확인
5. git log 최근 커밋 확인
```

`session.md`:
```markdown
# Session Management

## Session Start
1. Read CLAUDE.md
2. Read agent-os/product/mission.md (있을 경우)
3. Check recent spec status (docs/specs/ 최신 폴더)
4. Load active task context

## Session End
- Ensure all changes committed
- Update status.md if applicable
- Note next steps in tasks.md

## Post-Compaction Recovery
- Follow compaction.md recovery steps
- Ask specific questions if context insufficient
```

`doc-gardening.md`:
```markdown
# Doc Gardening (문서 동기화)

## Doc Impact Scan (구현 성공 후)

```bash
git diff --name-only HEAD
```

변경된 파일 키워드 → agent-os/standards/ 매칭 → 관련 문서 보고

## 동기화 대상
- spec.md ↔ 실제 구현
- tasks.md ↔ 완료 상태
- key-decisions.md ↔ 코드 내 결정

## 원칙
- 구현이 성공한 후에만 문서 동기화
- 문서는 코드의 결과물, 코드가 source of truth
```

- [ ] **Step 4: Create conventions template**

Create: `templates/agent-os/standards/global/conventions.md`

```markdown
# {{PROJECT_NAME}} Conventions

## Architecture
{{ARCHITECTURE_PATTERN}}

## Coding Style
{{CODING_STYLE}}

## Test Conventions
{{TEST_CONVENTIONS}}

## Git Conventions
- Commit messages: conventional commits
- Branch naming: feature/, fix/, chore/
```

- [ ] **Step 5: Create spec/task templates**

`templates/specs/spec-template.md`:
```markdown
# Specification: {{FEATURE_NAME}}

## Goal
[1-2 sentences describing the core objective]

## User Stories
- As a [user type], I want to [action] so that [benefit]

## Specific Requirements

### SR-1: [Requirement Name]
- [Sub-requirement]

## Out of Scope
- [Items explicitly excluded]
```

`templates/specs/tasks-template.md`:
```markdown
# Task Breakdown: {{FEATURE_NAME}}

## Overview
Total Task Groups: [count]

## Task List

### Task Group 1: [Group Name]
**Dependencies:** None
**Phase:** [phase]
**Required Skills:** [skills]

- [ ] 1.0 Complete [group description]
  - [ ] 1.1 [First sub-task]
  - [ ] 1.2 [Second sub-task]
  - [ ] 1.N Verify: [concrete verification command]

**Acceptance Criteria:**
- [Criterion]

## Execution Order
1. Task Group 1
2. Task Group 2 (depends on 1)
```

`templates/specs/open-questions-template.yml`:
```yaml
# Open Questions Registry
# Categories: pre-impl | impl-discovery | test-discovery | closure | waiver-revisit

questions: []
# Example:
#   - id: OQ-001
#     category: pre-impl
#     question: "설명"
#     raised_by: agent-name
#     raised_at: YYYY-MM-DD
#     status: open  # open | resolved | deferred
#     resolution: null
#     resolved_at: null
```

- [ ] **Step 6: Create hooks template**

Create: `templates/hooks/hnsf-automation.json`

```json
{
  "description": "harness-scaffold automation hooks",
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "pattern": "**/spec.md",
        "hooks": [
          {
            "type": "reminder",
            "message": "Spec Checklist:\n  [ ] Overview 30초 읽기 가능?\n  [ ] 섹션 독립적?\n  [ ] open-questions.yml 갱신?\n  [ ] 400줄 이내?"
          }
        ]
      },
      {
        "matcher": "Write",
        "pattern": "**/tasks.md",
        "hooks": [
          {
            "type": "reminder",
            "message": "Tasks Checklist:\n  [ ] 그룹별 dependencies 명시?\n  [ ] 검증 서브태스크 포함?\n  [ ] phase + required_skills 메타데이터?\n  [ ] 600줄 이내?"
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
            "message": "Context 75% - 태스크 완료 시점에 전략적 컴팩션 고려"
          },
          {
            "type": "reminder",
            "condition": "context.usage > 0.90",
            "message": "Context 90% - 즉시 컴팩션 권장 (Pre-Compact 체크리스트 실행)"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 7: Create parallel-work.sh template**

Create: `templates/scripts/parallel-work.sh` — generalized version of mrt3-order's script (same logic, remove project-specific references, use `main` as default base branch instead of `develop`)

- [ ] **Step 8: Create PLANS.md and COMPACTION-GUIDE templates**

`templates/plans-md.md`:
```markdown
# PLANS.md

## ExecPlan Rules

### 사용 조건
- 2단계 이상 작업
- 장시간 작업
- 높은 불확실성 작업

### 필수 구성
- Purpose / Big Picture
- Plan of Work (파일 경로, 변경 포인트 명시)
- Validation (커맨드 및 기대 결과)
- Progress (타임스탬프 체크리스트)
- Decision Log (결정/이유/영향)

### 작성 원칙
- Self-contained (외부 링크 의존 금지)
- 용어 즉시 정의
- 반복 가능한 단계
- 실패/재시도 방법 포함
```

`templates/compaction-guide.md`:
```markdown
# Compaction Guide

## 컴팩션이란?
대화가 길어져 token budget의 64-75%에 도달하면 자동 발생하는 대화 요약.

## 언제 수동 컴팩션?
- Task Group 완료 시
- Spec 문서 작성 완료 시
- Phase 전환 시

## Pre-Compact Checklist
- [ ] git commit
- [ ] key-decisions.md 기록
- [ ] 다음 Task 확인
- [ ] 작업 완전 종료 확인

## Post-Compact Recovery
1. CLAUDE.md 읽기
2. key-decisions.md 읽기
3. tasks.md 체크박스 확인
4. git log 확인
```

- [ ] **Step 9: Commit templates**

```bash
git add plugins/harness-scaffold/templates/
git commit -m "feat(hnsf): add all templates for init scaffolding"
```

---

## Task Group 3: References

**Dependencies:** Task Group 1
**Phase:** foundation

- [ ] **Step 1: Create command-execution-contract.md**

Create: `plugins/harness-scaffold/references/command-execution-contract.md`

Generalized from mrt3-order's version:

```markdown
# Command Execution Contract

## 1) Map-First Structure
- Start with Purpose, Required Inputs, Expected Outputs before steps.
- Keep phase ordering explicit and stable.
- State stop conditions and failure exits before dependent phases.

## 2) Agent Legibility
- Short imperative steps over narrative paragraphs.
- One rule in one place. Reuse shared references.
- Each phase independently understandable.

## 3) Size Discipline
- Target: <= 180 lines per command file.
- Exceed with annotation and extraction candidates.

## 4) Feedback Loop
- Repeating review issues → update source command text.

## 5) Input/Output Contracts per Delegation
- Before subagent call: list required inputs.
- After subagent call: list expected outputs + validation gate.
```

- [ ] **Step 2: Create worktree-protocol.md**

Create: `plugins/harness-scaffold/references/worktree-protocol.md`

```markdown
# Worktree Protocol

Use when worktree isolation is enabled.

## 1) Resolve Project Root
Find nearest dir containing `.claude/scripts/parallel-work.sh`.
If not found, stop with error message.

## 2) Worktree Lifecycle per Task Group
1. Determine base branch: `git branch --show-current`
2. Normalize slug: "Core DTO Changes" → "core-dto-changes"
3. Create: `.claude/scripts/parallel-work.sh create [slug] [base-branch]`
4. Delegate implementation in worktree
5. On completion: `git merge --no-ff [branch-name]`
6. Cleanup: `.claude/scripts/parallel-work.sh remove [slug]`

Merge conflicts → stop and report. No auto-resolution.
```

- [ ] **Step 3: Create review-protocol.md**

Create: `plugins/harness-scaffold/references/review-protocol.md`

```markdown
# Seed Discovery Protocol (Review)

## Stage 1: Seed
Read target spec, classify document type, extract internal references.

## Stage 2: First-Ring Companions
Glob same-directory siblings (tasks*, status*, context/*).
Follow relative Markdown links.

## Stage 3: Index Map Discovery
If docs/index.yml exists → keyword match → load relevant standards.
Fallback: scan agent-os/standards/ directly.

## Stage 4: Code Evidence
Grep/Glob for referenced classes, modules, APIs in codebase.

## Verdict Rules
- SHIP: All checks passed, no issues.
- REVISE: Non-blocking issues, fix or track as risk. Max 2 rounds.
- BLOCK: Critical issues, must stop and address. Escalate to human.
```

- [ ] **Step 4: Commit references**

```bash
git add plugins/harness-scaffold/references/
git commit -m "feat(hnsf): add reference documents"
```

---

## Task Group 4: Core Skills (Layer 1)

**Dependencies:** Task Group 1
**Phase:** skills

- [ ] **Step 1: Create agent-behavior skill**

Create: `plugins/harness-scaffold/skills/core/agent-behavior/SKILL.md`

```markdown
---
name: agent-behavior
description: >
  Use when starting any coding task, classifying risk, setting up verification loops,
  or performing post-implementation review. Covers L1/L2/L3 risk classification,
  Ralph Loop (BUILD→TEST→FIX, max 3), self-review, doc impact scan.
compatibility: claude-code
---

# Agent Behavior Protocols

## 0. Unified Rules
- CLAUDE.md overrides AGENTS.md on conflict
- Explore evidence first — never infer without docs/code

## 1. Pre-Work Checklist
1. Read `docs/specs/{feature}/context/key-decisions.md` (if exists)
2. Read `docs/specs/{feature}/spec.md`
3. Read `docs/specs/{feature}/tasks.md` → confirm current task
4. Check `agent-os/standards/` → matching standard
5. If unclear → ask specific question

## 2. Risk Classification

| Level | Task Type | Action |
|-------|-----------|--------|
| **L1** | 리팩토링, 포맷, 주석, 문서 | Auto-proceed + build check |
| **L2** | 신규 파일, 메서드 시그니처, 테스트 추가 | Auto-proceed + Ralph Loop |
| **L3** | 비즈니스 로직, 도메인 개념, 아키텍처 변경 | **WAIT for human approval** |

## 3. Ralph Loop (L2/L3)
```
MAX_RETRIES = 3
LOOP:
  1. BUILD → fail → FIX
  2. TEST → pass → EXIT (success)
  3. ANALYZE → root cause
  4. FIX → different approach
  5. ITERATION++ → if >= 3 → EXIT (escalate)
```

Failure Classification:
- Execution Failure (Mock, 파싱) → 루프 내 수정
- Implementation Failure (404, 500, spec 불일치) → 즉시 STOP

## 4. Self-Review
- L1/L2: 프로젝트 린터 실행
- L3 (품질 모드): Fresh Context Reviewer subagent
- L3 (효율 모드): Inline checklist
- Verdict: SHIP / REVISE (max 2) / BLOCK

## 5. Doc Impact Scan
변경 파일 키워드 → agent-os/standards/ 매칭 → 관련 문서 보고

## 6. Decision Recording
```md
### [YYYY-MM-DD] Decision Title
- **Decision**: what  - **Reason**: why
- **Evidence**: docs/code  - **Impact**: affected files
```
Location: `docs/specs/{feature}/context/key-decisions.md`

## NEVER
- key-decisions.md 미확인 상태 코딩
- Ralph Loop에서 동일 접근 반복
- 테스트 약화/삭제로 통과
- L3 변경 미승인 진행
- 3회 실패 후 계속 재시도
```

- [ ] **Step 2: Create compaction skill**

Create: `plugins/harness-scaffold/skills/core/compaction/SKILL.md`

```markdown
---
name: compaction
description: >
  Use when context usage exceeds 75%, when completing a task group, or when
  transitioning between phases. Guides strategic compaction timing and
  post-compaction context recovery.
compatibility: claude-code
---

# Strategic Compaction

## When to Compact
- Task Group 완료 시
- Spec 문서 작성 완료 시
- Phase 전환 시

## When NOT to Compact
- 구현 도중
- 테스트 디버깅 중
- 의사결정 논의 중

## Pre-Compact Checklist
- [ ] git commit
- [ ] key-decisions.md에 결정 기록
- [ ] 다음 Task 확인
- [ ] 작업 완전 종료 확인

## Recovery (Post-Compact)
1. Read CLAUDE.md
2. Read docs/specs/{feature}/context/key-decisions.md
3. Read docs/specs/{feature}/context/open-questions.yml
4. Check tasks.md 체크박스
5. git log 최근 커밋 확인

## NEVER
- 구현 중간에 컴팩션
- Recovery 없이 작업 재개
```

- [ ] **Step 3: Create spec-evolution skill**

Create: `plugins/harness-scaffold/skills/core/spec-evolution/SKILL.md`

```markdown
---
name: spec-evolution
description: >
  Use when implementing a spec-driven feature and discovering new edge cases,
  race conditions, contract gaps, or requirement changes. Forces recording
  via open-questions.yml and spec amendments instead of silent code-only fixes.
compatibility: claude-code
---

# Spec Evolution

## Trigger Scope
- spec 기반 구현 중 새 edge case, contract gap 발견
- open-questions.yml이 존재하는 feature 구현
- /harness-scaffold:implement-tasks, /harness-scaffold:drift-check 문맥

## Context-First: MUST READ
1. docs/specs/{feature}/spec.md
2. context/key-decisions.md
3. context/open-questions.yml (없으면 생성)
4. tasks.md 또는 status.md

## Core Principles

### Unknown First
spec이 예상하지 못한 사실 발견 → 먼저 open-questions.yml에 기록

### 5 Categories
- `pre-impl`: 구현 전 해결 필수
- `impl-discovery`: 구현 중 발견
- `test-discovery`: 테스트 중 발견
- `closure`: 완료 경계 모호
- `waiver-revisit`: 나중 재검토

### Correctness Gate
다음 해당 시 amendment 승격:
- silent data corruption 가능성
- external contract 변경
- AC 의미 변경
- retry/locking semantics 변경

### Append-Only Amendment
기존 spec 수정 금지 → `## Amendments` 섹션으로 추가

## NEVER
- 발견을 코드로만 반영
- open-questions.yml 없이 진행
- approved spec 전면 수정
- bug/amendment/defer 미구분
```

- [ ] **Step 4: Create session skill**

Create: `plugins/harness-scaffold/skills/core/session/SKILL.md`

```markdown
---
name: session
description: >
  Use when starting a new session or recovering from compaction.
  Loads project context, active task state, and key decisions.
compatibility: claude-code
---

# Session Management

## Session Start
1. Read CLAUDE.md
2. Read agent-os/product/mission.md (if exists)
3. Check latest spec status in docs/specs/
4. Load active task context from tasks.md

## Post-Compaction Recovery
1. Read CLAUDE.md
2. Read key-decisions.md
3. Read open-questions.yml
4. Check tasks.md checkboxes
5. git log recent commits

## Session End
- Ensure all changes committed
- Update status.md if applicable
```

- [ ] **Step 5: Commit core skills**

```bash
git add plugins/harness-scaffold/skills/core/
git commit -m "feat(hnsf): add core skills (agent-behavior, compaction, spec-evolution, session)"
```

---

## Task Group 5: SDD Skills (Layer 2)

**Dependencies:** Task Group 4
**Phase:** skills

- [ ] **Step 1: Create spec-writing skill**

Create: `plugins/harness-scaffold/skills/sdd/spec-writing/SKILL.md`

```markdown
---
name: spec-writing
description: >
  Use when writing spec.md documents. Defines structure, quality contracts,
  and documentation-only constraints for spec writers.
compatibility: claude-code
---

# Spec Writing Rules

## spec.md Structure
1. Goal (1-2 sentences)
2. User Stories
3. Specific Requirements (SR-N sections)
4. Visual Design (if mockups exist)
5. Existing Code to Leverage
6. Out of Scope

## Quality Contract
- Overview readable in 30 seconds
- Sections independently readable
- No duplication across sections
- Target: <= 400 lines
- No actual code in spec (describe requirements only)

## Context Loading
If docs/index.yml exists → keyword match → load related specs/standards
Fallback: scan agent-os/standards/ directly

## NEVER
- Write actual code in spec.md
- Exceed 400 lines without justification
- Leave TBD/TODO placeholders
```

- [ ] **Step 2: Create task-planning skill**

Create: `plugins/harness-scaffold/skills/sdd/task-planning/SKILL.md`

```markdown
---
name: task-planning
description: >
  Use when breaking down specs into task groups. Defines grouping strategy,
  dependency management, metadata requirements, and test limits.
compatibility: claude-code
---

# Task Planning Rules

## Grouping Strategy
- Group by skill/layer (DB, API, Frontend, Test)
- Each group: 2-8 focused tests maximum
- Verification sub-task at end of each group

## Required Metadata per Group
- `dependencies`: which groups must complete first
- `phase`: execution phase identifier
- `required_skills`: skills to load during implementation

## Test Limits
- Each task group: 2-8 focused tests
- Test review group: max 10 additional tests
- Total per feature: ~16-34 tests

## Quality Contract
- Target: <= 600 lines
- Acceptance criteria per group
- Concrete verification commands

## NEVER
- Group without dependencies field
- Group without verification sub-task
- Exhaustive test coverage (focus on critical paths)
```

- [ ] **Step 3: Create implementation skill**

Create: `plugins/harness-scaffold/skills/sdd/implementation/SKILL.md`

```markdown
---
name: implementation
description: >
  Use when implementing task groups from tasks.md. Defines source-of-truth gates,
  standard loading, Ralph Loop integration, and verification requirements.
compatibility: claude-code
---

# Implementation Rules

## Source-of-Truth Gate
Before implementation starts:
1. Check open-questions.yml for `pre-impl` + `status: open`
2. If any exist → BLOCK (do not proceed)
3. Read spec.md, tasks.md, key-decisions.md

## Standard Loading
1. Read agent-os/standards/ relevant to current task
2. Read agent-os/product/tech-stack.md for build/test commands
3. Apply conventions from agent-os/standards/global/

## Verification Loop
- Apply Ralph Loop per task group
- BUILD → TEST → FIX (max 3 iterations)
- Record evidence in status.md

## Spec-Evolution Monitoring
- Active during all implementation
- New discoveries → open-questions.yml immediately
- Correctness gate violations → amendment

## NEVER
- Implement with pre-impl questions unresolved
- Skip verification evidence recording
- Claim completion without running tests
```

- [ ] **Step 4: Commit SDD skills**

```bash
git add plugins/harness-scaffold/skills/sdd/
git commit -m "feat(hnsf): add SDD skills (spec-writing, task-planning, implementation)"
```

---

## Task Group 6: Review Skills (Layer 3)

**Dependencies:** Task Group 4
**Phase:** skills

- [ ] **Step 1: Create architecture review skill**

Create: `plugins/harness-scaffold/skills/review/architecture/SKILL.md`

```markdown
---
name: review-architecture
description: >
  Use when reviewing specs for architecture compliance. Checks layer separation,
  dependency direction, module boundaries, and port/adapter patterns.
compatibility: claude-code
---

# Architecture Review

## Seed Discovery Protocol
See: `@references/review-protocol.md`

## Checklist
- [ ] Domain/Application/Infrastructure 레이어 책임 분리?
- [ ] 상향 의존성 없음? (Infrastructure → Domain 금지)
- [ ] 외부 통합은 Application-layer Port?
- [ ] 크로스 모듈 경계 변경 시 명시적 근거?
- [ ] 아키텍처 패턴 일관성?
- [ ] 순환 의존성 없음?
- [ ] 트랜잭션 경계 소유권 보존?

## Verdict
- SHIP: All checks passed
- REVISE: Non-blocking issues (max 2 rounds)
- BLOCK: Critical architecture violation → escalate

## Output
`docs/specs/{feature}/context/engineer-review-architecture.md`
```

- [ ] **Step 2: Create implementation review skill**

Create: `plugins/harness-scaffold/skills/review/implementation/SKILL.md`

```markdown
---
name: review-implementation
description: >
  Use when reviewing specs for implementation feasibility. Checks code conflicts,
  referenced module existence, complexity, NFR anti-patterns, and rollout strategy.
compatibility: claude-code
---

# Implementation Review

## Seed Discovery Protocol
See: `@references/review-protocol.md`

## Checklist
- [ ] 참조된 클래스/모듈 존재 확인?
- [ ] 기존 코드와 충돌 없음?
- [ ] 복잡도 리스크 식별?
- [ ] NFR 안티패턴 없음? (N+1, 타임아웃 누락, 무제한 리소스)
- [ ] 마이그레이션/롤백 전략 명시?
- [ ] 동시성 안전성 고려?

## Verdict
- SHIP / REVISE (max 2) / BLOCK

## Output
`docs/specs/{feature}/context/engineer-review-implementation.md`
```

- [ ] **Step 3: Create usecase review skill**

Create: `plugins/harness-scaffold/skills/review/usecase/SKILL.md`

```markdown
---
name: review-usecase
description: >
  Use when reviewing specs for usecase coverage. Checks actor-goal pairs,
  scenario flows, acceptance criteria traceability, and edge case expansion.
compatibility: claude-code
---

# Usecase Review

## Seed Discovery Protocol
See: `@references/review-protocol.md`

## Checklist
- [ ] Actor-goal 쌍 명확?
- [ ] Main/Alternative/Exception 흐름 정의?
- [ ] Preconditions/Postconditions 명시?
- [ ] AC(Acceptance Criteria) traceability?
- [ ] 엣지케이스 체계적 확장?
- [ ] 테스트 전략 매핑?

## Verdict
- SHIP / REVISE (max 2) / BLOCK

## Output
`docs/specs/{feature}/context/engineer-review-usecase.md`
```

- [ ] **Step 4: Commit review skills**

```bash
git add plugins/harness-scaffold/skills/review/
git commit -m "feat(hnsf): add review skills (architecture, implementation, usecase)"
```

---

## Task Group 7: Agents

**Dependencies:** Task Group 4, Task Group 5
**Phase:** agents

- [ ] **Step 1: Create spec-initializer agent**

Create: `plugins/harness-scaffold/agents/spec-initializer.md`

Generalized from mrt3-order: creates `docs/specs/YYYY-MM-DD-{name}/` with planning/, planning/visuals/, context/, implementation/ subdirectories. No language-specific references.

- [ ] **Step 2: Create spec-shaper agent**

Create: `plugins/harness-scaffold/agents/spec-shaper.md`

Generalized: Q&A requirements gathering (4-8 questions), visual asset check, reusability check. References `agent-os/product/` and `agent-os/standards/` instead of hardcoded paths. No domain-specific terminology.

- [ ] **Step 3: Create spec-writer agent**

Create: `plugins/harness-scaffold/agents/spec-writer.md`

Generalized: documentation-only (Write MD only, Read, WebFetch). No Bash, no code. References `agent-os/standards/` for compliance. No domain glossary.

- [ ] **Step 4: Create tasks-list-creator agent**

Create: `plugins/harness-scaffold/agents/tasks-list-creator.md`

Generalized: creates tasks.md from spec.md. Groups by skill/layer. Enforces 2-8 tests per group, metadata per group. References `agent-os/standards/`.

- [ ] **Step 5: Create implementer agent**

Create: `plugins/harness-scaffold/agents/implementer.md`

Generalized: production code only (Write code, Read, IDE diagnostics). No test writing, no Bash. References `agent-os/product/tech-stack.md` for language/framework context.

- [ ] **Step 6: Create tester agent**

Create: `plugins/harness-scaffold/agents/tester.md`

Generalized: test code only (Write tests, Read, Bash for test execution). No production code modification. References `agent-os/product/tech-stack.md` for test framework.

- [ ] **Step 7: Create verifier agent**

Create: `plugins/harness-scaffold/agents/verifier.md`

Generalized: full access (Write, Read, Bash, WebFetch). Verifies tasks.md completion, runs test suite, creates final-verification.md. No browser/Playwright (backend-agnostic).

- [ ] **Step 8: Commit agents**

```bash
git add plugins/harness-scaffold/agents/
git commit -m "feat(hnsf): add 7 specialized agents"
```

---

## Task Group 8: SDD Commands

**Dependencies:** Task Group 4, Task Group 5, Task Group 7
**Phase:** commands

- [ ] **Step 1: Create shape-spec command**

Create: `plugins/harness-scaffold/commands/shape-spec.md`

Phases: init folder → load docs context (optional) → Q&A via spec-shaper → test strategy → seed open-questions → inform user. Uses `docs/specs/` path.

- [ ] **Step 2: Create write-spec command**

Create: `plugins/harness-scaffold/commands/write-spec.md`

Phases: load docs context → load open-questions → delegate to spec-writer. Quality contract: <=400 lines.

- [ ] **Step 3: Create create-tasks command**

Create: `plugins/harness-scaffold/commands/create-tasks.md`

Phases: read spec → load standards → delegate to tasks-list-creator. Quality contract: <=600 lines, verification sub-tasks.

- [ ] **Step 4: Create implement-tasks command**

Create: `plugins/harness-scaffold/commands/implement-tasks.md`

Phases: worktree choice → source-of-truth gate → select groups → load standards → delegate implementation → Ralph Loop → final verification.

- [ ] **Step 5: Create orchestrate-tasks command**

Create: `plugins/harness-scaffold/commands/orchestrate-tasks.md`

Phases: resolve tasks → create orchestration.yml → gather assignments → skill routing → source-of-truth gate → execute (sequential/parallel) → track results.

- [ ] **Step 6: Create drift-check command**

Create: `plugins/harness-scaffold/commands/drift-check.md`

4 lenses (Document-state, Contract, Verification, Decision). All findings require file:line evidence. Output: context/drift-check.md. Final: ALIGNED / AMENDMENTS NEEDED / NOT ALIGNED.

- [ ] **Step 7: Create interview-capture command**

Create: `plugins/harness-scaffold/commands/interview-capture.md`

5-7 targeted questions, open-questions.yml update, gate result: BLOCKED / READY.

- [ ] **Step 8: Create verify command**

Create: `plugins/harness-scaffold/commands/verify.md`

Standards → Lint → Build → Test → Record Evidence. Iron law: no completion without evidence.

- [ ] **Step 9: Create spec-review command**

Create: `plugins/harness-scaffold/commands/spec-review.md`

Orchestrates 3 reviewers (architecture → implementation → usecase). Seed Discovery Protocol. Verdict: SHIP/REVISE/BLOCK.

- [ ] **Step 10: Commit SDD commands**

```bash
git add plugins/harness-scaffold/commands/shape-spec.md commands/write-spec.md commands/create-tasks.md commands/implement-tasks.md commands/orchestrate-tasks.md commands/drift-check.md commands/interview-capture.md commands/verify.md commands/spec-review.md
git commit -m "feat(hnsf): add 9 SDD pipeline commands"
```

---

## Task Group 9: Init Command (Core Entry Point)

**Dependencies:** Task Group 2, Task Group 3, Task Group 8
**Phase:** commands

- [ ] **Step 1: Create init command**

Create: `plugins/harness-scaffold/commands/init.md`

The most complex command. 3 phases:

**Phase 1 — Auto Scan:**
- Detect language/framework from build files
- Detect module structure
- Detect test framework
- Detect existing AI settings (.claude/, CLAUDE.md, AGENTS.md)
- Detect docs/ structure

**Phase 2 — Interactive Setup (3-5 questions):**
- Q1: Confirm project profile
- Q2: Architecture pattern
- Q3: CLAUDE.md merge/create
- Q4: Mode (quality default / efficient)
- Q5: Parallel execution

**Phase 3 — Generate:**
- CLAUDE.md (from template, fill placeholders)
- PLANS.md
- agent-os/ directory tree (config.yml, product/, standards/)
- .claude/hooks/hnsf-automation.json
- .claude/scripts/parallel-work.sh (if parallel enabled)
- .claude/COMPACTION-GUIDE.md
- docs/specs/ (empty directory)

**Idempotency:**
- New files → create
- Existing identical → skip
- Existing modified → show diff → user choice (merge/skip/overwrite)

- [ ] **Step 2: Commit init command**

```bash
git add plugins/harness-scaffold/commands/init.md
git commit -m "feat(hnsf): add /harness-scaffold:init entry point command"
```

---

## Task Group 10: Integration & README

**Dependencies:** Task Group 9
**Phase:** integration

- [ ] **Step 1: Update root README.md**

Modify: `README.md` — add harness-scaffold to plugin table and installation guide

- [ ] **Step 2: Copy design spec to plugin docs**

Verify: `plugins/harness-scaffold/docs/specs/2026-03-29-harness-scaffold-design.md` is up to date

- [ ] **Step 3: Run verification**

```bash
# Verify plugin.json is valid JSON
python3 -c "import json; json.load(open('plugins/harness-scaffold/.claude-plugin/plugin.json'))"

# Verify all commands referenced in plugin.json exist
for cmd in $(python3 -c "import json; [print(c) for c in json.load(open('plugins/harness-scaffold/.claude-plugin/plugin.json'))['commands']]"); do
  test -f "plugins/harness-scaffold/$cmd" && echo "OK: $cmd" || echo "MISSING: $cmd"
done

# Verify all skills have SKILL.md
find plugins/harness-scaffold/skills -name "SKILL.md" | sort

# Verify all agents exist
ls plugins/harness-scaffold/agents/
```

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat(hnsf): complete harness-scaffold plugin v0.1.0"
```

---

## Execution Order

```
Task Group 1 (Skeleton)
    ├──→ Task Group 2 (Templates)  ──→ Task Group 9 (Init Command)
    ├──→ Task Group 3 (References)        │
    ├──→ Task Group 4 (Core Skills) ──┐   │
    │    ├──→ Task Group 5 (SDD Skills)├──→ Task Group 8 (SDD Commands)
    │    └──→ Task Group 6 (Reviews)  ┘   │
    └──→ Task Group 7 (Agents) ──────────→│
                                          └──→ Task Group 10 (Integration)
```

Parallelizable: Groups 2, 3, 4, 6, 7 can all run in parallel after Group 1.
Groups 5 depends on 4. Group 8 depends on 4+5+7. Group 9 depends on 2+3+8. Group 10 depends on 9.
