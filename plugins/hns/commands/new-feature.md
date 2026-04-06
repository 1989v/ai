---
description: "[hns] End-to-end feature development pipeline: shape → write → review → create-tasks"
---

# /hns:new-feature

## Purpose
shape-spec → write-spec → spec-review → create-tasks를 한 번에 실행하는 통합 파이프라인.

## Required Inputs
- Feature description (user provides)

## Expected Outputs
- docs/specs/{date}-{name}/
  - planning/requirements.md
  - planning/test-quality.md
  - spec.md
  - context/engineer-review-*.md (5 files)
  - tasks.md
  - open-questions.yml

---

## PHASE 0: Context Loading

1. Read docs/index.yml (if exists) for auto-reference
2. Read agent-os/product/mission.md
3. Read agent-os/product/tech-stack.md

## PHASE 1: Shape Spec

Delegate to `/hns:shape-spec` flow:
1. spec-initializer → create spec folder
2. spec-shaper → requirements.md
3. Build test strategy → test-quality.md
4. Seed open-questions.yml

## PHASE 2: Write Spec

Delegate to `/hns:write-spec` flow:
1. Load open-questions context
2. spec-writer → spec.md

## PHASE 2.5: Open Questions Update

Update open-questions.yml with any new unknowns from spec writing.

## PHASE 3: Spec Review (5-Dimension)

Delegate to `/hns:spec-review` flow:
1. Run 5 reviewers sequentially
2. If BLOCK → return to PHASE 2 with feedback (max 2 iterations)
3. If REVISE → auto-revise spec.md (max 2 iterations)
4. If all SHIP → proceed

## PHASE 4: Create Tasks

Delegate to `/hns:create-tasks` flow:
1. tasks-list-creator → tasks.md

## PHASE 5: User Approval Gate

Present pipeline results summary:
```
Pipeline complete for: {feature-name}

Artifacts:
- requirements.md ✓
- spec.md ✓ (reviewed, {verdict})
- tasks.md ✓ ({N} task groups)
- open-questions.yml ({M} open, {K} closed)

Review the spec folder and approve to proceed with implementation.
```

Wait for user approval before suggesting `/hns:implement-tasks`.
