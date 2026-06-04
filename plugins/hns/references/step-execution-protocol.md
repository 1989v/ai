# Step Execution Protocol

구현 실행의 두 가지 방식(mode)을 정의한다. 둘 다 **대화형 세션 안**에서 동작하며 별도 스크립트가 필요 없다.

> 출처: jha0313/harness_framework `execute.py`의 step 분할·자가교정·상태머신 패턴을 흡수하되, 세션 외부 python 드라이버 대신 **세션 내 subagent 루프**로 실현. 벤치마크: `docs/benchmarks/2026-06-04-jha0313-harness-framework.md`.

## 두 가지 모드

| | **Task-Group 모드** (기존/기본) | **Step 모드** (분할) |
|---|---|---|
| 실행 단위 | task group (tasks.md 그대로) | self-contained step 파일 |
| 컨텍스트 | implementer/tester subagent가 부모 세션 맥락 위에서 작업 | step마다 새 subagent = **독립 컨텍스트**, 가드레일+이전요약만 주입 |
| 적합 | 작은~중간 기능, 같이 보며 진행 | step 많은 큰 작업, step간 간섭 최소화하고 싶을 때 |
| 상태 추적 | `status.md` (서술) | `steps/index.json` (상태 머신) + `status.md` |

둘 다 무인 실행이 아니다 — 권한 프롬프트·확인은 평소처럼 사람이 응답한다. Step 모드의 이점은 "무인"이 아니라 **step별 컨텍스트 격리 + 결정론적 resume**이다.

## Step 모드 실행 절차 (세션 내)

### 1) Step 파일 생성 (tasks.md → steps/)
각 task group을 `steps/step{N}.md` 1개로 변환 (`templates/steps/step-template.md`). 규칙:
1. **Scope 최소화** — step당 1레이어/1모듈. 여러 모듈이면 쪼갠다.
2. **자기완결성** — "이전 대화에서 논의한 대로" 외부 참조 금지. 필요 정보 전부 파일 안에.
3. **사전 준비 강제** — 읽을 파일 경로(이전 step 산출물 포함) 명시.
4. **시그니처 수준 지시** — 인터페이스만, 구현은 에이전트 재량. 단 핵심 불변식(멱등성·보안·무결성)은 명시.
5. **AC = 실행 가능 커맨드** — 추상 서술 금지. `./gradlew build && test` 같은 실제 커맨드.
6. **구체적 금지** — "조심해라" 대신 "X 하지 마라. 이유: Y".

`steps/index.json` 생성 (`templates/steps/index.json`) — task group 순서대로 `pending`.

### 2) 순차 실행 루프
`index.json`의 첫 `pending` step부터:
1. **subagent 위임** — `implementer`(+필요시 `tester`)에게 위임. 프롬프트 = `step{N}.md` 본문 + 가드레일 + 이전 완료 step의 `summary` 누적. subagent는 자기 컨텍스트에서 실행.
2. **AC 검증** — step에 적힌 검증 커맨드 실행.
3. **상태 기록** — `index.json` 업데이트:
   - 통과 → `completed` + `summary`(산출물 한 줄: 생성 파일·핵심 결정) + `completed_at`
   - 3회 수정 후 실패 → `error` + `error_message` → **중단**
   - 사용자 개입 필요(API키·인증·수동설정) → `blocked` + `blocked_reason` → **중단**
4. **자가 교정** — 실패 시 직전 `error_message`를 다음 시도 프롬프트에 피드백, 최대 3회.
5. **커밋** — step 완료마다 `feat({phase}): step {N} — {name}` 커밋 (체크포인트).

### 3) Resume
- `error`: 원인 수정 → 해당 step `status`를 `pending`으로, `error_message` 삭제 → 재개
- `blocked`: `blocked_reason` 해결 → `pending`으로, `blocked_reason` 삭제 → 재개
- 이미 `completed`인 step은 재실행하지 않음.

## 상태 머신 (`steps/index.json`)

```json
{
  "project": "<name>", "phase": "<task-name>",
  "steps": [ { "step": 0, "name": "core-types", "status": "pending" } ]
}
```

| status | 의미 | 기록 |
|--------|------|------|
| `pending` | 미실행 | — |
| `completed` | AC 통과 | `completed_at`, `summary` |
| `error` | 3회 후 실패 | `failed_at`, `error_message` |
| `blocked` | 휴먼 게이트 | `blocked_at`, `blocked_reason` |

`status.md`(서술형 진행 노트)와 **병행** — 기계용 상태 머신(resume) + 사람용 노트의 역할 분리. (2026-04-06 벤치마크 "structured state + unstructured notes" 원칙.)

## 가드레일 주입

step subagent 프롬프트에는 cwd→repo_root의 `CLAUDE.md` + `docs/` 규칙을 누적 주입 (`@references/hierarchical-delegation.md` 정합). 가장 가까운 것이 우선, root는 base.
