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

## AI Workflow Rules

신규 기능 개발 요청 시 `/hns:new-feature` 파이프라인을 우선 사용한다.
스펙 작성 → 리뷰 → 태스크 분해를 거친 후 구현에 들어간다.
버그 수정, 리팩토링 등 간단한 작업은 파이프라인 없이 직접 수행 가능.

하네스 Lifecycle 커맨드:
- 같은 실수 반복 시 → `/hns:harness-evolve`로 규칙 추가
- 주기적 청소 → `/hns:harness-gc`
- 하네스 복잡도 점검 → `/hns:harness-diet`

---

## Active Commands

| Command | Purpose |
|---------|---------|
| `/hns:new-feature` | 신규 기능 파이프라인 (shape→write→review→tasks) |
| `/hns:shape-spec` | 요구사항 수집 및 스펙 폴더 초기화 |
| `/hns:write-spec` | 스펙 문서 작성 |
| `/hns:spec-review` | 스펙 리뷰 (architecture/implementation/usecase) |
| `/hns:create-tasks` | 태스크 분해 |
| `/hns:implement-tasks` | 구현 (워크트리 옵션) |
| `/hns:orchestrate-tasks` | 순차/병렬 오케스트레이션 |
| `/hns:interview-capture` | 구현 전 게이트 인터뷰 |
| `/hns:drift-check` | 구현-스펙 불일치 감지 |
| `/hns:verify` | 검증 (표준→린트→빌드→테스트) |
| `/hns:harness-gc` | 가비지 컬렉션 (dead code, doc drift 청소) |
| `/hns:harness-evolve` | 실패 패턴 → 규칙 인코딩 |
| `/hns:harness-diet` | 불필요한 규칙 제거 (Bitter Lesson) |
| `/hns:harness-audit` | 외부 벤치마크 비교 |

---

## Navigation Tips

- Feature-specific work → `docs/specs/`
- Standards → `agent-os/standards/`
- Product context → `agent-os/product/`
