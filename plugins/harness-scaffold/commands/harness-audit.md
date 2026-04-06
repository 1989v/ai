---
name: harness-audit
description: "Compare current harness against external benchmarks — repos, posts, best practices"
requires: []
auto_reference: false
---

# /harness-scaffold:harness-audit

## Purpose
외부 소스와 비교하여 하네스 개선 기회를 식별한다.

## Required Inputs
- External source (URL, repo path, or "auto" for web search)

## Expected Outputs
- docs/benchmarks/YYYY-MM-DD-{source}.md

---

## Execution

1. Load `hns:audit` skill
2. Ask user for source (or use "auto" for web search)
3. Analyze source's harness structure
4. Compare with current harness-scaffold
5. Generate benchmark report
6. User decides adoption → delegate to `/harness-scaffold:harness-evolve`
