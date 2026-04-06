---
description: "Review harness complexity, compact CLAUDE.md, and remove unnecessary rules — Bitter Lesson applied"
---

# /hns:diet

## Purpose
하네스 복잡도를 점검하고, CLAUDE.md를 지도 수준으로 압축하며, 불필요한 규칙을 제거한다.

## Required Inputs
- Access to harness files (CLAUDE.md, skills/, agents/, hooks/)
- Access to project docs/ directory

## Expected Outputs
- Diet proposal (candidate list)
- Updated harness (after user approval)
- Entry in docs/changelog/harness-changelog.md

---

## Philosophy
See `@references/diet-criteria.md` and `docs/philosophy/bitter-lesson.md`.

## Process

### Phase 1: CLAUDE.md Compaction
CLAUDE.md는 **지도(map)**이지 설명서가 아니다. 60줄 이하를 목표로 압축.

1. **Measure**: CLAUDE.md 줄 수 측정. 60줄 이하면 Phase 2로 스킵.
2. **Classify**: 각 섹션을 분류
   - `@references/diet-criteria.md`의 CLAUDE.md 기준 적용
3. **Extract**: "on-demand" 섹션을 docs/ 파일로 추출
   - 기존 docs/ 파일에 병합 가능하면 병합, 없으면 신규 생성
   - CLAUDE.md에는 한 줄 포인터(`→ docs/path.md`)만 남김
4. **Propose**: 추출 계획을 사용자에게 제시
   - 현재 줄 수 → 목표 줄 수
   - 추출할 섹션 목록 + 대상 docs/ 경로
5. **Execute**: 승인 후 실행
6. **Verify**: 최종 CLAUDE.md 줄 수 확인 (60줄 이하)

### Phase 2: Rule Pruning
하네스 규칙(skills, agents, hooks, templates)의 불필요 항목 제거.

1. **Measure**: 하네스 토큰 수 측정
   - skills/ 전체
   - agents/ 전체
   - hooks/ 전체
   - templates/ 전체

2. **Identify**: 감량 후보 식별
   - `@references/diet-criteria.md` 기준 적용
   - changelog에서 각 규칙의 마지막 트리거 일자 확인

3. **Propose**: 후보 목록을 사용자에게 제시
   - 각 후보의 현재 역할
   - 제거 시 예상 영향
   - 제거 근거

4. **Execute**: 사용자 승인된 항목만 제거/아카이브

5. **Record**: changelog에 기록:
   `[date] [diet] [removed: {rule}] [reason: {criterion}]`

## Protected Items (절대 제거 불가)
- CLAUDE.md (압축은 하되 삭제 불가)
- core/session
- core/compaction
- references/harness-philosophy.md

## NEVER
- 사용자 승인 없이 규칙 제거 또는 섹션 추출
- protected items 제거 제안
