---
description: "[hns] Review harness complexity and remove unnecessary rules — Bitter Lesson applied"
---

# /hns:harness-diet

## Purpose
하네스 복잡도를 점검하고 불필요한 규칙을 제거한다.

## Required Inputs
- Access to harness files (CLAUDE.md, skills/, agents/, hooks/)

## Expected Outputs
- Diet proposal (candidate list)
- Updated harness (after user approval)
- Entry in docs/changelog/harness-changelog.md

---

## Philosophy
See `@references/diet-criteria.md` and `docs/philosophy/bitter-lesson.md`.

## Process
1. **Measure**: 하네스 토큰 수 측정
   - CLAUDE.md
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
- CLAUDE.md
- core/session
- core/compaction
- references/harness-philosophy.md

## NEVER
- 사용자 승인 없이 규칙 제거
- protected items 제거 제안
