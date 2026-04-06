# harness-scaffold (hnsf) — Design Spec

**Date**: 2026-03-29
**Status**: Draft
**Plugin ID**: `hnsf`
**Display Name**: `harness-scaffold`

---

## 1. Overview

어떤 프로젝트든 `/hns:init` 한 번으로 성숙한 AI 하네스 환경을 구축하는 범용 Claude Code 플러그인.

mrt3-order 프로젝트의 검증된 AI 하네스 엔지니어링(SDD Pipeline, Agent-OS, Agent Behavior Standards, Spec-Reviewer, Hooks, Parallel Execution)을 범용화하여 언어/프레임워크 무관하게 적용 가능한 플러그인으로 제공한다.

### 핵심 가치

1. **Zero-to-Harness in 5 minutes** — 자동 스캔 + 대화형 셋업으로 즉시 구축
2. **SDD-First** — Spec → Plan → Implement → Verify 전체 라이프사이클
3. **Evidence-Based** — 모든 결정과 검증에 증거 필수
4. **Progressive Disclosure** — 필요한 컨텍스트만 로딩, 토큰 효율 극대화

### 타겟

- 오픈소스 범용 플러그인
- 1인 개발자부터 팀 프로젝트까지
- 언어/프레임워크 무관 (Java, TypeScript, Python, Go 등)

---

## 2. Architecture

### 4-Layer 구조

```
Layer 1 — Core (항상 활성)
  agent-behavior, compaction, spec-evolution, session

Layer 2 — SDD Pipeline (기본 활성)
  shape-spec, write-spec, create-tasks, implement-tasks,
  orchestrate-tasks, drift-check, interview-capture, verify

Layer 3 — Review (기본 활성)
  spec-reviewer (architecture, implementation, usecase)

Layer 4 — Project-Adaptive (init 시 생성)
  CLAUDE.md, agent-os/, hooks, parallel-work.sh
```

### 품질 모드 vs 효율 모드

`/hns:init` 셋업 시 선택. **기본값: 품질 모드**.

| | 품질 모드 (기본) | 효율 모드 |
|---|---|---|
| Self-Review | 서브에이전트 리뷰 (fresh context) | 인라인 체크리스트 |
| Spec-Review | 3관점 전체 순차 실행 | 선택한 관점만 |
| 스킬 로딩 | 관련 references 전부 로딩 | description + 본문만 |
| Ralph Loop | max 3회 + 상세 분석 | max 3회 + 간결 분석 |
| Drift Check | 4렌즈 전체 | 선택적 렌즈 |
| Verify | 표준 + Lint + 빌드 + 테스트 전체 | 빌드 + 테스트만 |

`agent-os/config.yml`에 저장:
```yaml
mode: quality  # quality | efficient
```

커맨드 실행 시 일시 오버라이드 가능: `/hns:verify --mode efficient`

### 디렉토리 구조

```
plugins/harness-scaffold/
├── .claude-plugin/plugin.json
├── commands/
│   ├── init.md                  # /hns:init
│   ├── shape-spec.md            # /hns:shape-spec
│   ├── write-spec.md            # /hns:write-spec
│   ├── create-tasks.md          # /hns:create-tasks
│   ├── implement-tasks.md       # /hns:implement-tasks
│   ├── orchestrate-tasks.md     # /hns:orchestrate-tasks
│   ├── drift-check.md           # /hns:drift-check
│   ├── interview-capture.md     # /hns:interview-capture
│   ├── verify.md                # /hns:verify
│   └── spec-review.md           # /hns:spec-review
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
│   ├── claude-md/               # CLAUDE.md 템플릿
│   ├── agent-os/                # agent-os 디렉토리 구조 템플릿
│   ├── hooks/                   # hooks 설정 템플릿
│   ├── specs/                   # spec.md, tasks.md 템플릿
│   └── scripts/                 # parallel-work.sh 등
└── references/
    ├── command-execution-contract.md
    ├── worktree-protocol.md
    └── review-protocol.md
```

---

## 3. `/hns:init` — 자동 스캔 + 대화형 셋업

### Phase 1: 자동 스캔 (무인)

```
감지 항목:
├── 언어/프레임워크 (Java/Spring, TypeScript/Express, Python/FastAPI 등)
├── 빌드 도구 (Gradle, Maven, npm, pnpm, pip 등)
├── 모듈 구조 (모노레포, 멀티모듈, 단일)
├── 테스트 프레임워크 (JUnit, Spock, Jest, pytest 등)
├── 기존 AI 설정 (.claude/, CLAUDE.md, AGENTS.md 존재 여부)
├── Git 설정 (브랜치 전략, 기존 hooks)
└── docs/ 구조 (기존 문서 체계 파악)
```

### Phase 2: 대화형 셋업 (3-5개 질문)

```
Q1. 프로젝트 프로파일이 맞나요? [자동 감지 결과 표시]
Q2. 아키텍처 패턴은? (Clean Architecture / Layered / Monolith / Microservice)
Q3. 기존 CLAUDE.md가 있는데 병합할까요, 새로 만들까요?
Q4. 모드 선택 — 품질 모드(기본, 비용 무관 최고 품질) / 효율 모드(토큰 절약)?
Q5. 병렬 실행 지원이 필요한가요? (worktree 스크립트 설치)
```

### Phase 3: 산출물 생성

```
프로젝트/
├── CLAUDE.md                                    # 프로젝트 맞춤
├── PLANS.md                                     # ExecPlan 규칙
├── agent-os/
│   ├── config.yml                               # mode, 활성 레이어
│   ├── product/
│   │   ├── mission.md                           # 프로젝트 미션
│   │   └── tech-stack.md                        # 자동 감지 기반
│   ├── standards/
│   │   ├── agent-behavior/
│   │   │   ├── core-rules.md                    # 탐색 우선, 증거 기반
│   │   │   ├── confirmation.md                  # L1/L2/L3 리스크 분류
│   │   │   ├── self-review.md                   # 구현 후 리뷰
│   │   │   ├── compaction.md                    # 컴팩션 규칙
│   │   │   ├── session.md                       # 세션 관리
│   │   │   └── doc-gardening.md                 # 문서 동기화
│   │   └── global/
│   │       └── conventions.md                   # 프로젝트 컨벤션
│   └── parallel-execution-rules.md              # (선택)
├── .claude/
│   ├── hooks/
│   │   └── hnsf-automation.json                 # 자동화 hooks
│   ├── scripts/
│   │   └── parallel-work.sh                     # (선택)
│   └── COMPACTION-GUIDE.md                      # 컴팩션 가이드
└── docs/
    ├── index.yml                                # (선택) 문서 라우팅
    └── specs/                                   # SDD 스펙 저장소
```

### CLAUDE.md 생성 구조

```markdown
# CLAUDE.md
# {프로젝트명} Project Configuration

## Unified Rules
- **AGENTS.md**: Shared baseline (있을 경우)
- **CLAUDE.md**: Project-specific overrides (this file)
- **PLANS.md**: Complex work orchestration
**On conflict**: CLAUDE.md wins.

## Environment
### Build Commands          ← tech-stack.md에서 자동 추출
### Test Commands           ← 테스트 프레임워크 감지 기반

## Agent Behavior Standards ← agent-os/standards/ 라우팅
## Standards & Conventions  ← agent-os/standards/global/ 라우팅
## Active Commands          ← hnsf 커맨드 목록

## Navigation Tips
- Start with docs/index.yml (있을 경우)
- Feature work → docs/specs/
```

### 멱등성

```
재실행 시 동작:
├── 신규 파일       → 생성
├── 기존 동일 파일   → 스킵
├── 기존 수정된 파일 → diff 표시 → 사용자 선택 (병합/스킵/덮어쓰기)
├── agent-os/config.yml → 기존 설정 보존, 새 옵션만 추가
└── CLAUDE.md        → 섹션별 병합 (사용자 추가 섹션 보존)
```

### 크로스 플랫폼 지원

| 파일 | 대상 | 생성 조건 |
|------|------|-----------|
| `CLAUDE.md` | Claude Code | 항상 |
| `AGENTS.md` 병합 | Codex, 범용 | 기존 AGENTS.md 있을 때 |
| `GEMINI.md` | Gemini CLI | 사용자 요청 시 |

agentskills.io 호환: 스킬 YAML frontmatter를 agentskills.io 스펙에 맞춰 설계.

---

## 4. SDD Pipeline 커맨드

### 파이프라인 흐름

```
/hns:shape-spec ──→ /hns:write-spec ──→ /hns:create-tasks
       │                                         │
       │         /hns:interview-capture          │
       │         (구현 전 게이트)                    │
       │                ↓                         ↓
       │         /hns:implement-tasks ←──── /hns:orchestrate-tasks
       │                │
       │         /hns:verify
       │                │
       └──────── /hns:drift-check (언제든 실행 가능)
```

### 커맨드 상세

#### `/hns:shape-spec` — 요구사항 수집

- Phase 1: 스펙 폴더 초기화 (`docs/specs/YYYY-MM-DD-{name}/`)
- Phase 2: docs/index.yml 기반 관련 문서 자동 로딩 (있을 경우)
- Phase 3: spec-shaper 에이전트로 Q&A (4-8개 질문)
- Phase 4: `planning/requirements.md` + `planning/test-quality.md` 생성
- Phase 5: `context/open-questions.yml` 시딩
- **산출물**: 스펙 폴더 + requirements + open-questions

#### `/hns:write-spec` — 스펙 작성

- spec-writer 에이전트에 위임 (코드 작성 금지)
- docs/index.yml 연동으로 관련 문서 자동 참조
- **산출물**: `spec.md` (≤400줄, Overview 30초 읽기 목표)

#### `/hns:create-tasks` — 태스크 분해

- tasks-list-creator 에이전트에 위임
- 그룹별 분해: 스킬 기반 (DB Layer, API Layer, Test 등)
- 그룹별 `phase`, `required_skills`, `dependencies` 메타데이터
- **산출물**: `tasks.md` (≤600줄, 검증 서브태스크 포함)

#### `/hns:implement-tasks` — 구현

- Phase 0: 워크트리 사용 여부 확인
- Phase 1: Source-of-truth 게이트 (open-questions의 pre-impl 미결 시 BLOCK)
- Phase 2: 태스크 그룹 선택 → 에이전트 위임
- Phase 3: 그룹별 Ralph Loop (BUILD→TEST→FIX, max 3회)
- Phase 4: 최종 검증 리포트

#### `/hns:orchestrate-tasks` — 순차/병렬 오케스트레이션

- `orchestration.yml` 생성 (실행 순서, 병렬 가능 그룹, 스킬 라우팅)
- Sequential: 현재 세션에서 순차 실행
- Parallel: 워크트리 기반 병렬 + 의존성 순서 머지

#### `/hns:drift-check` — 4렌즈 불일치 감지

- Lens A: 문서 상태 drift (status vs tasks)
- Lens B: 계약 drift (API/엔티티 vs spec)
- Lens C: 검증 drift (테스트 커버리지 vs AC)
- Lens D: 결정 drift (코드 vs key-decisions.md)
- **산출물**: `context/drift-check.md` (모든 발견에 `file:line` 증거 필수)
- **최종 판정**: ALIGNED / ALIGNED WITH AMENDMENTS NEEDED / NOT ALIGNED

#### `/hns:interview-capture` — 구현 전 게이트 인터뷰

- 5-7개 타겟 질문 (actor/trigger, 실패 시맨틱, 범위 경계 등)
- **산출물**: `context/open-questions.yml` 갱신 + 게이트 결과
- **게이트**: BLOCKED FOR IMPLEMENTATION / READY WITH DISCOVERIES TRACKED

#### `/hns:verify` — 구현 검증

```
Step 1: Standards Verification → agent-os/standards/ 준수 확인
Step 2: Lint Verification → 프로젝트 린터 실행 (감지 기반)
Step 3: Build Verification → tech-stack.md 빌드 커맨드
Step 4: Test Verification → 테스트 스위트 실행
Step 5: Record Evidence → status.md에 결과 + 타임스탬프
```

#### `/hns:spec-review` — 스펙 리뷰

- 3가지 리뷰어: architecture, implementation, usecase
- Seed Discovery Protocol로 동적 컨텍스트 로딩
- **Verdict**: SHIP / REVISE (max 2회) / BLOCK

### 범용화 전략

| mrt3-order (특화) | hnsf (범용) |
|-------------------|------------|
| Java/Spring 하드코딩 | 언어/프레임워크 감지 후 적응 |
| `./gradlew compileJava` | `agent-os/tech-stack.md`에서 빌드 커맨드 참조 |
| 도메인 스킬 (주문/결제) | 프로젝트별 `agent-os/standards/` 참조 |
| `docs/index.yml` 필수 | `docs/index.yml` 선택 (없으면 폴더 스캔 폴백) |
| BDD Spock 테스트 | 감지된 테스트 프레임워크 적응 |

---

## 5. Agent-OS 에이전트

### 7개 에이전트 — 역할 경계

| 에이전트 | 역할 | 허용 도구 | 금지 |
|----------|------|-----------|------|
| `spec-initializer` | 스펙 폴더 구조 생성 | Write, Bash | 코드 작성 |
| `spec-shaper` | 요구사항 Q&A 수집 | Write, Read, Bash, WebFetch | 코드 작성 |
| `spec-writer` | 스펙 문서 작성 | Write(MD만), Read, WebFetch | **Bash, 코드 작성** |
| `tasks-list-creator` | 태스크 분해 | Write, Read, Bash, WebFetch | 코드 작성 |
| `implementer` | 프로덕션 코드 구현 | Write(코드), Read, IDE진단 | **테스트 작성, 빌드 실행** |
| `tester` | 테스트 코드 작성 | Write(테스트), Read, Bash(테스트 실행만) | **프로덕션 코드 수정** |
| `verifier` | 최종 검증 + 리포트 | Write, Read, Bash, WebFetch | - |

### Iron Laws

```
spec-writer는 절대 코드를 작성하지 않는다
implementer는 절대 테스트를 작성하지 않는다
tester는 절대 프로덕션 코드를 수정하지 않는다
```

### 설계 원칙

1. **컨텍스트 격리** — 각 에이전트는 fresh context (서브에이전트), 필요한 파일만 명시적 전달
2. **범용 적응** — 언어/프레임워크 하드코딩 없음, `agent-os/tech-stack.md` 참조
3. **Progressive Disclosure** — 에이전트 정의 ≤180줄, 상세는 references/ 참조

---

## 6. Skills

### Layer 1 — Core Skills (항상 활성)

#### `core/agent-behavior`

- **트리거**: 모든 코드 수정 작업 시작
- Pre-Work 체크리스트: key-decisions.md → spec.md → tasks.md 확인
- **리스크 분류**:
  - L1 (Auto): 리팩토링, 포맷, 문서 → 빌드 체크만
  - L2 (Ralph Loop): 신규 파일, 메서드 변경 → BUILD→TEST→FIX (max 3회)
  - L3 (Human Gate): 비즈니스 로직, 아키텍처 변경 → 사람 승인 필수
- Ralph Loop: Execution Failure → 루프 내 수정, Implementation Failure → 즉시 STOP
- **NEVER**: 동일 접근 반복, 테스트 약화로 통과, L3 미승인 코딩

#### `core/compaction`

- **트리거**: 컨텍스트 75%+ 사용 시
- 언제 컴팩트: 태스크 그룹 완료, 스펙 작성 완료, 페이즈 전환
- 언제 금지: 구현 중, 디버깅 중, 결정 중
- Recovery: CLAUDE.md + key-decisions.md → git history → 테스트 코드 참조

#### `core/spec-evolution`

- **트리거**: SDD 기반 구현 중
- open-questions.yml 5분류: pre-impl, impl-discovery, test-discovery, closure, waiver-revisit
- Correctness Gate: silent corruption, 외부 계약, AC 변경 → amendment 승격
- Append-Only: 기존 spec 수정 금지, `## Amendments` 섹션으로 추가
- **NEVER**: 발견을 코드로만 반영, open-questions.yml 없이 진행

#### `core/session`

- **트리거**: 세션 시작, 컴팩션 후 복구
- 세션 시작: CLAUDE.md → agent-os/product/ → 최근 spec status 로딩
- 복구: key-decisions.md → open-questions.yml → tasks.md 체크박스

### Layer 2 — SDD Skills

#### `sdd/spec-writing`

- spec.md 구조: Goal, User Stories, Specific Requirements, Out of Scope
- 품질 계약: Overview 30초, 독립 섹션, ≤400줄
- docs/index.yml 키워드 매칭 관련 문서 자동 참조

#### `sdd/task-planning`

- 그룹별 분해 (스킬/레이어 기반)
- 그룹별 메타데이터: phase, required_skills, dependencies
- 검증 서브태스크 필수, ≤600줄

#### `sdd/implementation`

- Source-of-truth 게이트 (pre-impl 미결 시 BLOCK)
- 표준 로딩: agent-os/standards/ 참조
- 검증 루프: Ralph Loop 연동

### Layer 3 — Review Skills

#### `review/architecture`

- Seed Discovery Protocol: spec → siblings → index map → code evidence
- 체크리스트: 레이어 분리, 의존성 방향, 순환 의존성, 모듈 경계
- Verdict: SHIP / REVISE (max 2회) / BLOCK

#### `review/implementation`

- 참조 클래스/모듈 존재 확인, 기존 코드 충돌, 복잡도 리스크
- NFR 안티패턴 스캔 (N+1, 타임아웃 누락, 무제한 리소스)
- 마이그레이션/롤백 전략 검증

#### `review/usecase`

- Actor-goal 쌍, main/alternative/exception 흐름
- AC traceability, 엣지케이스 확장
- 테스트 전략 매핑 검증

### Seed Discovery Protocol (모든 리뷰 스킬 공통)

```
Stage 1: Seed — 대상 spec 읽기, 문서 유형 분류
Stage 2: First-Ring — 같은 디렉토리 siblings (tasks*, status*, context/*)
Stage 3: Index Map — docs/index.yml 키워드 매칭 (없으면 agent-os/standards/ 폴백)
Stage 4: Code Evidence — Grep/Glob → 참조 클래스/모듈 확인
```

### 토큰 효율 전략

- **CSO**: 스킬 description은 "Use when..." 트리거 조건만
- **Progressive Disclosure**: frontmatter(~100 tokens) → 본문(<5k tokens) → references(on-demand)
- **품질 모드 기본**: 서브에이전트 리뷰 (fresh context), 전체 references 로딩

---

## 7. Hooks & 병렬 실행

### Hooks (`.claude/hooks/hnsf-automation.json`)

**PostToolUse — 체크리스트 리마인더:**

- spec.md Write 시: Overview 30초? 섹션 독립? open-questions 갱신? ≤400줄?
- tasks.md Write 시: dependencies 명시? 검증 서브태스크? 메타데이터? ≤600줄?
- orchestration.yml Write 시: 의존성 일치? 병렬 충돌 없음?

**PrePrompt — 컨텍스트 경고:**

- >75%: 전략적 컴팩션 고려 알림
- >90%: 즉시 컴팩션 권장 + Pre-Compact 체크리스트

**PostToolUse — 완료 게이트 (품질 모드):**

- 태스크 completed 마킹 시: verify 증거 존재? status.md 기록?

### 병렬 실행

**`parallel-work.sh`:**
```bash
parallel-work.sh create <task-name> [base-branch]
parallel-work.sh list
parallel-work.sh status
parallel-work.sh remove <task-name>
parallel-work.sh cleanup
```

**병렬 실행 규칙:**
- 자동 승인: orchestration.yml 명시 태스크, 구현 방법 선택, 파일 위치 등
- 확인 필요: 치명적 리스크, 스펙 모호성, 블로킹 의존성
- 목표: 95%+ 무확인 완료
- 머지 충돌 시: 자동 해결 시도 X, 즉시 STOP

---

## 8. open-questions.yml & Spec Evolution

### open-questions.yml 구조

```yaml
questions:
  - id: OQ-001
    category: pre-impl    # pre-impl | impl-discovery | test-discovery | closure | waiver-revisit
    question: "설명"
    raised_by: agent-name
    raised_at: 2026-04-01
    status: open           # open | resolved | deferred
    resolution: null
    resolved_at: null
```

### 게이트 규칙

- `pre-impl` + `open` → **구현 BLOCK**
- `impl-discovery` + `open` → 구현 계속, amendment 후보
- `test-discovery` → 테스트 작성 시 반영
- `closure` → 스펙 완료 전 해결 필수
- `waiver-revisit` → 이월 허용

### Amendment 승격 조건

1. behavior 문장 변경
2. API request/response 스키마 변경
3. AC 불충분
4. Source-of-truth 재정의

→ spec.md `## Amendments` 섹션으로 append-only 추가

---

## 9. Verify & 품질 게이트

### `/hns:verify` 실행 흐름

```
Step 1: Standards → agent-os/standards/ 준수 (FAIL on violation)
Step 2: Lint → 프로젝트 린터 (FAIL on errors, WARN on warnings)
Step 3: Build → tech-stack.md 빌드 커맨드 (FAIL on failure)
Step 4: Test → 테스트 스위트 (FAIL on failure)
Step 5: Record → status.md에 증거 + 타임스탬프
```

### status.md 구조

```markdown
# Feature Status
## Current State: IN_PROGRESS

## Verification History
| Date | Step | Result | Evidence |
|------|------|--------|----------|
| 2026-04-01 | Build | PASS | BUILD SUCCESSFUL in 12s |
| 2026-04-01 | Test | PASS | 47 tests, 0 failures |

## Task Completion
- [x] Group 1: Data Layer (verified 2026-04-01)
- [ ] Group 2: API Layer
```

### Iron Laws (모든 모드 공통)

1. **검증 증거 없이 완료 선언 금지**
2. **Ralph Loop 3회 실패 → 즉시 STOP**
3. **pre-impl open question 미결 → 구현 BLOCK**

---

## 10. Out of Scope (v1)

- 도메인 특화 스킬 (주문/결제/예약 등) — 프로젝트별 자체 생성
- CI/CD 파이프라인 통합
- IDE 플러그인 (VS Code, JetBrains)
- 웹 대시보드
- 다국어 지원 (한국어 기본, 영어는 v2)
