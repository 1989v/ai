# Diet Criteria

## CLAUDE.md Compaction 기준

각 섹션을 다음 기준으로 분류:

| 분류 | 기준 | 처리 |
|------|------|------|
| **always** | 매 세션 반드시 필요 (빌드 명령, 핵심 원칙, 라우팅 규칙) | CLAUDE.md에 유지 |
| **on-demand** | 특정 작업 시에만 필요 (패키지 구조, 테스트 예시, 토픽 목록 등) | docs/로 추출, 포인터만 남김 |
| **derivable** | 코드/git에서 파생 가능 (현재 모듈 목록, 최근 변경사항 등) | 삭제 |
| **duplicate** | 다른 docs/ 파일에 이미 존재 | 삭제, 기존 docs 포인터만 남김 |

### 추출 규칙
- 코드 블록(예시 포함) 10줄 이상 → on-demand 후보
- 테이블 5행 이상 → on-demand 후보
- 이미 docs/에 상세 문서가 있는 내용 → duplicate
- 기존 docs/ 파일에 병합 가능하면 신규 파일 생성하지 않음

---

## Rule Pruning 기준

| # | Criterion | Signal | Action |
|---|-----------|--------|--------|
| 1 | 3개월 이상 미트리거 | changelog에 해당 규칙 트리거 기록 없음 | 후보 |
| 2 | 모델 내장 능력 중복 | 규칙 없이도 모델이 올바르게 동작 (샘플 테스트) | 후보 |
| 3 | 상위 규칙에 포함 | 다른 규칙이 이미 동일 범위를 커버 | 통합/제거 |
| 4 | 프로젝트 해당 없음 | 현재 프로젝트 기술 스택과 무관한 규칙 | 제거 |

---

## 공통 프로세스
1. 후보 목록 생성 → 사용자 승인 → 실행
2. changelog에 기록: `[date] [diet] [action] [reason]`
3. 문제 발생 시: `harness-evolve`로 즉시 복원

## 절대 제거 불가 항목
- CLAUDE.md 자체 (압축은 가능)
- core/session 스킬 (세션 관리)
- core/compaction 스킬 (컨텍스트 관리)
- references/harness-philosophy.md (원칙 문서)
