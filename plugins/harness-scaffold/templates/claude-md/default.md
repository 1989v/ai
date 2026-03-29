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
| `/hnsf:shape-spec` | 요구사항 수집 및 스펙 폴더 초기화 |
| `/hnsf:write-spec` | 스펙 문서 작성 |
| `/hnsf:create-tasks` | 태스크 분해 |
| `/hnsf:implement-tasks` | 구현 (워크트리 옵션) |
| `/hnsf:orchestrate-tasks` | 순차/병렬 오케스트레이션 |
| `/hnsf:drift-check` | 구현-스펙 불일치 감지 |
| `/hnsf:interview-capture` | 구현 전 게이트 인터뷰 |
| `/hnsf:verify` | 검증 (표준→린트→빌드→테스트) |
| `/hnsf:spec-review` | 스펙 리뷰 (architecture/implementation/usecase) |

---

## Navigation Tips

- Feature-specific work → `docs/specs/`
- Standards → `agent-os/standards/`
- Product context → `agent-os/product/`
