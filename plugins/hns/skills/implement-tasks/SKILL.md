---
name: implement-tasks
description: Use to execute task groups from an hns tasks.md with verification gates — source-of-truth gate, session startup routine, implementer/verifier subagents, evidence recording, and post-implementation validation.
user-invocable: false
---

# implement-tasks

## 0. 게이트
1. `context/open-questions.yml` 에 `pre-impl` + `open` 이 있으면 **BLOCK** — 목록을 보여주고 해소를 요청한다.
2. `spec.md` 를 정본으로, `tasks.md` `context/key-decisions.md` 를 읽는다.
3. `hns:spec-evolution` 규칙이 구현 내내 활성이다.

## 1. 세션 시작 루틴
- **첫 세션**: `context/progress.md` 를 만든다(현재 그룹 · 완료 · 다음 단계 · 블로커).
- **이어가는 세션**(progress.md 있음): progress → `git log --oneline -10` → 이전 작업의 빌드/테스트를 한 번 돌려 깨진 상태가 아닌지 확인 → 기록된 다음 단계부터. 완료된 그룹은 다시 구현하지 않는다.
- 한 세션에 한 그룹씩 끝내는 것을 기본으로 한다. 세션 끝은 깨진 코드·미기록 변경이 없는 상태여야 한다.

## 2. 실행 방식
| 방식 | 언제 | 어떻게 |
|---|---|---|
| **Task-Group** (기본) | 작은~중간 기능 | 그룹마다 `hns:implementer` 에 위임(스펙 경로·그룹·이전 그룹 요약). 순차. |
| **Parallel** | 의존성 없는 그룹이 2개 이상 | 같은 위임을 `Agent` 도구로 동시에, 각각 `isolation: worktree`. 의존 순서로 머지, 충돌은 사용자에게. 통합 테스트 후 다음 단계. |
| **Step** | 그룹 6개 이상, step 간 간섭 최소화 | `references/step-execution-protocol.md`: tasks.md → `steps/step{N}.md`(자기완결) + `steps/index.json` 상태머신 → step 마다 새 서브에이전트 → 자가교정 3회 → step 별 커밋. 사용자가 Workflow 도구를 요청했으면 그것을 드라이버로 쓴다. |

## 3. 그룹 완료 절차
1. implementer 보고의 검증 명령을 **직접 다시 실행**하고 결과 줄을 `status.md` 에 기록한다.
2. 통과 시에만 `tasks.md` 체크박스를 표시한다.
3. 커밋: `feat({feature}): complete task group {N} — {name}`.
4. `context/progress.md` 갱신(완료·다음 단계). 결정은 `key-decisions.md`.
5. implementer 가 올린 open questions 를 `open-questions.yml` 에 분류해 넣는다.

## 4. 최종 검증
모든 그룹 후 `hns:verifier` 에이전트(fresh context) → `verifications/final-verification.md`. FAIL 이면 해당 그룹으로 돌아간다.

## 5. 구현 후 검증 (기본 ON, `--no-validate`)
`hns:validate --code` → `hns:drift-check` → `hns:validate --docs`. `hns:start` PHASE 7 과 같은 표.
`--wrapup` 이 있으면 `hns:wrapup`.

## Iron Laws
1. 검증 증거 없이 완료 없음.
2. pre-impl 미해결 상태로 구현 없음.
3. 3회 실패 → 중단·보고.
