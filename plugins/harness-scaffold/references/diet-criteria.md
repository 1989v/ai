# Diet Criteria

## 감량 후보 판별 기준

| # | Criterion | Signal | Action |
|---|-----------|--------|--------|
| 1 | 3개월 이상 미트리거 | changelog에 해당 규칙 트리거 기록 없음 | 후보 |
| 2 | 모델 내장 능력 중복 | 규칙 없이도 모델이 올바르게 동작 (샘플 테스트) | 후보 |
| 3 | 상위 규칙에 포함 | 다른 규칙이 이미 동일 범위를 커버 | 통합/제거 |
| 4 | 프로젝트 해당 없음 | 현재 프로젝트 기술 스택과 무관한 규칙 | 제거 |

## 감량 프로세스
1. 후보 목록 생성 → 사용자 승인 → 제거/아카이브
2. changelog에 기록: `[date] [diet] [removed rule] [reason]`
3. 제거 후 문제 발생 시: `harness-evolve`로 즉시 복원

## 절대 제거 불가 항목
- CLAUDE.md 자체
- core/session 스킬 (세션 관리)
- core/compaction 스킬 (컨텍스트 관리)
- references/harness-philosophy.md (원칙 문서)
