---
name: harness-evolve
description: "Encode a failure pattern as a new harness rule to prevent recurrence"
requires: []
auto_reference: false
---

# /harness-scaffold:harness-evolve

## Purpose
실패 패턴을 하네스 규칙으로 인코딩하여 재발 방지.

## Required Inputs
- Failure description (user provides or detected from recent session)

## Expected Outputs
- New rule added to appropriate harness layer
- Entry in docs/changelog/harness-changelog.md

---

## Execution

1. Load `hns:evolve` skill
2. Ask user to describe the failure (or detect from recent session)
3. Classify failure type
4. Propose rule addition with target location
5. User approves → create rule → record changelog
