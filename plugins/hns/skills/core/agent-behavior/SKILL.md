---
name: agent-behavior
description: Use when starting any coding task, classifying risk, setting up verification loops, or performing post-implementation review
user-invocable: false
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

## 7. External Skill Isolation (HNS Pipeline Guard)

HNS 커맨드(`/hns:*`) 실행 중에는 외부 플러그인 스킬과의 충돌을 방지한다.

**HNS 파이프라인 활성 시**:
- HNS 자체 스킬만 사용 (agent-behavior, session, compaction, implementation 등)
- 외부 스킬(superpowers 등)은 자동 invoke하지 않음
- 기능이 겹치는 경우 HNS 스킬이 우선

**외부 스킬 사용이 필요한 경우**:
- 사용자에게 먼저 질의: "HNS 파이프라인 중입니다. {skill}을 추가로 사용할까요?"
- 사용자 승인 후에만 활용
- HNS와 충돌하지 않는 보조 기능에 한정 (예: debugging은 Ralph Loop 실패 후 보조로 가능)

**HNS 비활성 시 (일반 작업)**:
- 외부 스킬 자유롭게 사용 가능
- HNS 커맨드 호출 시점부터 격리 적용

| 겹치는 영역 | HNS 담당 | 외부 스킬 (사용자 승인 시만) |
|------------|----------|-------------------------|
| 브레인스토밍 | shape-spec | superpowers:brainstorming |
| 플랜 작성 | write-spec + create-tasks | superpowers:writing-plans |
| 구현 실행 | implement-tasks | superpowers:executing-plans |
| 검증 | verify + verify-crosscheck | superpowers:verification-before-completion |
| 코드 리뷰 | spec-review | superpowers:requesting-code-review |
| 워크트리 | implement-tasks worktree | superpowers:using-git-worktrees |

## 8. Subagent Usage Guidelines
Use subagents when tasks can run in parallel, require isolated context, or involve independent workstreams.
Work directly (no subagent) when:
- Single file read/edit
- Sequential operations sharing state
- Simple grep/glob lookup is sufficient
- Context continuity across steps is needed

## NEVER
- Start coding without checking key-decisions.md
- Repeat same approach in Ralph Loop
- Weaken/delete tests to pass
- Proceed with L3 changes without approval
- Continue retrying after 3 failures
- Spawn subagents for tasks a single tool call can handle
