# Harness Changelog

> evolve/diet/audit에 의한 하네스 변경 자동 기록

| Date | Type | Change | Rationale |
|------|------|--------|-----------|
| 2026-04-06 | init | v2 initial release | 6-layer architecture, doc-scaffolding merge, lifecycle layer |
| 2026-06-04 | audit→evolve | Step 모드(self-contained step + steps/ JSON 상태머신, 세션 내 subagent-per-step) + hns:start 구현방식 선택 + FE-slop A-9~A-12 (0.11.0) | jha0313/harness_framework `execute.py`의 step 분할·자가교정·상태머신 패턴 흡수 — 단 외부 python 드라이버 대신 세션 내 subagent 루프로 실현(무인 실행 제외) |
