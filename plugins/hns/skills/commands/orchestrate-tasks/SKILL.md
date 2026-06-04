---
user-invocable: false
---

# /hns:orchestrate-tasks

## Purpose
Plan and execute task groups with explicit routing and optional parallel execution.

## Required Inputs
- `tasks.md` in spec folder

## Expected Outputs
- `orchestration.yml` (execution plan)
- Implemented task groups
- Updated status.md

---

## PHASE 1: Resolve Tasks

Read `docs/specs/[this-spec]/tasks.md`

## PHASE 2: Create orchestration.yml

Generate single source of truth for execution:
```yaml
feature: [feature-name]
spec_path: docs/specs/[this-spec]/
groups:
  - name: [group-name]
    execution: sequential  # sequential | parallel
    phase: [phase-id]
    required_skills: [list]
    dependencies: [list]
```

## PHASE 3: User Assignments

Present orchestration plan. Ask:
- Execution mode per group (sequential/parallel)
- Any overrides to dependencies

## PHASE 4: Source-of-Truth Gate

Check open-questions.yml for pre-impl blockers → BLOCK if any

## PHASE 5: Execute

Choose execution mode per `@references/step-execution-protocol.md`. 모두 세션 내 동작.

**Task-Group mode** [기본]: Delegate each group in current session per implement-tasks flow (`status.md` 진행 추적).

**Parallel mode** (if worktree enabled):
1. Build dependency phases
2. Create worktree per parallel group
3. Spawn background tasks
4. Collect results
5. Merge in dependency order
6. Run integration tests
7. Cleanup worktrees

Apply `@references/worktree-protocol.md` for parallel execution.

**Step mode** [분할, step별 독립 컨텍스트]: `@references/step-execution-protocol.md` 적용.
1. **Self-Contained Step 생성**: tasks.md의 각 task group → `steps/step{N}.md` 1개로 변환 (`templates/steps/step-template.md`). 각 파일은 단독으로 읽고 실행 가능해야 함 — 읽을 파일·시그니처 수준 지시·AC 실행커맨드·구체적 금지 포함, 외부 참조 금지.
2. **상태 머신 생성**: `steps/index.json` (`templates/steps/index.json`) — task group 순서대로 `pending`.
3. **순차 실행**: 첫 `pending` step부터 `implementer`(+필요시 `tester`) subagent에 위임 (step 본문 + 가드레일 + 이전 step `summary` 누적). step마다 새 subagent = 독립 컨텍스트. AC 검증 → `index.json` 상태 기록 → 자가교정(max 3) → step별 커밋.
4. **resume**: `error`/`blocked` → 원인 수정 → `status`를 `pending`으로 → 재개.

## PHASE 6: Close Out

Update status.md with final results per group.
