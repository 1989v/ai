---
name: create-tasks
description: "Break down a spec into actionable task groups with dependencies"
---

# /hnsf:create-tasks

## Purpose
Create a task breakdown from a spec for implementation.

## Required Inputs
- `spec.md` and/or `planning/requirements.md`

## Expected Outputs
- `tasks.md` in the spec folder

---

## PHASE 1: Read Spec

Read `docs/specs/[this-spec]/spec.md` and `planning/requirements.md`.

## PHASE 2: Load Standards

1. IF `docs/index.yml` exists → keyword match → load relevant standards
2. Load `agent-os/standards/` applicable rules

## PHASE 3: Create Tasks

Delegate to `tasks-list-creator` agent with:
- Spec and requirements
- Standards context
- Visual assets (if present)
- Output contract: verification sub-tasks, execution metadata, <= 600 lines

## Completion

```
Tasks created: [spec-folder]/tasks.md

Next:
- /hnsf:interview-capture (recommended pre-implementation gate)
- /hnsf:implement-tasks (start implementation)
- /hnsf:orchestrate-tasks (plan execution order)
```
