<!-- source: plugins/hns/commands/start.md -->
<!-- source: plugins/hns/scripts/doctor.py -->

# hns@0.10.0 — Hierarchical Delegation + MCP Surface Diagnostic

- **Status**: in-progress
- **Date**: 2026-05-13
- **Target version**: `0.9.0 → 0.10.0`
- **Driver**: msa 모노레포 16 서비스 × 각자 `CLAUDE.md` 구조에서 sub-context 누락 + 미사용 MCP 서버의 컨텍스트 비용 가시화

## Origin

- ZeroCho TV "OpenAI Codex 하네스 엔지니어링 실습 요약본" (`https://youtu.be/MpeuOAmctAg`) 시청 후 분석
- OpenAI 공식 정의 "Harness engineering" 의 핵심 컴포넌트 5개(Context Files / MCP Servers / Skill Files / Mechanical Enforcement / Feedback Loops) 중 hns에서 비어있던 2개를 도입
- revfactory `harness` 6 팀 아키텍처 패턴 중 hns 미구현 패턴(계층적 위임)을 일급 패턴으로 승격

## P1 — Hierarchical Delegation

### Problem
`/hns:start` PHASE 0 Context Loading이 root `docs/`만 읽는다. msa 같은 모노레포에서 cwd가 `order/app/...` 인데 spec/review/tasks 단계가 `order/CLAUDE.md` + `order/docs/`를 자동 흡수하지 않음 → 서비스 로컬 규칙 누락.

### Solution
Context Routing에 **Level 0.5: nearest-ancestor CLAUDE.md + docs/** 추가. cwd → root 까지 거슬러 올라가며 발견되는 모든 `CLAUDE.md` 와 인접 `docs/index.yml` 을 누적 로드. 가장 가까운 것이 우선 적용 (root는 base, sub는 override).

### Changes
- `plugins/hns/commands/start.md` — PHASE 0 에 Step 6 추가
- `plugins/hns/references/hierarchical-delegation.md` — 신규 프로토콜 문서

### Verify
- msa `order/` 안에서 `/hns:start` 실행 시 컨텍스트에 `order/CLAUDE.md` 가 포함되는지 (로그 확인)
- root만 있는 단일 모듈 프로젝트에서는 기존과 동일 동작 (regression 없음)

## P2 — MCP Surface Diagnostic

### Problem
`/hns:doctor` 4 레이어가 문서/하네스 정합성만 본다. 활성 MCP 서버 × 도구 × 추정 컨텍스트 비용은 측정되지 않아, 미사용 MCP가 매 세션 토큰을 먹는지 알 수 없음.

### Solution
Doctor 에 **L5 MCP Surface** 추가:
- `.claude/settings.json`(local·project) 의 `mcpServers` / `enabledPlugins` 파싱
- 서버별 도구 개수, 추정 스키마 토큰(보수적 휴리스틱: 도구당 ~150 토큰)
- 총합이 임계치(기본 6000 토큰) 초과면 WARN

### Weight Redistribution (총합 100 유지)
| Layer | Before | After |
|---|---|---|
| L1 Index Integrity | 30 | 27 |
| L2 Agent Guidance | 25 | 23 |
| L3 Harness Alignment | 25 | 23 |
| L4 Evidence Coverage | 20 | 17 |
| L5 MCP Surface | — | 10 |

### Changes
- `plugins/hns/commands/doctor.md` — L5 행 + Triage 항목 추가
- `plugins/hns/scripts/doctor.py` — `_check_mcp_surface()` 함수 + LAYERS 갱신 + weight 재분배
- `plugins/hns/.claude-plugin/plugin.json` — `0.9.0 → 0.10.0`

### Verify
- `python3 plugins/hns/scripts/doctor.py .` 가 L5 행을 출력
- ai 레포 자체에 적용 시 활성 MCP 서버 목록 표시
- 도구 0개 또는 settings.json 부재 시 정보 표시(FAIL 아님, INFO/PASS)

## Out of Scope
- 동적 MCP 호출 빈도 측정(세션 로그 의존)은 Phase 2
- Codex AGENTS.md 듀얼 런타임 지원(사용자가 명시적 제외)
- 베이스라인 자기 측정(`/hns:bench --self`), Ralph Loop resume — 별도 spec

## Release Plan
- C1: P1 구현 (start.md + hierarchical-delegation.md)
- C2: P2 구현 + version bump (doctor.md + doctor.py + plugin.json)
- push to `1989v/ai` main
- 사용자 캐시 갱신 안내
