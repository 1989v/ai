---
name: orchestrate-tasks
description: "Create orchestration plan and execute tasks sequentially or in parallel"
---

# /hnsf:orchestrate-tasks

## Purpose
Plan and execute task groups with explicit routing and optional parallel execution.

## Required Inputs
- `tasks.md` in spec folder

## Expected Outputs
- `orchestration.yml` (execution plan)
- Implemented task groups
- Updated status.md

---

## PHASE 1: Resolve Tasks

Read `docs/specs/[this-spec]/tasks.md`

## PHASE 2: Create orchestration.yml

Generate single source of truth for execution:
```yaml
feature: [feature-name]
spec_path: docs/specs/[this-spec]/
groups:
  - name: [group-name]
    execution: sequential  # sequential | parallel
    phase: [phase-id]
    required_skills: [list]
    dependencies: [list]
```

## PHASE 3: User Assignments

Present orchestration plan. Ask:
- Execution mode per group (sequential/parallel)
- Any overrides to dependencies

## PHASE 4: Source-of-Truth Gate

Check open-questions.yml for pre-impl blockers → BLOCK if any

## PHASE 5: Execute

**Sequential mode**: Delegate each group in current session per implement-tasks flow.

**Parallel mode** (if worktree enabled):
1. Build dependency phases
2. Create worktree per parallel group
3. Spawn background tasks
4. Collect results
5. Merge in dependency order
6. Run integration tests
7. Cleanup worktrees

Apply `@references/worktree-protocol.md` for parallel execution.

## PHASE 6: Close Out

Update status.md with final results per group.
