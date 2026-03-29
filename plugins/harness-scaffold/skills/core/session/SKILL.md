---
name: session
description: >
  Use when starting a new session or recovering from compaction.
  Loads project context, active task state, and key decisions.
compatibility: claude-code
---

# Session Management

## Session Start
1. Read CLAUDE.md
2. Read agent-os/product/mission.md (if exists)
3. Check latest spec status in docs/specs/
4. Load active task context from tasks.md

## Post-Compaction Recovery
1. Read CLAUDE.md
2. Read key-decisions.md
3. Read open-questions.yml
4. Check tasks.md checkboxes
5. git log recent commits

## Session End
- Ensure all changes committed
- Update status.md if applicable
