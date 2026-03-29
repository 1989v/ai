---
name: review-implementation
description: Use when reviewing specs for implementation feasibility - checks code conflicts, complexity, NFR anti-patterns
---

# Implementation Review

## Seed Discovery Protocol
Apply `@references/review-protocol.md` stages 1-4.

## Checklist
- [ ] Referenced classes/modules exist?
- [ ] No conflicts with existing code?
- [ ] Complexity risks identified?
- [ ] No NFR anti-patterns? (N+1, missing timeouts, unbounded resources)
- [ ] Migration/rollback strategy specified?
- [ ] Concurrency safety considered?

## Verdict
- **SHIP** / **REVISE** (max 2) / **BLOCK**

## Output
`docs/specs/{feature}/context/engineer-review-implementation.md`
