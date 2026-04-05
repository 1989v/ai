---
name: review-domain
description: Use when reviewing specs for domain model integrity - checks bounded contexts, ubiquitous language, aggregate invariants
---

# Domain Review

## Seed Discovery Protocol
Apply `@references/review-protocol.md` stages 1-4.

## Checklist
- [ ] Bounded context boundaries clearly defined? No leakage across contexts?
- [ ] Ubiquitous language consistent between spec and existing codebase?
- [ ] Aggregate invariants explicitly stated and enforceable?
- [ ] Domain events properly scoped to owning aggregate?
- [ ] No cross-aggregate direct references? (API only)
- [ ] Value Objects vs Entities correctly classified?

For each check item, load the corresponding skillset from `skillsets/` if available.

## Verdict
- **SHIP**: All checks passed
- **REVISE**: Non-blocking issues (max 2 rounds)
- **BLOCK**: Critical domain model violation → escalate

## Output
`docs/specs/{feature}/context/engineer-review-domain.md`

## NEVER
- Start review without Seed Discovery Protocol
- Return verdict without evidence (cite file:line)
- Mix reviewer types
