# Architecture Review

## Seed Discovery Protocol
Apply `references/review-protocol.md` stages 1–4 (Seed Discovery).

## Reference
`references/language-reference.md` §3 — Module / Interface / Depth / Seam 어휘의 단일 출처.

## Checklist

### Layer & Dependency
- [ ] Domain/Application/Infrastructure layer responsibility separation?
- [ ] No upward dependency violations? (Infrastructure → Domain forbidden)
- [ ] External integrations via Application-layer Ports?
- [ ] Cross-module boundary changes with explicit rationale?
- [ ] Architecture pattern consistency?
- [ ] No circular dependencies?
- [ ] Transaction boundary ownership preserved?

### Module Depth (anti-shallow)
- [ ] **Interface surface minimal?** Public methods/exports do not nearly mirror the implementation complexity
- [ ] **No shallow pass-throughs?** Modules with 1-2 methods that only forward to another module — fail the Deletion Test
- [ ] **Information hiding depth?** Caller does not need to know internal state, error ordering, or call sequencing beyond what the interface documents
- [ ] **Seam realism?** Any new interface with only 1 adapter is justified beyond "for testing" (1 adapter = hypothetical seam; 2+ = real seam)
- [ ] **Module naming from glossary?** New module names come from `glossary.md` terms (no `XxxService`, `FooBarHandler` AI-slop unless the glossary actually defines those)

### Deletion Test (apply to any new module ≥ 1 file)
For each new module, ask: *if we delete this module, does its complexity*
- collapse into one caller? → it was shallow, **REVISE** (inline it)
- scatter across N callers? → it was earning its keep, **SHIP**
- vanish entirely? → it was pure pass-through, **BLOCK** (remove it)

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
