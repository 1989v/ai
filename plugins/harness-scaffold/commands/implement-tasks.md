---
name: implement-tasks
description: "Execute task groups with verification gates and optional worktree isolation"
---

# /hns:implement-tasks

## Purpose
Execute task groups from tasks.md with verification gates.

## Required Inputs
- `tasks.md` in spec folder

## Expected Outputs
- Implemented code per task group
- Updated task checkboxes
- `verifications/final-verification.md`

---

## PHASE 0: Worktree Decision

Ask user: "Git worktree isolation per task group? (recommended for large groups) [y/N]"
If yes → apply `@references/worktree-protocol.md`

## PHASE 0.5: Source-of-Truth Gate

1. Establish canonical spec document
2. Read `context/open-questions.yml`
3. IF any `pre-impl` + `open` → **BLOCK**: "Pre-implementation questions must be resolved first"
4. List unresolved questions and ask user to resolve

## PHASE 1: Select Scope

Present task groups from tasks.md. Ask: "Which groups to implement? (all / specific numbers)"

## PHASE 1.5: Load Standards

1. Load from `agent-os/standards/` matching task keywords
2. Load `agent-os/product/tech-stack.md` for build/test commands

## PHASE 1.8: Skill Routing

Always load: `spec-evolution` skill (active during implementation)
Load additional skills from task metadata `required_skills`

## PHASE 2: Execute

For each selected task group (sequentially):
1. Delegate to `implementer` agent (production code)
2. Delegate to `tester` agent (test code)
3. Apply Ralph Loop: BUILD → TEST → FIX (max 3)
4. Record evidence in status.md
5. Mark checkboxes on pass

## PHASE 3: Final Verification

Delegate to `verifier` agent:
- Verify all tasks marked complete
- Run full test suite
- Create `verifications/final-verification.md`
