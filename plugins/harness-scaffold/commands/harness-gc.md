---
name: harness-gc
description: "Run garbage collection — detect dead code, doc drift, rule violations, stale harness"
requires:
  - agent-os/standards/global/conventions.md
auto_reference: true
---

# /harness-scaffold:harness-gc

## Purpose
프로젝트의 코드/문서/하네스를 청소한다.

## Required Inputs
- Access to project root

## Expected Outputs
- harness-gc-report.md

---

## Execution

1. Load `hns:gc` skill
2. Delegate to `hns:gc-agent`
3. Agent performs full scan per `@references/gc-protocol.md`
4. Report generated at project root
5. User reviews and approves auto-fixes
