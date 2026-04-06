---
description: "[hns] Pre-implementation gate interview to surface missing assumptions"
---

# /hns:interview-capture

## Purpose
Surface missing assumptions and detect document-state drift before implementation.

## Required Inputs
- Spec folder path

## Expected Outputs
- Updated `context/open-questions.yml`
- `context/interview-capture.md`
- Gate result: BLOCKED or READY

---

## PHASE 1: Resolve & Detect Mode

1. Resolve spec folder
2. Check status.md: new feature or resume?
   - No status.md or early status → **New mode**
   - Existing progress → **Resume mode**

## PHASE 2: Source-of-Truth Check

Read all present documents. Record disagreements as pre-impl questions immediately.

## PHASE 3: Load Light Code Context

Read representative files (controller, service, test) — top 50 lines each.

## PHASE 4: Ask 5-7 Targeted Questions

From these buckets:

**Always applicable:**
- Actor/trigger: Who initiates this? What triggers it?
- Upstream inputs: What data do we receive? What format?
- Downstream persistence: What gets saved? Where?
- Failure semantics: What happens on failure? Retry? Idempotency?
- Out-of-scope boundary: What explicitly won't be handled?

**New mode additions:**
- Observability: How will we debug this?
- Verification floor: What's the minimum test coverage?

**Resume mode additions:**
- Closure unknowns: What's still open from previous work?
- Drift resolution: Who owns resolving detected drift?

## PHASE 5: Update open-questions.yml

- Append new questions with category classification
- Mark resolved items
- Categories: pre-impl, impl-discovery, test-discovery, closure, waiver-revisit

## PHASE 6: Write Summary

Write `context/interview-capture.md`:
1. Source-of-Truth Status
2. Questions and Findings
3. Confirmed Assumptions
4. Recommended Next Action

## PHASE 7: Gate Result

Emit exactly one:

**BLOCKED FOR IMPLEMENTATION**
```
Gate: BLOCKED
Reason: [N] pre-impl questions unresolved
Questions: [list]
Action: Resolve before proceeding to /hns:implement-tasks
```

**READY WITH DISCOVERIES TRACKED**
```
Gate: READY
Discoveries: [N] tracked in open-questions.yml
Action: Proceed to /hns:implement-tasks
```

This command MUST NOT exit without emitting a gate state.
