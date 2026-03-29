---
name: spec-review
description: "Multi-perspective spec review: architecture, implementation, usecase"
---

# /hnsf:spec-review

## Purpose
Review a spec from multiple perspectives to catch issues before implementation.

## Required Inputs
- Spec folder with spec.md

## Expected Outputs
- `context/engineer-review-{type}.md` per reviewer
- Overall verdict

---

## PHASE 1: Resolve Spec

1. Resolve spec folder (user-provided or most recent)
2. Read spec.md

## PHASE 2: Run Reviews

Execute 3 reviewers sequentially. Each applies the Seed Discovery Protocol from `@references/review-protocol.md`.

### Review 1: Architecture
Load `harness-scaffold:review-architecture` skill.
Focus: layer separation, dependency direction, module boundaries, patterns.

### Review 2: Implementation
Load `harness-scaffold:review-implementation` skill.
Focus: feasibility, code conflicts, complexity, NFR anti-patterns.

### Review 3: Usecase
Load `harness-scaffold:review-usecase` skill.
Focus: actor-goal pairs, flows, AC traceability, edge cases.

## PHASE 3: Verdict Progression

- If any reviewer returns **BLOCK** → halt remaining reviews → report
- If **REVISE** → continue remaining reviews → collect all issues
- If all **SHIP** → proceed

## PHASE 4: Summary

Output verdict table:
```
| Reviewer | Verdict | Issues |
|----------|---------|--------|
| Architecture | SHIP | 0 |
| Implementation | REVISE | 2 |
| Usecase | SHIP | 0 |

Overall: REVISE
Action: Address implementation issues, then re-review
```

Save individual reports to `context/engineer-review-{type}.md`.

## Mode Behavior
- **Quality mode**: Run all 3 reviewers always
- **Efficient mode**: Ask user which reviewers to run
