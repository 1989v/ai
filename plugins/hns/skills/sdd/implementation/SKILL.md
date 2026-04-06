---
name: implementation
description: Use when implementing task groups from tasks.md - defines source-of-truth gates, Ralph Loop, and verification
user-invocable: false
---

# Implementation Rules

## Source-of-Truth Gate (MUST before implementation)
1. Read `context/open-questions.yml`
2. Check for `category: pre-impl` + `status: open`
3. If any exist → **BLOCK** (do not proceed until resolved)
4. Read spec.md as canonical reference
5. Read tasks.md for current assignment
6. Read key-decisions.md for prior decisions

## Standard Loading
1. Read `agent-os/standards/` relevant to current task
2. Read `agent-os/product/tech-stack.md` for build/test commands
3. Apply conventions from `agent-os/standards/global/`
4. Load `spec-evolution` skill (always active during implementation)

## Verification Loop (per Task Group)
Apply Ralph Loop from agent-behavior skill:
```
BUILD → TEST → ANALYZE → FIX (max 3 iterations)
```

After each group completion:
1. Run verification command from tasks.md
2. Record evidence (command + output) in status.md
3. Mark task group checkbox only on PASS

## Spec-Evolution Monitoring
Active during ALL implementation:
- New edge case discovered → open-questions.yml immediately
- Correctness gate triggered → amendment consideration
- Never silently fix spec drift in code only

## Final Verification
After all groups complete:
- Run `/hns:verify` or equivalent
- Create `verifications/final-verification.md`
- Update status.md with comprehensive evidence

## Iron Laws
1. **No completion without verification evidence**
2. **No implementation with pre-impl questions unresolved**
3. **Ralph Loop 3 failures → immediate STOP and escalate**

## NEVER
- Implement with pre-impl questions open
- Skip verification evidence recording
- Claim completion without running tests
- Ignore spec-evolution discoveries
- Continue after 3 Ralph Loop failures
