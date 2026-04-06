---
name: doc-validate
description: "Validate CLAUDE.md and docs/ against actual codebase"
requires: []
auto_reference: false
---

# /hns:doc-validate

## Purpose
CLAUDE.md와 docs/가 실제 코드 구조와 일치하는지 검증한다.

## Required Inputs
- CLAUDE.md and docs/ must exist

## Expected Outputs
- Validation report (PASS/WARN/FAIL per check)

---

Load `hns:doc-validate` skill and execute all checks.
Output report to terminal.
