# Harness Changelog

> evolve/diet/audit에 의한 하네스 변경 자동 기록

| Date | Type | Change | Rationale |
|------|------|--------|-----------|
| 2026-04-06 | init | v2 initial release | 6-layer architecture, doc-scaffolding merge, lifecycle layer |
| 2026-06-04 | audit→evolve | Step 모드(self-contained step + steps/ JSON 상태머신, 세션 내 subagent-per-step) + hns:start 구현방식 선택 + FE-slop A-9~A-12 (0.11.0) | jha0313/harness_framework `execute.py`의 step 분할·자가교정·상태머신 패턴 흡수 — 단 외부 python 드라이버 대신 세션 내 subagent 루프로 실현(무인 실행 제외) |
| 2026-06-16 | audit→evolve | Shape 단계 모호성 게이트(`ambiguity-gating-protocol.md`): Round 0 토폴로지 + 가중 모호성 점수 + 약한차원 단일질문 + 챌린지 모드(Contrarian/Simplifier/Ontologist) + 온톨로지 수렴 → hns:glossary 연계. spec-shaper 재작성, hns:start PHASE 1 게이트화, `--quick/--deep/--no-interview` 플래그, shaping-template.md (0.13.0) | oh-my-claudecode `deep-interview`(Ouroboros) 벤치마크 — omc 전용(.omc state/omc-plan/autopilot/ralph/team/autoresearch)은 드롭, hns 경로·calibrated tone·glossary 연계로 적응 |
