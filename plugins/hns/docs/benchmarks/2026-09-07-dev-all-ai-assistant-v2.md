# 벤치마크: myrealtrip/dev-all-ai-assistant-v2

**Date**: 2026-09-07 · **Source**: 사내 레포(비공개), 클론 대조 · **결과**: 0.16.0 (ADR-007)

## 대상
서버·웹·Android·iOS **6+레포 크로스플랫폼 오케스트레이터**. 스킬 29 · 훅 8 · 에이전트 8 · 규칙 5 · 순회 스크립트 6.
구조는 **머리/손 분리** — dev-all(머리)이 계획·계약·결정화·dispatch 를 하고, 하위 `harness/kernel/execute.py`(손)가
대상 레포의 fresh 세션에서 코딩+빌드+AC 를 돌린다. 종료 상태 3종(completed/error/blocked), work-order 는 Stranger Test 통과가 조건.

## 비교 요약

| 축 | dev-all | hns (0.15.1) |
|---|---|---|
| 파이프라인 | prd-interview → impact → api-design → tech-plan-write → **tech-plan-review** → 승인 → jira/branch → dispatch → **superpower-review** → PR | shape → spec → **spec-review(6차원 병렬)** → tasks → implement → validate |
| 실행 격리 | 외부 프로세스 커널(`claude -p`), step 상태머신 | 세션 내 subagent, Step 모드 상태머신 |
| 코딩 전 검수 | tech-plan-review 4차원(의도는 메인, 나머지 fresh) | spec-review 6차원 fresh 병렬 |
| 코딩 후 검수 | 멀티 라운드 적대 리뷰 + **판정 에이전트 분리** | fresh 1회, 발견·판정 겸함 |
| 학습 루프 | 리뷰 발견 → 승격 심판 → `code-check-list` → **코딩 시 주입 + 리뷰 시 사냥** | evolve → rules/hook/memory (구현 프롬프트로 안 돌아옴) |
| 상태 | 4파일 + 순회 조언 스크립트 | `progress.md` + `steps/index.json` |
| 사용자 | 개발자/비개발자 2모드, Jira·PR 라이프사이클 | 단일 |

**뼈대는 이미 같다.** 결정화된 자기완결 step·AC=실행 커맨드·3회 자가교정·상태머신 resume 은 hns Step 모드가
같은 계보에서 이미 흡수했다(벤치마크 2026-06-04). 베낄 게 있는 곳은 **뼈대가 아니라 세 축**이었다.

## 채택 (→ ADR-007, 0.16.0)

| # | 개념 | 출처 | hns 반영 |
|---|---|---|---|
| A | 발견 ≠ 판정 분리 · 소집 불가 시 정지 · 기존 패턴 강등 | `superpower-review/execution-flow.md` 3단계, `adversarial-reviewer` 헌법 5, 사고 #12 | `agents/review-verdict.md` 신설 · `spec-review` 3단계 · `agent-behavior` §4 · `review-protocol` Finding Discipline |
| B | 코드 체크리스트 SSOT(코딩 주입 + 리뷰 사냥) · 승격 심판 · 출처 보존 · soft cap | `update-code-check-list`, `code-check-judge` | `/hns:code-check` 신설 · `docs/checks/` · implementer 2-b · `review-protocol` Stage 3 |
| C | 산문→코드화 3분류 · 못 막는 금지는 표기 의무로 | `dev-all-repo-update-workflow.md`, 사고 #13 | `evolve` 두 절 |
| D | 빼기 규칙 ④⑤ (4시점 전이 · 예외 경로 축소 먼저) | CLAUDE.md 원칙 9, 사고 #11 | `evolve` 절차 2·3 + NEVER |
| E | 커밋 스코프 가드 | `harness-dispatch` ④-pre | `templates/hooks/scripts/commit-scope.sh` |

**A 의 근거가 가장 날카롭다** — "부실한 수정은 다음 라운드가 재검출하지만, 기각은 같은 재량이 반복 적용된다."
라운드를 늘려도 못 잡는 유일한 편향이라 판정자를 분리한 것.

**C 의 사고 #13 은 하네스 설계 일반 원칙이다** — 강제 장치 없는 금지문("시안 없으면 dispatch 금지")이
석 달간 작동하지 않았고(step 파일 503개 중 준수 9개), 아무도 몰랐다. 처방은 금지를 지우는 게 아니라
**표기 의무로 낮춰 어긴 사실을 산출물에 남기는 것**. hns 의 "훅은 빨간불을 본 뒤에만 켰다고 한다" 의 다음 문장.

**E 는 이 레포에서 살아 있는 문제였다** — 대조 작업 중 msa 의 `submodule-auto-push.sh` 가 `git add -A` 로
파일 4개를 한 커밋에 쓸어담고 그 중 한 파일 이름으로 메시지를 달았다. 사용자 메모리에도 같은 사고 2건
(`rebase-leaves-submodule-worktrees-behind`, `shared-worktree-concurrency`).

## 미채택 + 사유

| 항목 | 사유 |
|---|---|
| work-order + 외부 `execute.py` 커널 | Step 모드가 이미 흡수. python 드라이버를 다시 넣으면 상태 소유권이 둘로 갈린다 |
| `next-step.py` 순회 조언자 | 슬라이스×레포 **이중 루프**라 산문으로 감당이 안 된 산물. hns 는 단일 축 — 조기 최적화. **분류 체계(C)만** 채택 |
| 4파일 상태 모델 · `progress.py` | 멀티 레포 × 멀티 세션의 산물. `progress.md` + `steps/index.json` 으로 충분 |
| 소통 모드 · Jira 라이프사이클 · repo-registry/context · 크로스레포 순차 실행 | 조직 구조 대응물. msa 엔 대응 개념 없음 |
| handoff 파일(사실만 3~5줄) | implementer 보고의 "Notes for next group" 이 같은 자리를 차지. 휘발성이 문제로 드러나면 그때 파일로 |
| 규모 축소 레인(quick-fix) | 판정 기준("겉보기 크기가 아니라 위험·파일수·로직여부")까지 좋지만, hns 는 Query/Feature 분기가 아직 아프지 않다 |
| 자기 변경 검토 + 조건부 시뮬 3렌즈 | **가장 아까운 미채택.** 기계 검사·정적 검토가 전부 초록인 상태에서 시뮬만 게이트 뚫림 3건을 발견했다. 훅을 계속 손대는 중이라 값어치가 있으나, 이번 변경 자체가 안전장치를 건드려 같은 세션에서 자기검증이 되는 순환 — 다음 라운드로 |

## 다음
조건부 3건(handoff · 축소 레인 · 자기 변경 검토)은 실사용에서 아픔이 관측될 때 재평가.
`docs/checks/` 는 첫 항목이 쌓이기 전까지 무동작이므로, 다음 구현 후 리뷰에서 유지된 발견을 첫 후보로 태운다.
