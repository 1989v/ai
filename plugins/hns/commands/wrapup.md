---
description: "Session retrospective: what-went-well, where-blocked, what-to-change with risk classification. Trigger on: 세션 정리, 회고, 작업 마무리, session wrapup, retrospective"
---

# /hns:wrapup

세션 종료 시 자동 회고 문서를 생성한다.

## Usage

```
/hns:wrapup                    # 현재 세션 회고
/hns:wrapup --spec {path}      # 특정 스펙 기준 회고
```

## Required Inputs
- context/progress.md (있으면 사용, 없으면 세션 대화 기반)
- 태스크 완료/실패 이력
- 검증 리포트 (있으면 사용)

## Expected Outputs
- `docs/retrospectives/{date}-session.md`

---

## Process

### Step 1: 세션 데이터 수집

1. `context/progress.md` 읽기 (태스크 진행 상태)
2. 최근 커밋 이력 분석 (`git log --oneline -20`)
3. 검증 리포트 수집 (verify, validate, drift-check 결과)
4. 현재 대화에서 에러/재시도/블로커 이벤트 추출

### Step 2: 회고 문서 생성

```markdown
# Session Retrospective — {date}

## What Went Well
| Item | Evidence | Impact |
|------|----------|--------|
| {완료된 태스크/성공 패턴} | {커밋 SHA, 테스트 결과 등} | {효과} |

## Where Blocked
| Item | Root Cause | Duration | Resolution |
|------|-----------|----------|------------|
| {블로커/실패} | {원인 분석} | {소요 시간} | {해결 방법 또는 미해결} |

## What to Change
| Suggestion | Risk | Effort | Action |
|------------|------|--------|--------|
| {개선 제안} | LOW/MEDIUM/HIGH | {예상 공수} | {바로 실행 가능/계획 필요/사람 판단} |
```

### Step 3: 개선 제안 리스크 분류

- **LOW**: 하네스 규칙 추가, 문서 업데이트 등 — 바로 실행 가능
- **MEDIUM**: 스크립트/자동화 추가, 워크플로 변경 — 계획 수립 후 실행
- **HIGH**: 아키텍처 변경, 큰 리팩토링 — 사람 판단 필요

### Step 4: 액션 아이템 연결

LOW 리스크 항목 중 즉시 적용 가능한 것은:
- `/hns:evolve`로 규칙 인코딩 제안
- `/hns:validate`로 문서 동기화 제안

## Integration

- **Called by:** `/hns:feat` (PHASE 7 이후 옵셔널), 사용자 직접 호출
- **Calls:** evolve (LOW 리스크 자동 적용 시)
