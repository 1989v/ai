---
name: write-spec
description: "Create comprehensive specification from shaped requirements"
---

# /harness-scaffold:write-spec

## Purpose
Create a comprehensive specification for a feature from shaped requirements.

## Required Inputs
- Spec folder with `planning/requirements.md` (from /harness-scaffold:shape-spec)

## Expected Outputs
- `spec.md` in the spec folder

---

## PHASE 1: Load Context

1. Resolve spec folder (user-provided or most recent `docs/specs/YYYY-MM-DD-*/`)
2. IF `docs/index.yml` exists → keyword match → load related docs
3. IF `context/open-questions.yml` exists → include unresolved pre-impl items as context

## PHASE 2: Write Spec

Delegate to `spec-writer` agent with:
- Documentation context from Phase 1
- `planning/requirements.md`
- `planning/visuals/` (if present)
- Quality contract: Overview 30s readable, independent sections, <= 400 lines

## Completion

```
Spec written: [spec-folder]/spec.md

Next: /harness-scaffold:create-tasks to break down into implementable tasks
```
