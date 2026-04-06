---
name: compaction
description: Use when context usage exceeds 75%, completing a task group, or transitioning between phases
user-invocable: false
---

# Strategic Compaction

## When to Compact
- Task Group completion
- Spec document completion
- Phase transitions

## When NOT to Compact
- During implementation
- During test debugging
- During critical decision discussions

## Pre-Compact Checklist
- [ ] git commit current work
- [ ] Record decisions in key-decisions.md
- [ ] Save progress state to `docs/specs/{feature}/context/progress.md`:
  - Current task group and step
  - What was completed this session
  - What to do next (specific, actionable)
  - Blockers or open issues
- [ ] Confirm next task clarity
- [ ] Verify work completion

## Recovery (Post-Compact)
1. Read CLAUDE.md
2. Read docs/specs/{feature}/context/key-decisions.md
3. Read docs/specs/{feature}/context/open-questions.yml
4. Read docs/specs/{feature}/context/progress.md (if exists)
5. Check tasks.md checkboxes
6. git log recent commits

## NEVER
- Compact during implementation
- Resume work without recovery
