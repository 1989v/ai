---
name: gc
description: Use when performing garbage collection on the project — detects dead code, doc drift, rule violations, stale harness rules
---

# Garbage Collection

## Protocol
Follow `@references/gc-protocol.md` for scan modes and report format.

## Scan Checklist
- [ ] Dead code: 미사용 import, 빈 파일, 호출 없는 public 함수
- [ ] Doc drift: CLAUDE.md/docs 내용 vs 실제 코드 괴리
- [ ] Rule violation: agent-os/standards/ 규칙 vs 코드 위반
- [ ] Stale harness: 불필요한 규칙/스킬/훅 (→ diet 연계)

## Auto-fix Policy
- Dead imports → auto-remove (사용자 확인 불필요)
- Doc path typos → auto-correct
- 나머지 → 사용자 확인 필요

## Output
`harness-gc-report.md` in project root (overwritten each run)

## NEVER
- Auto-fix rule violations without user approval
- Delete files without explicit user confirmation
- Run full scan in light mode (light = changed files only)
