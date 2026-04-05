# The Bitter Lesson — Harness Simplification

> 모델이 똑똒해질수록 하네스는 더 단순해져야 한다 — Richard Sutton

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
