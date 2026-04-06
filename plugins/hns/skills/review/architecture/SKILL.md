---
name: review-architecture
description: Use when reviewing specs for architecture compliance - checks layer separation, dependency direction, module boundaries
user-invocable: false
---

# Architecture Review

## Seed Discovery Protocol
Apply `@references/review-protocol.md` stages 1-4.

## Checklist
- [ ] Domain/Application/Infrastructure layer responsibility separation?
- [ ] No upward dependency violations? (Infrastructure → Domain forbidden)
- [ ] External integrations via Application-layer Ports?
- [ ] Cross-module boundary changes with explicit rationale?
- [ ] Architecture pattern consistency?
- [ ] No circular dependencies?
- [ ] Transaction boundary ownership preserved?

## Verdict
- **SHIP**: All checks passed
- **REVISE**: Non-blocking issues (max 2 rounds)
- **BLOCK**: Critical architecture violation → escalate

## Output
`docs/specs/{feature}/context/engineer-review-architecture.md`

## NEVER
- Start review without Seed Discovery Protocol
- Return verdict without evidence
- Mix reviewer types
