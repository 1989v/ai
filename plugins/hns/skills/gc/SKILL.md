---
name: gc
description: Use to run harness garbage collection — dead code, doc drift, rule violations, and stale harness items — via the gc-agent, producing harness-gc-report.md.
disable-model-invocation: true
argument-hint: "[--docs | --doctor]"
---

# /hns:gc

## Purpose
프로젝트의 코드/문서/하네스를 청소한다.

## Required Inputs
- Access to project root

## Expected Outputs
- harness-gc-report.md

---

## Protocol
Follow `@references/gc-protocol.md` for scan modes and report format.

## Modes

- `/hns:gc` — 전체 스캔 (아래 체크리스트 전부)
- `/hns:gc --docs` — 문서 drift 전용 서브플로우 (ADR-0023)
- `/hns:gc --doctor` — doctor 진단 연계. `doctor.py` 결과를 우선순위 입력으로 auto-fix

### `--docs` 서브플로우 순서

1. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_map.py` → lock 갱신
2. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_scan.py --base HEAD` → 영향 문서 리포트
3. 리포트 출력 (impacted docs, new sources, dangling docs)
4. 사람이 문서 수정 → `doc_map.py` 재실행 → lock 커밋

자동 아카이브/삭제 금지. orphan 탐지는 보고만.

### `--doctor` 서브플로우 순서

1. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py . --output-json docs/verify/DOCTOR_REPORT.json --output-md docs/verify/DOCTOR_REPORT.md`
2. `DOCTOR_REPORT.json`을 읽어 layer별 findings 분류
3. 우선순위 fix 순서: L3 broken-link → L1 index → L2 agent → L4 evidence
4. 배치 크기 제한: **1회 실행당 최대 20개 findings**
5. 남은 findings은 `docs/verify/DOCTOR_TODO.md`에 기록 → 다음 실행 시 HIGH 우선 처리
6. 변경사항 있으면 PR 생성, 없으면 `STALE_DOC_AUDIT.md`만 업데이트

**Idempotency**: 같은 입력이면 같은 결과. `DOCTOR_REPORT.*` 는 덮어쓴다.
자동 fix 전 사용자 확인 요청(파괴적 변경 방지).

## Scan Checklist
- [ ] Dead code: 미사용 import, 빈 파일, 호출 없는 public 함수
- [ ] Doc drift: CLAUDE.md/docs 내용 vs 실제 코드 괴리 (`--docs` 시 doc_map + doc_scan 파이프라인 사용)
- [ ] Rule violation: docs/standards/ 규칙 vs 코드 위반
- [ ] Stale harness: 불필요한 규칙/스킬/훅 (→ diet 연계)

## Auto-fix Policy
- Dead imports → auto-remove (사용자 확인 불필요)
- Doc path typos → auto-correct
- 나머지 → 사용자 확인 필요

## Execution

0. Delegate to `hns:gc-agent` with the mode and `${CLAUDE_PLUGIN_ROOT}/scripts` path
1. Perform full scan per `@references/gc-protocol.md`
2. Report generated at project root
3. User reviews and approves auto-fixes

## Output
`harness-gc-report.md` in project root (overwritten each run)

## NEVER
- Auto-fix rule violations without user approval
- Delete files without explicit user confirmation
- Run full scan in light mode (light = changed files only)
