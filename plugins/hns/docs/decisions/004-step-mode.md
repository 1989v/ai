# ADR-004: Step 모드 (세션 내 step별 독립 컨텍스트 실행)

**Date**: 2026-06-04
**Status**: Accepted
**Source**: `/hns:audit` → `docs/benchmarks/2026-06-04-jha0313-harness-framework.md`

## Context

jha0313/harness_framework(영상 "빈 프로젝트에서 하네스 직접 만들기")의 정체는 `scripts/execute.py` 하나 — step마다 별도 `claude -p` 프로세스를 띄워 컨텍스트를 리셋하고, 요약을 누적 전달하며, 자가 교정하고, JSON 상태 머신으로 재개하는 헤드리스 멀티세션 드라이버다.

HNS는 풍부한 기획/리뷰/라이프사이클을 갖췄으나, 구현 실행은 한 세션 안의 subagent 위임(task group 단위)뿐이었다. step 많은 큰 작업에서는 부모 세션 컨텍스트가 누적·부패하고, step간 간섭을 줄일 방법이 없었다.

## Decision

`execute.py`의 **step 분할 · 자가교정 · 상태머신** 패턴을 흡수하되, **외부 python 드라이버는 채택하지 않는다.** 그 가치(step별 독립 컨텍스트)는 Claude Code의 **세션 내 subagent**가 이미 제공하기 때문이다. python이 필요한 유일한 이유였던 "무인/CI 실행"은 현재 사용자 워크플로(대화형)에 해당하지 않는다.

1. **구현 실행을 2개 모드로** — `@references/step-execution-protocol.md`:
   - **Task-Group 모드**(기본): 기존 `implement-tasks` 흐름. 작은~중간 기능.
   - **Step 모드**: tasks.md → self-contained `steps/step{N}.md` 변환 → step마다 새 subagent(독립 컨텍스트)로 순차 실행. `steps/index.json` 상태머신 + 자가교정(max 3) + step별 커밋.
2. **`hns:start` PHASE 5에서 모드 선택** — 승인 게이트에서 [1] Task-Group / [2] Step 질의.
3. **상태머신 병행** — `steps/index.json`(기계용, resume) + `status.md`(사람용 노트).

## Consequences

**+** step 많은 큰 작업에서 step별 컨텍스트 격리 → 부패 방지 / 결정론적 resume / step간 간섭 최소화.
**+** python 의존·`--dangerously-skip-permissions` 안전성 부담 없음 — 전부 세션 내, 권한 프롬프트 정상 동작.
**+** 기본(Task-Group) 무변경 — regression 없음.
**−** 진짜 무인/CI 실행은 제공하지 않음 (의도적 제외 — 필요해지면 그때 외부 드라이버 재도입 검토).
**−** Step 모드는 tasks.md→steps 변환 단계가 추가됨 (오버헤드, 큰 작업에서만 가치).

## Not Adopted

- **외부 python step-runner (`execute.py` 직접 포팅)** — 무인 실행 외 가치는 세션 내 subagent로 대체 가능. 미사용 기능을 미완 상태로 남기지 않기 위해 제거.
- `--dangerously-skip-permissions` 기본화 (confirmation Level 철학과 충돌)
- 5파일 미니멀화 (6차원 리뷰/라이프사이클은 핵심 가치)
- Next.js 전제 템플릿 (HNS는 스택 중립)
