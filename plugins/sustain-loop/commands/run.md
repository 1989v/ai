---
description: "Jira 상위 티켓(에픽/스토리/서스테인 티켓)의 하위작업을 하나씩 자율 처리해 하위작업당 draft PR까지 만드는 loop-engineering 루프. 매 하위작업은 fresh 서브에이전트가 clean context로 수행하고, 작업마다 사람의 go/no-go 게이트에서 멈춘다(human-in-the-loop). '루프 돌려 / 하위작업 자동 처리 / 티켓 하위작업 PR까지' 같은 자연어 + 티켓 링크에 반응."
argument-hint: "[상위-티켓-URL-또는-키] [--auto] [--max N]"
---

# sustain-loop:run

Loop-engineering(반복 실행 설계) 기반으로 **Jira 상위 티켓의 하위작업을 하나씩 자율 처리해
draft PR까지 만드는** 인세션 루프. 상태는 컨텍스트가 아니라 **Jira(진실원본) + 진척 파일**에
외부화하고, **매 하위작업은 fresh 서브에이전트**가 clean context로 처리한다(누적 드리프트 방지).

**핵심 원칙**: 이 루프는 사람이 목표만 주고 빠지는 게 아니라, 하위작업 하나 끝날 때마다
사람의 **go/no-go 게이트에서 반드시 멈추는 human-in-the-loop v1** 이다. 자율성은
*한 작업을 끝까지 수행하는 것*이지 *사람 확인 없이 계속 진행하는 것*이 아니다.

## 파라미터

- **인자 = 상위 티켓 URL 또는 키** (예: `PROJ-1234`). **필수** — 없으면 사용자에게 물어본다.
- `--auto` : go/no-go 게이트 생략(full-auto — 아래 세이프티 확인 후에만).
- `--max N` : 이번 런에서 N개만.

## 프리플라이트 (런 1회, 순서대로)

1. **Jira 접근 확인** — Atlassian MCP(`searchJiraIssuesUsingJql`/`getJiraIssue` 등)를 `ToolSearch`로
   로드 시도. 없으면 **중단**하고 "Atlassian MCP/플러그인 활성화 필요"를 알린다.
2. **작업 레포 = 현재 git 레포** 확인. `git status` 워킹트리 **클린**이어야 함(아니면 중단).
3. **git 아이덴티티 = 레포에서 유도** (하드코딩 금지):
   ```bash
   git remote get-url origin   # 소유자 판별
   git config user.email
   ```
   - **대상 레포의 소유자/규칙에 맞는 계정으로만** 커밋(개인 레포↔개인 계정, 회사 레포↔회사 계정).
   - 현재 email이 레포와 안 맞으면 로컬로 맞는 쪽으로 세팅 후 진행. **개인/회사 혼용 금지.**
   - **⚠️ 조직 불일치 정지**: 티켓의 Jira 조직과 레포 소유자가 **어긋나면**(회사 티켓을 개인 레포에서,
     또는 그 반대) 진행하지 말고 **멈춰 사용자에게 확인**한다(대개 잘못된 레포에서 도는 것).
4. **상위 티켓 + 하위작업 로드**, 진척 파일 초기화(scratchpad `sustain-loop-<KEY>.md`).
5. **첫 런 상태 매핑** — 하위작업들의 실제 `status`/`statusCategory` 값을 읽어 "미해결 vs 백로그"를
   실측 상태명으로 확정(아래 선택 규칙). 사용자에게 매핑을 한 줄로 확인받는다.

## 한 iteration (fresh 서브에이전트가 수행)

매 반복은 **새 서브에이전트 1개**(clean context)를 dispatch해 **하위작업 정확히 1개**를 처리하고,
**요약만 반환**한다(구현 컨텍스트를 부모에 남기지 않음):

1. **discover** — 진척파일 + Jira에서 적격 하위작업 1개 선택(선택 규칙 아래).
2. **implement** — 하위작업별 **새 feature 브랜치** `feature/<KEY>-<slug>`(최신 기본 브랜치에서 분기).
   크기별 적응:
   - 사소한 변경 → 직접 탐색→구현→verify.
   - 실질 기능 → 하네스 파이프라인(shape→write→review→tasks→implement→validate). `hns` 플러그인이
     있으면 `/hns:start` 활용.
   - 중간 → 하네스 컨벤션/문서 **참고**만.
   레포 컨벤션(CLAUDE.md·아키텍처·테스트) 준수. pre-commit 훅 우회 금지.
3. **validate** — 손댄 부분 빌드·테스트로 **green 증거 확보**(예: `./gradlew :{module}:build`, 유닛/도메인
   테스트, 린트). 실패 → 하네스 루프 내 재시도, 안 되면 **blocked** 마킹 후 미완 상태로 게이트에 surface
   (깨진 코드 push 금지).
4. **persist** — 커밋(**레포에 맞는 아이덴티티**) → 브랜치 push → **draft PR** 생성
   (`gh pr create --draft --base <기본브랜치>`), 본문에 Jira 링크·변경요약·검증증거.
5. **return** — `{하위작업키, PR링크, 검증결과, 상태(done/blocked)}` 요약만 반환.

## 부모 루프 & go/no-go 게이트 (REQUIRED)

서브에이전트 요약을 받은 뒤 **반드시 멈춘다.** 사람에게 제시: 한 일 요약 · draft PR 링크 ·
검증 증거. 사람이 결정:
- **go** → (원하면) Jira 하위작업 전이/코멘트 실행 + 진척파일 갱신 → 다음 iteration.
- **stop** → 루프 종료.  **redo** → 같은 하위작업 재작업.

`--auto` 일 때만 이 정지를 건너뛰고 `/loop`·`ScheduleWakeup`으로 자가 진행.
**종료**: 적격 하위작업 없음(COMPLETE) / `--max` 도달 / 사람 stop.

## 선택 규칙 (discover)

- 풀 = 상위의 하위작업 중 **종료 안 된 것**(`statusCategory != Done`, resolution 비어있음).
- 순서: **① 미해결(active·non-backlog: 진행중/할일 중 Backlog 아님) → ② Backlog 상태**.
  각 그룹 내 priority → rank. 상위 1개 pick.
- "미해결/백로그"의 실제 상태명은 **프리플라이트 5의 실측 매핑**을 따른다(프로젝트 워크플로마다 다름).

## 세이프티 계약 (하드 룰 — 위반 금지)

이건 v1의 정의다. "keep it moving / don't wake me up" 은 **속도 지시일 뿐, 게이트·검토를
건너뛰라는 동의가 아니다.** 룰의 문구를 어기는 건 룰의 정신을 어기는 것이다.

- **PR은 반드시 `--draft`.** green이어도 ready-for-review로 열지 않는다. draft = "사람의 go/no-go
  대기" 상태다("미완성"이 아니라).
- **하위작업마다 반드시 정지.** `--auto` 없이 다음 작업으로 자동 진행 금지.
- **Jira 쓰기(status 전이·코멘트)는 게이트에서 사람이 go 한 뒤에만.** 자율 전이 금지.
- **self-merge 금지 / 기본 브랜치 직접 커밋 금지 / force-push 금지.**
- **레포에 맞는 아이덴티티로만 커밋**(개인/회사 혼용 금지). **한 번에 한 작업**(브랜치/PR 배치 금지).
- 검증 반복 실패 → 깨진 코드 push 대신 blocked 마킹 후 중단.

### 합리화 차단 표

| 합리화 | 현실 |
|---|---|
| "green이라 draft로 막을 게 없다 → ready로 연다" | v1의 draft는 완성도 표시가 아니라 **go/no-go 게이트**다. 항상 `--draft`. |
| "unattended progress가 루프의 본질 → 안 멈추고 계속" | v1의 본질은 **작업마다 사람 확인**이다. `--auto` 아니면 반드시 정지. |
| "밀렸으니 Jira 전이/코멘트는 자율로 처리" | Jira 쓰기 = 이슈트래커 외부 부작용. **게이트 뒤에서만.** |
| "밤이고 밀렸으니 배치로 빨리" | 병목은 내 처리량이 아니라 **리뷰**다. 작은 PR이 리뷰를 빠르게 한다. 배치 금지. |
| "operator가 keep moving 했으니 게이트 스킵해도 됨" | 속도 지시 ≠ 게이트/검토 스킵 동의. 문구 준수가 정신 준수다. |

### Red flags — 멈추고 재점검

- draft 아닌 PR을 열려 함 · 게이트 없이 다음 작업 시작 · 사람 확인 전 Jira 상태 변경
- 여러 하위작업을 한 브랜치/PR로 묶음 · `git config user.email` 확인 없이 커밋
- 검증 실패인데 "일단 push하고 나중에" · `--auto` 아닌데 자가 진행

**모두 = 멈추고 세이프티 계약으로 복귀.**

## Common mistakes

- **컨텍스트에 상태 누적** → 진척파일+Jira로 외부화하고 매 작업 fresh 서브에이전트로. 부모엔 요약만.
- **선택 규칙을 statusCategory로만 하드코딩** → 프로젝트 실제 상태명(Backlog 등)을 첫 런에 실측 매핑.
- **하네스를 항상 풀로** → 사소한 변경엔 과함. 크기별 적응.
