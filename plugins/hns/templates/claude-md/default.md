# CLAUDE.md
# {{PROJECT_NAME}} Project Configuration

---

## Unified Rules

- **CLAUDE.md**: 이 파일. 200줄 이하, 항상 참인 것만
- **.claude/rules/**: 경로 스코프 컨벤션 (`paths:`)
- **docs/**: 상세 (필요할 때 읽는다)

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

- **리스크 분류 & 검증 루프** → `docs/standards/agent-behavior.md#risk-classification--confirmation`
  - Level 1-3 분류, Ralph Loop (BUILD→TEST→FIX, max 3회), Level 3 승인 필수
- **구현 후 리뷰** → `docs/standards/agent-behavior.md#self-review-protocol`
  - Level 1-2: 자동 lint, Level 3: fresh context reviewer
- **문서 동기화** → `docs/standards/agent-behavior.md#doc-gardening`
  - 구현 성공 후 Doc Impact Scan 실행

**범용 행동 원칙**:
- **탐색 우선, 증거 기반** → `docs/standards/agent-behavior.md#core-rules`
- **세션 복구·컴팩션** → `docs/standards/agent-behavior.md#session-management` (hns SessionStart/PreCompact 훅이 진행 노트를 주입)
- **세션 관리** → `docs/standards/agent-behavior.md#session-management`

---

## Standards & Conventions

All rules are routed via `docs/standards/`.

---

## AI Workflow Rules

작업 요청 시 `/hns:start`를 통합 진입점으로 사용한다.
요청을 분석하여 코드베이스 질의(탐색/분석/설명) 또는 피처 파이프라인(shape→write→review→tasks→implement→validate)으로 자동 라우팅한다.
버그 수정, 리팩토링 등 간단한 작업은 파이프라인 없이 직접 수행 가능.

하네스 Lifecycle 커맨드:
- 같은 실수 반복 시 → `/hns:evolve`로 규칙 추가
- 주기적 청소 → `/hns:gc`
- 하네스 복잡도 점검 → `/hns:diet`
- 세션 회고 → `/hns:wrapup`

---

## Active Commands

| Command | Purpose |
|---------|---------|
| `/hns:start` | 통합 진입점: 질의 응답 or 피처 파이프라인 (shape→spec→review→tasks→implement→validate) |
| `/hns:verify` | 검증 (표준→린트→빌드→테스트, 증거 기록) |
| `/hns:validate` | docs 일관성 · 코드 규칙 · 교차 일관성 (`--docs` `--code` `--crosscheck`) |
| `/hns:doctor` | 문서/하네스 헬스체크 (5 레이어 점수) |
| `/hns:glossary` | 도메인 사전 구축·갱신 |
| `/hns:wrapup` | 세션 회고 → evolve |
| `/hns:evolve` · `/hns:diet` · `/hns:gc` · `/hns:audit` | 하네스 진화 · 감량 · 청소 · 외부 비교 |
| `/hns:setup-hooks` | 라이프사이클 훅 설치 (reminder / feedback / enforce) |

---

## Navigation Tips

- Feature-specific work → `docs/specs/`
- Standards → `docs/standards/`
- Product context → `docs/product/`
