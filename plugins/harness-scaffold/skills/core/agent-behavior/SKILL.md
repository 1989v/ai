---
name: agent-behavior
description: Use when starting any coding task, classifying risk, setting up verification loops, or performing post-implementation review
---

# Agent Behavior Protocols

## 0. Unified Rules
- CLAUDE.md overrides AGENTS.md on conflict
- Explore evidence first — never infer without docs/code

## 1. Pre-Work Checklist
1. Read `docs/specs/{feature}/context/key-decisions.md` (if exists)
2. Read `docs/specs/{feature}/spec.md`
3. Read `docs/specs/{feature}/tasks.md` → confirm current task
4. Check `agent-os/standards/` → matching standard
5. If unclear → ask specific question

## 2. Risk Classification

| Level | Task Type | Action |
|-------|-----------|--------|
| **L1** | 리팩토링, 포맷, 주석, 문서 | Auto-proceed + build check |
| **L2** | 신규 파일, 메서드 시그니처, 테스트 추가 | Auto-proceed + Ralph Loop |
| **L3** | 비즈니스 로직, 도메인 개념, 아키텍처 변경 | **WAIT for human approval** |

## 3. Ralph Loop (L2/L3)
```
MAX_RETRIES = 3
LOOP:
  1. BUILD → fail → FIX
  2. TEST → pass → EXIT (success)
  3. ANALYZE → root cause
  4. FIX → different approach
  5. ITERATION++ → if >= 3 → EXIT (escalate)
```

Failure Classification:
- Execution Failure (Mock, parsing) → fix in loop
- Implementation Failure (404, 500, spec mismatch) → STOP immediately

## 4. Self-Review
- L1/L2: Run project linter
- L3 (quality mode): Fresh Context Reviewer subagent
- L3 (efficient mode): Inline checklist
- Verdict: SHIP / REVISE (max 2) / BLOCK

## 5. Doc Impact Scan
Changed file keywords → agent-os/standards/ match → report related docs

## 6. Decision Recording
```md
### [YYYY-MM-DD] Decision Title
- **Decision**: what  - **Reason**: why
- **Evidence**: docs/code  - **Impact**: affected files
```
Location: `docs/specs/{feature}/context/key-decisions.md`

## NEVER
- Start coding without checking key-decisions.md
- Repeat same approach in Ralph Loop
- Weaken/delete tests to pass
- Proceed with L3 changes without approval
- Continue retrying after 3 failures
