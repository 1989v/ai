---
name: review-test-strategy
description: Use when reviewing specs for test strategy adequacy - checks AC-to-test derivation, test layer assignment, mock boundaries
user-invocable: false
---

# Test Strategy Review

## Seed Discovery Protocol
Apply `@references/review-protocol.md` stages 1-4.

## Checklist
- [ ] Every Acceptance Criterion has at least one test case derived?
- [ ] Test layer assignment appropriate? (unit/integration/component/e2e)
- [ ] Mock boundaries clearly defined? No over-mocking?
- [ ] Test data strategy specified? (fixtures, factories, builders)
- [ ] Negative/edge cases covered in test plan?
- [ ] Test naming convention consistent with project standards?

For each check item, load the corresponding skillset from `skillsets/` if available.

## Verdict
- **SHIP**: All checks passed
- **REVISE**: Non-blocking issues (max 2 rounds)
- **BLOCK**: Critical test coverage gap → escalate

## Output
`docs/specs/{feature}/context/engineer-review-test-strategy.md`

## NEVER
- Start review without Seed Discovery Protocol
- Return verdict without evidence
- Mix reviewer types
