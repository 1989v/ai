---
name: verify
description: "[hns] Run verification suite: standards → lint → build → test with evidence recording"
---

# /hns:verify

## Purpose
Verify implementation against standards, lint, build, and tests. Record evidence.

## Required Inputs
- Feature spec path (e.g., `docs/specs/{feature}/`)

## Expected Outputs
- Updated `status.md` with verification evidence

---

## Step 1: Standards Verification

1. Load relevant standards from `agent-os/standards/`
2. Verify code compliance (architecture, conventions, error handling)
3. Record pass/fail with brief evidence
4. **Failure Policy**: Standards violations = **FAIL**

## Step 2: Lint Verification

1. Detect project linter from tech-stack.md (eslint, checkstyle, flake8, etc.)
2. Run linter
3. Record results
4. **Failure Policy**: Errors = **FAIL**, Warnings = **WARN**

## Step 3: Build Verification

1. Get build command from `agent-os/product/tech-stack.md`
2. Execute build
3. Record result
4. **Failure Policy**: Build failure = **FAIL**

## Step 4: Test Verification

1. Get test command from `agent-os/product/tech-stack.md`
2. Execute tests
3. Record result (total, pass, fail)
4. **Failure Policy**: Test failure = **FAIL**

## Step 5: Record Evidence

Update `docs/specs/{feature}/status.md`:

```markdown
## Verification [YYYY-MM-DD]

| Step | Result | Evidence |
|------|--------|----------|
| Standards | PASS/FAIL | [details] |
| Lint | PASS/WARN/FAIL | [details] |
| Build | PASS/FAIL | [output summary] |
| Test | PASS/FAIL | [N] tests, [N] failures |
```

## Failure Policy Summary

| Category | Level | Blocks? |
|----------|-------|---------|
| Standards violations | FAIL | Yes |
| Lint errors | FAIL | Yes |
| Lint warnings | WARN | No |
| Build failure | FAIL | Yes |
| Test failure | FAIL | Yes |

## Iron Law
Do not report success unless all FAIL-level checks pass.
Do not claim "tests pass" without actually running them.
