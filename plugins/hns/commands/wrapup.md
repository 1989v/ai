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

### Step 3: 실패 패턴 분류 (Self-Healing 입력)

Where Blocked의 각 항목을 evolve의 실패 유형으로 자동 분류:

| 실패 유형 | 감지 신호 | 셀프힐링 대상 |
|-----------|----------|-------------|
| **코딩 실수** (반복 패턴) | 같은 종류 에러 2회 이상, Ralph Loop 3회 초과 | lint rule / hook 추가 |
| **아키텍처 위반** | validate --code FAIL, domain에 Spring 의존 등 | CLAUDE.md constraint 추가 |
| **스펙 부족/모호** | drift-check FAIL, 구현 중 스펙 재해석 발생 | review skillset 강화 또는 스펙 템플릿 보완 |
| **도구 오용** | 잘못된 스킬 선택, subagent 과용, 수동 반복 | agent-behavior 규칙 추가 |
| **프롬프트 품질** | 스킬이 의도와 다른 결과 생성, 사용자 재요청 반복 | 해당 스킬의 description/지시문 개선 |

### Step 4: 개선 제안 리스크 분류

- **LOW**: 하네스 규칙 추가, 문서 업데이트 등 — 바로 실행 가능
- **MEDIUM**: 스크립트/자동화 추가, 워크플로 변경 — 계획 수립 후 실행
- **HIGH**: 아키텍처 변경, 큰 리팩토링 — 사람 판단 필요

### Step 5: Self-Healing 실행 (사용자 승인 후)

분류된 실패 패턴을 기반으로 자동 개선을 제안하고, 사용자 승인 시 즉시 적용:

```
[실패 패턴 감지]
  → 사용자에게 제안 목록 표시:
    1. "Ralph Loop 3회 초과 발생 — CLAUDE.md에 {패턴} 금지 규칙 추가할까요?"
    2. "validate --code에서 패키지 위반 감지 — hook enforcement에 체크 추가할까요?"
    3. "feat 스킬에서 ADR 판단이 누락됨 — description에 트리거 조건 보강할까요?"
  → 사용자 승인 항목만 실행
```

**실행 흐름:**

```
wrapup Step 3 (패턴 분류)
  → LOW 항목: `/hns:evolve` 자동 호출 (사용자 y/n 확인)
    → evolve가 규칙 생성 + changelog 기록
  → 프롬프트 품질 항목: 해당 스킬 파일을 직접 수정 제안
    → 사용자 승인 시 commands/*.md 또는 skills/*/SKILL.md 수정
  → MEDIUM/HIGH 항목: 회고 문서에 기록만 (다음 세션에서 수동 처리)
```

### Step 6: 회고 문서 최종화

Step 5의 Self-Healing 결과를 회고 문서에 추가:

```markdown
## Self-Healing Actions Taken
| Pattern | Type | Action | Result |
|---------|------|--------|--------|
| Ralph Loop 3회 초과 | 코딩 실수 | CLAUDE.md에 규칙 추가 | ✅ Applied |
| feat에서 ADR 누락 | 프롬프트 품질 | feat.md description 보강 | ✅ Applied |
| 검색 인덱스 설계 변경 | 아키텍처 변경 | 기록만 (HIGH) | 📋 Deferred |
```

## Integration

- **Called by:** `/hns:feat` (PHASE 7 이후 옵셔널), 사용자 직접 호출
- **Calls:**
  - `evolve` — 코딩실수/아키텍처위반/도구오용 패턴의 규칙 인코딩
  - `validate --docs` — 문서 동기화 확인
  - 직접 수정 — 프롬프트 품질 항목은 해당 스킬 파일을 직접 개선
