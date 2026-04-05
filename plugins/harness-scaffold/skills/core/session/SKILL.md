---
name: session
description: Use when starting a new session or recovering from compaction to load project context and key decisions
---

# Session Management

## Context Routing

### Level 0: Always Load
1. Read CLAUDE.md

### Level 1: Command-Specific
Each command declares `requires:` in frontmatter → load those files.

### Level 2: Keyword Matching
If `docs/index.yml` exists and command has `auto_reference: true`:
1. Extract keywords from current task description
2. Match against index.yml entries (threshold: 2+ keywords)
3. Load top 3 matched documents (prefer_section if available)
4. Load silently (no user notification)

## Session Start
1. Level 0: Read CLAUDE.md
2. Read agent-os/product/mission.md (if exists)
3. Check latest spec status in docs/specs/
4. Load active task context from tasks.md

## Post-Compaction Recovery
1. Level 0: Read CLAUDE.md
2. Read key-decisions.md
3. Read open-questions.yml
4. Check tasks.md checkboxes
5. git log recent commits

## Session End
- Ensure all changes committed
- Update status.md if applicable
