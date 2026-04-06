---
name: spec-evolution
description: Use when implementing a spec-driven feature and discovering new edge cases, contract gaps, or requirement changes
user-invocable: false
---

# Spec Evolution

## Trigger Scope
- Spec-based implementation discovers new edge case, contract gap
- open-questions.yml exists for the feature
- During /hns:implement-tasks, /hns:drift-check context

## Context-First: MUST READ
1. docs/specs/{feature}/spec.md
2. context/key-decisions.md
3. context/open-questions.yml (create if missing)
4. tasks.md or status.md

## Core Principles

### Unknown First
Unexpected discovery → record in open-questions.yml before continuing

### 5 Categories
- `pre-impl`: Must resolve before implementation
- `impl-discovery`: Found during implementation
- `test-discovery`: Found during testing
- `closure`: Ambiguous completion boundary
- `waiver-revisit`: Accept now, revisit later

### Correctness Gate
Promote to amendment when:
- Silent data corruption possible
- External contract changes
- AC meaning changes
- Retry/locking semantics change

### Append-Only Amendment
Never modify approved spec body → add `## Amendments` section

## NEVER
- Reflect discoveries only in code
- Proceed without open-questions.yml
- Fully rewrite approved spec
- Treat bugs/amendments/deferrals equally
