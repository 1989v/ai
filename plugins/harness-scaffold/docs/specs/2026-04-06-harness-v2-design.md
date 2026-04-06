# Harness Scaffold v2 — Complete Design

> harness-scaffold를 하네스 엔지니어링 완전체로 확장하는 설계 문서

## Meta

| 항목 | 내용 |
|------|------|
| 작성일 | 2026-04-06 |
| 상태 | APPROVED |
| 기반 | harness-scaffold v0.1.0 + doc-scaffolding v0.1.0 |
| 벤치마크 | mrt3-order 하네스 시스템 |
| 철학 참조 | [하네스 엔지니어링 분석](../../../../msa/docs/harness-engineering-analysis.md) |

---

## 1. Goal

harness-scaffold 플러그인을 하네스 엔지니어링의 3기둥(Context, Enforcement, Evolution)을 모두 구현하는 완전체로 확장한다.

### 핵심 변경 요약

1. **doc-scaffolding 흡수** — doc-gen, doc-validate, doc-html을 harness-scaffold 하위로 통합
2. **5차원 spec-review** — domain + test-strategy 리뷰어 추가 + skillset 프로시저 체계
3. **new-feature 통합 커맨드** — shape→write→review→create-tasks 일괄 파이프라인
4. **verify-crosscheck** — 6레이어 교차 일관성 검증
5. **Lifecycle 레이어 신설** — GC, 자가진화, 다이어트, 벤치마크
6. **Enforcement 훅 체계** — reminder → feedback → enforcement 3단계
7. **컨텍스트 라우팅** — index.yml 기반 키워드 매칭, 필요 문서만 선택 로딩
8. **Knowledge Base** — 하네스 철학/결정/변경이력/벤치마크 문서화

---

## 2. Architecture — 6 Layer

```
Layer 1: Core           — 에이전트 행동 표준, 세션, 컴팩션, 스펙 진화
Layer 2: SDD            — 스펙 작성, 태스크 분해, 구현 루프
Layer 3: Review         — 5차원 스펙 리뷰 + skillset 프로시저
Layer 4: Docs           — CLAUDE.md/docs 생성, 검증, HTML 사이트
Layer 5: Lifecycle      — GC, 자가진화, 다이어트, 벤치마크
Layer 6: Project-Adaptive — 프로젝트별 도메인 스킬 (init 시 생성)
```

### 하네스 3기둥 매핑

| 기둥 | 개념 | 매핑 레이어 |
|------|------|------------|
| **Context** | CLAUDE.md, docs, session, compaction, 라우팅 | Core + Docs |
| **Enforcement** | 훅, 린트, 검증 게이트, Ralph Loop | SDD + Review + 훅 체계 |
| **Evolution** | GC, 자가진화, 다이어트, 벤치마크 | Lifecycle |

---

## 3. Context Routing — 전체 스캔 방지

### 3단계 로딩 전략

```
Level 0: 항상 로딩     → CLAUDE.md (60줄 이하, 지도 역할)
Level 1: 커맨드별 로딩  → 커맨드가 requires로 선언한 문서만
Level 2: 키워드 매칭    → index.yml로 관련 문서만 로딩 (max 3개, threshold 2+)
```

### index.yml 스키마

```yaml
schema_version: 1
entries:
  - id: {unique-id}
    path: {relative-path}
    section: "## Optional Section Header"   # 섹션 단위 로딩
    keywords: [keyword1, keyword2, ...]
auto_reference:
  threshold: 2          # 키워드 N개 이상 매칭 시 로딩
  max_docs: 3           # 한 번에 최대 N개
  prefer_section: true  # 전체 파일 대신 섹션만
```

### 커맨드별 의존 선언

```yaml
# 각 command .md frontmatter
requires:
  - agent-os/standards/global/conventions.md
  - agent-os/product/tech-stack.md
auto_reference: true   # Level 2 키워드 매칭 허용
```

### 원칙

- 매칭 문서는 조용히 로딩 (사용자 알림 불필요)
- 매칭 0건이면 그냥 진행
- `prefer_section: true`면 해당 섹션만 로딩 → 토큰 절약

---

## 4. Lifecycle Layer — GC, 자가진화, 다이어트, 벤치마크

### 4-1. harness-gc (가비지 컬렉션)

**3가지 실행 모드:**

| 모드 | 트리거 | 범위 |
|------|--------|------|
| 수동 | `/harness-scaffold:harness-gc` | full scan |
| 이벤트 | PostToolUse hook (커밋 후) | light scan |
| 스케줄 | `/schedule` 크론 | full scan |

**점검 4가지:**

| 항목 | 방법 |
|------|------|
| Dead code | 미사용 import, 빈 파일, 호출 없는 함수 탐지 |
| Doc drift | CLAUDE.md/docs 내용 vs 실제 코드 괴리 |
| Rule violation | 아키텍처 제약, 네이밍 규칙 위반 코드 |
| Stale harness | 불필요한 규칙/스킬/훅 탐지 (→ diet 연계) |

**출력**: `harness-gc-report.md`

**gc-agent 도구**: Read, Grep, Glob, Bash(린트/빌드), Write

### 4-2. harness-evolve (자가진화)

**흐름:**

```
실패 감지 → 패턴 분류 → 규칙 생성 → 하네스 반영 → changelog 기록
```

**실패 감지 소스:**
- 테스트 실패
- spec-review BLOCK 판정
- Ralph Loop 3회 초과
- verify 실패
- 사용자 피드백 ("이거 하지 마")

**분류 → 반영 대상:**

| 실패 유형 | 반영 대상 |
|----------|----------|
| 코딩 실수 | lint rule 또는 hook enforcement |
| 아키텍처 위반 | CLAUDE.md constraint 추가 |
| 스펙 부족 | spec-review skillset 강화 |
| 도구 오용 | agent behavior 규칙 추가 |

**출력**: `harness-changelog.md`에 자동 append

### 4-3. harness-diet (프롬프트 감량)

**핵심 원칙**: 모델이 좋아질수록 하네스는 가벼워져야 한다 (Bitter Lesson)

**동작:**
1. 하네스 토큰 수 측정 (CLAUDE.md + 스킬 + 훅 + 에이전트)
2. 각 규칙별 필요성 테스트
3. 불필요 규칙 후보 목록 생성
4. 사용자 승인 후 제거/아카이브
5. `harness-changelog.md`에 감량 이력 기록

**감량 판단 기준 (references/diet-criteria.md):**
- 3개월 이상 트리거 안 된 규칙 → 후보
- 모델 버전 업그레이드 후 중복된 내장 능력 → 후보
- 다른 규칙에 이미 포함된 하위 규칙 → 후보

### 4-4. harness-audit (외부 벤치마크)

**동작:**
1. 외부 소스 수집 (URL/레포/포스트 지정 또는 자동 검색)
2. 현재 harness-scaffold 구조와 비교
3. 누락된 패턴/개선 가능 항목 식별
4. `docs/benchmarks/YYYY-MM-DD-{source}.md` 생성
5. 채택 여부는 사용자 결정 → 채택 시 `harness-evolve`로 반영

**순환 사이클:**

```
harness-audit (외부 비교)
    → harness-evolve (규칙 추가/강화)
    → harness-diet (불필요 규칙 제거)
    → harness-audit (다시 비교)
```

---

## 5. Enforcement Hook System

### 3단계 훅 템플릿

| 단계 | 파일 | 성격 |
|------|------|------|
| Light | `hnsf-hooks-reminder.json` | 체크리스트 리마인더만 (현재 수준) |
| Medium | `hnsf-hooks-feedback.json` | 린트/컴파일 실패 시 피드백 (차단 안 함) |
| Strict | `hnsf-hooks-enforcement.json` | 실패 시 차단 + 자동 수정 루프 |

### "성공은 조용히, 실패만 시끄럽게" 원칙

```json
{
  "onSuccess": "silent",
  "onFailure": "feedback|block"
}
```

- `silent`: 통과 시 아무 출력 없음
- `feedback`: 실패 내용을 에이전트에게 전달, 자체 수정 유도
- `block`: 실패 시 해당 동작 차단

### Enforcement 훅 예시

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash",
      "pattern": "git commit*",
      "hooks": [{
        "type": "command",
        "command": "./gradlew compileKotlin --quiet",
        "onFailure": "block",
        "message": "컴파일 실패 — 커밋 차단"
      }]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Write|Edit",
      "pattern": "**/*.kt",
      "hooks": [{
        "type": "command",
        "command": "ktlint --relative .",
        "onSuccess": "silent",
        "onFailure": "feedback"
      }]
    }
  ]
}
```

### init 시 훅 단계 선택

```
Phase 4 (init): "프로젝트에 적용할 훅 수준을 선택하세요"
  (A) Light  — 리마인더만 (신규 프로젝트, 탐색 단계)
  (B) Medium — 피드백 (개발 진행 중)
  (C) Strict — 강제 (안정 운영 단계)
```

---

## 6. Review 5-Dimension + Skillsets

### 5개 리뷰어

| 리뷰어 | 페르소나 | 핵심 체크 |
|--------|---------|----------|
| architecture | Architecture Reviewer | 레이어 분리, 의존 방향, 포트/어댑터 |
| implementation | Implementation Engineer | 산술, 동시 쓰기, NFR 안티패턴, 마이그레이션 |
| usecase | UC Architect | 액터-목표, 시나리오 흐름, AC 추적성 |
| domain | Domain Modeler | 바운디드 컨텍스트, 유비쿼터스 언어, Aggregate 불변식 |
| test-strategy | Test Architect | AC→테스트 도출, 테스트 레이어, Mock 경계 |

### Skillset 프로시저 구조

```
skills/review/{type}/
├── SKILL.md                    ← 리뷰어 정의 + 체크리스트
└── skillsets/                   ← 절차적 서브스킬
    ├── {check-name-1}.md
    ├── {check-name-2}.md
    └── {check-name-3}.md
```

리뷰어가 체크리스트의 각 항목을 수행할 때 해당 skillset을 로딩하여 절차를 따름.
전체 skillset을 한 번에 로딩하지 않고, 해당 체크 항목 실행 시에만 로딩.

### Skillset 목록

**architecture/**
- dependency-direction-analysis.md
- port-adapter-compliance-audit.md
- module-boundary-impact-scan.md

**implementation/**
- arithmetic-verification.md
- concurrent-write-simulation.md
- nfr-anti-pattern-scan.md

**usecase/**
- ac-to-scenario-traceability.md
- exception-edge-case-expansion.md

**domain/**
- bounded-context-leakage-check.md
- ubiquitous-language-drift-scan.md
- aggregate-invariant-trace.md

**test-strategy/**
- ac-to-test-case-derivation.md
- mock-boundary-decision.md
- test-layer-assignment.md

### Seed Discovery Protocol (리뷰 컨텍스트 수집)

```
Stage 1: Seed    — spec.md 읽기, 분류, 참조 추출
Stage 2: Ring 1  — 같은 디렉토리 형제 파일
Stage 3: Index   — docs/index.yml 키워드 매칭
Stage 4: Code    — Grep/Glob으로 참조된 클래스/모듈 확인
```

### 판정

- **SHIP**: 이슈 없음, 진행
- **REVISE**: 수정 필요 (최대 2회 자동 리바이스)
- **BLOCK**: 중대 이슈, 사용자 확인 필요

---

## 7. new-feature (통합 파이프라인)

개별 커맨드를 수동 연결하는 대신 한 번에 흐르는 파이프라인.

```
Phase 0:   문서 컨텍스트 로딩 (index.yml)
Phase 1:   shape-spec (spec-shaper → requirements.md)
Phase 2:   write-spec (spec-writer → spec.md)
Phase 2.5: open-questions.yml 시드
Phase 3:   spec-review (5차원, BLOCK → Phase 2 복귀, 자동 리바이스 max 2회)
Phase 4:   create-tasks (tasks-list-creator → tasks.md)
Phase 5:   사용자 승인 게이트
```

- 각 Phase 실패 시 해당 Phase에서 멈추고 보고
- Phase 3 BLOCK → Phase 2로 자동 복귀
- 개별 커맨드는 그대로 유지 (단독 실행 가능)

---

## 8. verify-crosscheck (6레이어 교차 검증)

```
Layer 1: SOT 내부 일관성    — docs/ 내 문서 간 모순
Layer 2: docs ↔ agent-os    — 표준/규칙 문서 동기화
Layer 3: product ↔ specs    — 미션/요구사항 vs 스펙 정합성
Layer 4: standards ↔ specs  — 코딩 표준 vs 스펙 준수
Layer 5: specs ↔ tasks      — 스펙 요구사항 vs 태스크 커버리지
Layer 6: tasks ↔ code       — 태스크 완료 vs 실제 구현
```

**출력**: `CROSSCHECK_REPORT.md` (레이어별 PASS/WARN/FAIL + 증거 file:line)

---

## 9. Doc Layer (doc-scaffolding 흡수)

### 흡수 매핑

| doc-scaffolding 원본 | → harness-scaffold 위치 | 비고 |
|---------------------|------------------------|------|
| skills/scaffold/ | 제거 | init이 역할 흡수 |
| skills/doc-gen/ | skills/docs/doc-gen/ | |
| skills/doc-validate/ | skills/docs/doc-validate/ | |
| skills/doc-site/ | skills/docs/doc-html/ | rename |
| commands/scaffold.md | 제거 | init으로 통합 |
| commands/doc-gen.md | commands/doc-gen.md | |
| commands/doc-validate.md | commands/doc-validate.md | |
| commands/doc-site.md | commands/doc-html.md | rename |
| agents/scaffolding-agent.md | agents/doc-gen-agent.md | rename |
| templates/claude-md/ | templates/claude-md/ | 유지 |
| templates/docs-tree/ | templates/docs-tree/ | 이동 |
| templates/site-template.html | templates/site-template.html | 이동 |

### init 커맨드 확장

```
Phase 1: Auto scan (기존)
Phase 2: Interactive setup (기존)
Phase 3: doc-gen 호출 → CLAUDE.md + docs/ 생성
Phase 4: 훅 단계 선택 (Light/Medium/Strict)
Phase 5: index.yml 초기 생성
Phase 6: Idempotency check (기존)
```

---

## 10. Knowledge Base

```
docs/
├── philosophy/
│   ├── what-is-harness.md         — 하네스란? 말 비유, 모델 vs 하네스
│   ├── three-pillars.md           — Context / Enforcement / Evolution
│   ├── bitter-lesson.md           — 모델↑ → 하네스↓, diet 연계
│   └── evolution-model.md         — 실수→규칙 파이프라인, 순환 사이클
├── decisions/
│   └── NNN-{title}.md             — ADR 스타일 의사결정 기록
├── changelog/
│   └── harness-changelog.md       — evolve/diet/audit 자동 기록
├── benchmarks/
│   └── YYYY-MM-DD-{source}.md     — audit 결과 아카이브
└── specs/
    ├── 2026-03-29-harness-scaffold-design.md  (v1)
    └── 2026-04-06-harness-v2-design.md        (이 문서)
```

---

## 11. Final Structure

```
harness-scaffold/
│
├── .claude-plugin/plugin.json
│
├── skills/
│   ├── core/                          Layer 1: Core
│   │   ├── agent-behavior/SKILL.md
│   │   ├── compaction/SKILL.md
│   │   ├── session/SKILL.md           (확장: 라우팅 체계 통합)
│   │   └── spec-evolution/SKILL.md
│   │
│   ├── sdd/                           Layer 2: SDD
│   │   ├── spec-writing/SKILL.md
│   │   ├── task-planning/SKILL.md
│   │   └── implementation/SKILL.md
│   │
│   ├── review/                        Layer 3: Review (3→5차원)
│   │   ├── architecture/
│   │   │   ├── SKILL.md
│   │   │   └── skillsets/
│   │   │       ├── dependency-direction-analysis.md
│   │   │       ├── port-adapter-compliance-audit.md
│   │   │       └── module-boundary-impact-scan.md
│   │   ├── implementation/
│   │   │   ├── SKILL.md
│   │   │   └── skillsets/
│   │   │       ├── arithmetic-verification.md
│   │   │       ├── concurrent-write-simulation.md
│   │   │       └── nfr-anti-pattern-scan.md
│   │   ├── usecase/
│   │   │   ├── SKILL.md
│   │   │   └── skillsets/
│   │   │       ├── ac-to-scenario-traceability.md
│   │   │       └── exception-edge-case-expansion.md
│   │   ├── domain/                    ★ 신규
│   │   │   ├── SKILL.md
│   │   │   └── skillsets/
│   │   │       ├── bounded-context-leakage-check.md
│   │   │       ├── ubiquitous-language-drift-scan.md
│   │   │       └── aggregate-invariant-trace.md
│   │   └── test-strategy/             ★ 신규
│   │       ├── SKILL.md
│   │       └── skillsets/
│   │           ├── ac-to-test-case-derivation.md
│   │           ├── mock-boundary-decision.md
│   │           └── test-layer-assignment.md
│   │
│   ├── docs/                          Layer 4: Docs ★ 신규 (흡수)
│   │   ├── doc-gen/SKILL.md
│   │   ├── doc-validate/SKILL.md
│   │   └── doc-html/SKILL.md
│   │
│   └── lifecycle/                     Layer 5: Lifecycle ★ 신규
│       ├── gc/SKILL.md
│       ├── evolve/SKILL.md
│       ├── diet/SKILL.md
│       └── audit/SKILL.md
│
├── commands/                          19 commands
│   ├── init.md                        (확장: doc-gen + 훅 선택 + index.yml)
│   ├── shape-spec.md
│   ├── write-spec.md
│   ├── new-feature.md               ★ 신규
│   ├── spec-review.md                 (확장: 5차원)
│   ├── create-tasks.md
│   ├── implement-tasks.md
│   ├── orchestrate-tasks.md
│   ├── interview-capture.md
│   ├── drift-check.md
│   ├── verify.md
│   ├── verify-crosscheck.md           ★ 신규
│   ├── doc-gen.md                     ★ 흡수
│   ├── doc-validate.md                ★ 흡수
│   ├── doc-html.md                    ★ 흡수 (rename)
│   ├── harness-gc.md                  ★ 신규
│   ├── harness-evolve.md              ★ 신규
│   ├── harness-diet.md                ★ 신규
│   └── harness-audit.md               ★ 신규
│
├── agents/                            10 agents
│   ├── spec-initializer.md
│   ├── spec-shaper.md
│   ├── spec-writer.md
│   ├── tasks-list-creator.md
│   ├── implementer.md
│   ├── tester.md
│   ├── verifier.md
│   ├── gc-agent.md                    ★ 신규
│   ├── doc-gen-agent.md               ★ 흡수 (rename)
│   └── harness-auditor.md             ★ 신규
│
├── references/
│   ├── command-execution-contract.md
│   ├── review-protocol.md
│   ├── worktree-protocol.md
│   ├── gc-protocol.md                 ★ 신규
│   ├── harness-philosophy.md          ★ 신규
│   └── diet-criteria.md               ★ 신규
│
├── templates/
│   ├── claude-md/
│   │   ├── default.md
│   │   └── spring-kotlin.md           (흡수)
│   ├── docs-tree/                     (흡수)
│   │   ├── index.md
│   │   ├── architecture/overview.md
│   │   └── adr/_template.md
│   ├── docs-index.yml                 ★ 신규 (라우팅 맵 템플릿)
│   ├── site-template.html             (흡수)
│   ├── compaction-guide.md
│   ├── plans-md.md
│   ├── agent-os/                      (기존 유지)
│   ├── specs/                         (기존 유지)
│   ├── hooks/
│   │   ├── hnsf-hooks-reminder.json   (기존 rename)
│   │   ├── hnsf-hooks-feedback.json   ★ 신규
│   │   └── hnsf-hooks-enforcement.json ★ 신규
│   └── scripts/
│       └── parallel-work.sh           (기존 유지)
│
└── docs/                              Knowledge Base ★ 신규
    ├── philosophy/
    │   ├── what-is-harness.md
    │   ├── three-pillars.md
    │   ├── bitter-lesson.md
    │   └── evolution-model.md
    ├── decisions/
    │   ├── 001-layer-architecture.md
    │   ├── 002-gc-three-modes.md
    │   └── 003-doc-scaffolding-merge.md
    ├── changelog/
    │   └── harness-changelog.md
    ├── benchmarks/
    └── specs/
        ├── 2026-03-29-harness-scaffold-design.md
        ├── 2026-03-29-harness-scaffold-plan.md
        └── 2026-04-06-harness-v2-design.md
```

---

## 12. Out of Scope (v2)

- superpowers 플러그인 수정 (별개 유지)
- 프로젝트별 도메인 스킬 자동 생성 (Layer 6, v3 검토)
- 멀티 모델 하네스 (Claude 외 모델 지원)
- 하네스 마켓플레이스 (템플릿 공유)

---

## 13. Migration

### doc-scaffolding 제거

1. harness-scaffold v2 배포
2. msa/.claude/settings.json에서 `doc-scaffolding@ai-common` 제거
3. ai/plugins/doc-scaffolding/ 아카이브 또는 삭제

### 기존 프로젝트 영향

- 기존 `/harness-scaffold:*` 커맨드 경로 변경 없음 (하위 호환)
- 신규 커맨드 추가만 발생
- `init` 재실행 시 idempotency check로 기존 파일 보존
