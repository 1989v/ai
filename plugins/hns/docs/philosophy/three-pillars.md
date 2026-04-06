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
