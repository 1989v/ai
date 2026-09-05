# The Three Pillars of Harness Engineering

## Pillar 1: Context Files (컨텍스트)
AI가 작업 시작 시 가장 먼저 읽는 파일.

**원칙**: 1,000페이지 설명서가 아니라 지도를 줘야 한다.
- CLAUDE.md: 200줄 이하, 보편적으로 항상 적용되는 내용만
- 세부 내용은 다른 파일에 나눠서 필요할 때만 로딩
- 컨텍스트 부패 해결: 새 세션마다 항상 읽히는 파일

**hns 매핑**
- 로딩은 플랫폼: 루트 CLAUDE.md 항상, 하위 CLAUDE.md·`.claude/rules/` `paths:` 는 그 파일을 읽을 때, 스킬은 호출될 때
- `hns:agent-behavior` — 세션·컴팩션 규칙(파일이 원본)
- SessionStart / PreCompact 훅 — 진행 노트 주입·보존 지시
- `/hns:doc-gen` `/hns:init` — CLAUDE.md + docs/ + `.claude/rules/` 생성

## Pillar 2: Auto-Enforcement (자동 강제)
"좋은 코드를 작성해 줘"가 아니라 기계적으로 강제.

**원칙**: 성공은 조용히, 실패만 시끄럽게.
- 린터가 빨간 불 → 에이전트가 자체 수정 → 사람 개입 불필요
- 통과한 테스트 4,000줄을 다 보여주면 AI가 할 일을 잃어버림

**hns 매핑**
- `hns:implement-tasks` — BUILD→TEST→FIX 최대 3회, 검증 증거 없이 완료 없음
- `hns:spec-review` — 6차원 병렬 리뷰(읽기 전용 서브에이전트)
- 훅 — 커밋 전 컴파일(deny), 편집 후 린트, Stop 증거 게이트(prompt)

**3단계 훅:**
| 단계 | 성격 | 용도 |
|------|------|------|
| reminder | 세션 복구·컴팩션 보존만 | 신규 프로젝트 |
| feedback | + 컴파일·린트 실패 알림 | 개발 중 |
| enforce | + 커밋 차단 · 완료 주장 증거 게이트 | 안정 운영 |

## Pillar 3: Evolution (진화)
에이전트가 실수할 때마다 하네스가 더 정교해지는 구조.

**핵심**: 나쁜 패턴이 있으면 AI가 따라하므로, 주기적으로 청소(GC).
- 실수 → 새 규칙 → 린트/테스트/제약 추가
- 하네스가 시간이 지날수록 점점 더 정교해짐

**hns 매핑**
- `/hns:gc` — 청소 (dead code, doc drift, rule violation, stale harness)
- `/hns:evolve` — 실수 → memory / rules / hook / CLAUDE.md 중 한 곳
- `/hns:diet` — 사용 증거 기반 감량
- `/hns:audit` — 외부 벤치마크 비교
- auto memory — 사용자 교정을 Claude 가 스스로 축적 (가장 싼 진화 경로)
