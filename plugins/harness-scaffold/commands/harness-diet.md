---
name: harness-diet
description: "Review harness complexity and remove unnecessary rules — Bitter Lesson applied"
requires: []
auto_reference: false
---

# /harness-scaffold:harness-diet

## Purpose
하네스 복잡도를 점검하고 불필요한 규칙을 제거한다.

## Required Inputs
- Access to harness files (CLAUDE.md, skills/, agents/, hooks/)

## Expected Outputs
- Diet proposal (candidate list)
- Updated harness (after user approval)
- Entry in docs/changelog/harness-changelog.md

---

## Execution

1. Load `hns:diet` skill
2. Measure current harness token count
3. Apply `@references/diet-criteria.md`
4. Present candidates to user
5. User selects items to remove → execute → record changelog
