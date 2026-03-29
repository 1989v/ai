---
name: review-usecase
description: >
  Use when reviewing specs for usecase coverage. Checks actor-goal pairs,
  scenario flows, acceptance criteria traceability, and edge case expansion.
compatibility: claude-code
---

# Usecase Review

## Seed Discovery Protocol
Apply `@references/review-protocol.md` stages 1-4.

## Checklist
- [ ] Actor-goal pairs clearly defined?
- [ ] Main/Alternative/Exception flows specified?
- [ ] Preconditions/Postconditions explicit?
- [ ] AC (Acceptance Criteria) traceable?
- [ ] Edge cases systematically expanded?
- [ ] Test strategy mapping defined?

## Verdict
- **SHIP** / **REVISE** (max 2) / **BLOCK**

## Output
`docs/specs/{feature}/context/engineer-review-usecase.md`
