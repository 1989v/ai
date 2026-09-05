# Harness Changelog

> evolve/diet/audit에 의한 하네스 변경 자동 기록

| Date | Type | Change | Rationale |
|------|------|--------|-----------|
| 2026-04-06 | init | v2 initial release | 6-layer architecture, doc-scaffolding merge, lifecycle layer |
| 2026-06-04 | audit→evolve | Step 모드(self-contained step + steps/ JSON 상태머신, 세션 내 subagent-per-step) + hns:start 구현방식 선택 + FE-slop A-9~A-12 (0.11.0) | jha0313/harness_framework `execute.py`의 step 분할·자가교정·상태머신 패턴 흡수 — 단 외부 python 드라이버 대신 세션 내 subagent 루프로 실현(무인 실행 제외) |
| 2026-06-16 | audit→evolve | Shape 단계 모호성 게이트(`ambiguity-gating-protocol.md`): Round 0 토폴로지 + 가중 모호성 점수 + 약한차원 단일질문 + 챌린지 모드(Contrarian/Simplifier/Ontologist) + 온톨로지 수렴 → hns:glossary 연계. spec-shaper 재작성, hns:start PHASE 1 게이트화, `--quick/--deep/--no-interview` 플래그, shaping-template.md (0.13.0) | oh-my-claudecode `deep-interview`(Ouroboros) 벤치마크 — omc 전용(.omc state/omc-plan/autopilot/ralph/team/autoresearch)은 드롭, hns 경로·calibrated tone·glossary 연계로 적응 |
| 2026-09-05 | audit→diet+evolve | **0.14.0** 모델 상향·플랫폼 2.1 재점검(ADR-005): 가짜 훅 3종 → 실제 스키마 훅 4종 + Stop 증거 게이트(주입 테스트·런타임 검증 완료) · commands 13 + 숨은 스킬 22 → 평탄 스킬 23(플러그인 skills/ 는 한 단계만 탐색, 실측) · 에이전트 10 → 5(spec-reviewer 신규, 6차원 병렬) · index.yml 라우팅·계층 위임·parallel-work.sh·config.yml 모드·컴팩션 리마인더·doc-html·interview-capture·orchestrate-tasks·verify-crosscheck 제거 · diet 는 세션 기록 사용 증거로, evolve 는 memory/rules/hook/CLAUDE.md 라우팅 · init 컨벤션 → `.claude/rules/` `paths:` | 세션 99건에서 `/hns:*` 직접 호출 0 · 에이전트 0 · `hns:start` 14; 훅 스키마 불일치; 플랫폼 내장(rules·worktree·skill-doctor·auto memory) |
