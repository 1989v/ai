
# /hns:drift-check

## Purpose
Evaluate whether implementation has drifted from the active spec.

## Required Inputs
- Spec folder with spec.md and tasks.md

## Expected Outputs
- `context/drift-check.md`

---

## PHASE 1: Resolve Context

Read all available documents:
- spec.md, tasks.md, key-decisions.md, open-questions.yml, status.md

## PHASE 2: Gather Evidence

Grep-based search for referenced classes, APIs, state transitions.
Every finding MUST cite `{file}:{line}` — findings without citations are INVALID.

## PHASE 3: Evaluate 4 Lenses

**Lens A — Document-state drift**
- status.md vs tasks.md completion claims
- Learnings/review artifacts vs status

**Lens B — Contract drift**
- API shape, entity fields, state transitions vs spec
- Request/response schemas vs documented contracts

**Lens C — Verification drift**
- Test coverage per AC
- Tests for unspecified behavior
- Unresolved open questions

**Lens D — Decision drift**
- Code behavior vs key-decisions.md
- Non-trivial code paths without decision records

## PHASE 4: Classify

- **CRITICAL**: Breaks correctness or contracts
- **MAJOR**: Significant deviation, needs attention
- **MINOR**: Documentation gap, low risk

## PHASE 5: Write Report

Write `context/drift-check.md` with fixed sections:
- Executive Summary
- Critical/Major/Minor findings (each with file:line evidence)
- Evidence Table
- Recommended Next Action

## PHASE 6: Final Recommendation

Emit exactly one:
- **ALIGNED**: No drift detected
- **ALIGNED WITH AMENDMENTS NEEDED**: Minor drift, record amendments
- **NOT ALIGNED**: Significant drift, must address before proceeding
