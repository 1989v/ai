---
user-invocable: false
---

# /hns:implement-tasks

## Purpose
Execute task groups from tasks.md with verification gates.

## Required Inputs
- `tasks.md` in spec folder

## Expected Outputs
- Implemented code per task group
- Updated task checkboxes
- `verifications/final-verification.md`

---

## PHASE 0: Worktree Decision

Ask user: "Git worktree isolation per task group? (recommended for large groups) [y/N]"
If yes → apply `@references/worktree-protocol.md`

## PHASE 0.5: Source-of-Truth Gate

1. Establish canonical spec document
2. Read `context/open-questions.yml`
3. IF any `pre-impl` + `open` → **BLOCK**: "Pre-implementation questions must be resolved first"
4. List unresolved questions and ask user to resolve

## PHASE 0.8: Session Type Detection

Determine current session type:

**First Window** (no prior progress):
- Create `context/progress.md` with initial state
- Set up verification scripts if needed (e.g., `./verify.sh`)
- Focus on foundation task groups first

**Continuation Window** (progress.md exists):
- Read `context/progress.md` → resume from recorded next step
- Run quick smoke test on prior work before continuing
- Do NOT re-implement completed groups

## PHASE 1: Select Scope

Present task groups from tasks.md. Ask: "Which groups to implement? (all / specific numbers)"

## PHASE 1.5: Load Standards

1. Load from `agent-os/standards/` matching task keywords
2. Load `agent-os/product/tech-stack.md` for build/test commands

## PHASE 1.8: Skill Routing

Always load: `spec-evolution` skill (active during implementation)
Load additional skills from task metadata `required_skills`

## PHASE 2: Execute

For each selected task group (sequentially):
1. Delegate to `implementer` agent (production code)
2. Delegate to `tester` agent (test code)
3. Apply Ralph Loop: BUILD → TEST → FIX (max 3)
4. Record evidence in status.md
5. Mark checkboxes on pass

## PHASE 3: Final Verification

Delegate to `verifier` agent:
- Verify all tasks marked complete
- Run full test suite
- Create `verifications/final-verification.md`

## PHASE 4: Post-Implementation Validation (Optional)

> 기본 ON. `--no-validate` 옵션 또는 `/hns:start --no-validate`로 스킵 가능.

구현 완료 후 3단계 검증을 자동 수행:

### Step 1: Code Validation (`hns:validate --code`)
- 아키텍처 원칙 준수 (domain에 Spring 의존성 없음 등)
- 패키지 네이밍 컨벤션
- 테스트 규칙 준수

### Step 2: Drift Check (`hns:drift-check`)
- 구현 코드가 spec.md와 일치하는지
- 스펙에 없는 기능 추가 또는 누락 여부

### Step 3: Docs Sync (`hns:validate --docs`)
- 새 모듈/인프라가 CLAUDE.md, README.md, docs/에 반영되었는지

### Validation Report

```
## Post-Implementation Validation — {date}

| Step | Result | Details |
|------|--------|---------|
| Code Validation | PASS/WARN/FAIL | [summary] |
| Drift Check | PASS/WARN/FAIL | [summary] |
| Docs Sync | PASS/WARN/FAIL | [summary] |

Overall: PASS / NEEDS_ATTENTION
```

- **PASS**: 모든 검증 통과
- **NEEDS_ATTENTION**: WARN/FAIL 항목에 대해 수정 옵션 제안

## PHASE 5: Session Wrapup (Optional)

> 기본 ON. `--no-wrapup` 옵션으로 스킵 가능.

PHASE 4까지 완료 후 `/hns:wrapup`을 자동 호출하여 세션 회고 + 셀프힐링을 수행:

1. 세션 데이터 수집 (progress.md, 커밋, 검증 리포트)
2. 실패 패턴 분류 (코딩실수/아키텍처위반/스펙부족/도구오용/프롬프트품질)
3. LOW 리스크 → evolve 자동 호출 (사용자 승인)
4. 회고 문서 생성 (`docs/retrospectives/{date}-session.md`)
