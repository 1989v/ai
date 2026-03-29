---
name: spec-writing
description: Use when writing spec.md documents - defines structure, quality contracts, and documentation-only constraints
---

# Spec Writing Rules

## spec.md Structure
1. **Goal** (1-2 sentences)
2. **User Stories** (As a [user], I want...)
3. **Specific Requirements** (SR-N sections, max 8 sub-items each)
4. **Visual Design** (if mockups exist)
5. **Existing Code to Leverage**
6. **Out of Scope**

## Quality Contract
- Overview readable in 30 seconds
- Sections independently readable
- No duplication across sections
- Target: <= 400 lines
- No actual code in spec (describe requirements only)

## Context Loading
1. If `docs/index.yml` exists → keyword match → load related specs/standards
2. Fallback: scan `agent-os/standards/` directly
3. Check `context/open-questions.yml` → include unresolved pre-impl items as context

## Documentation References
- Load top 3 related specs at README level
- Load top 2 references at full content
- Load matching standards

## NEVER
- Write actual code in spec.md
- Exceed 400 lines without justification
- Leave TBD/TODO placeholders
- Duplicate information across sections
