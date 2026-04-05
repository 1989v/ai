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
