# sustain-loop

Loop-engineering 기반 **Jira 상위 티켓 → 하위작업 → PR** 자율 루프 플러그인.

상위 티켓(에픽/스토리/서스테인 티켓)의 하위작업을 **하나씩** 처리한다. 각 하위작업은
**fresh 서브에이전트**가 clean context로 수행(누적 드리프트 방지)하고, 상태는 컨텍스트가 아니라
**Jira + 진척 파일**에 외부화한다. 하위작업 하나가 끝나면 **draft PR**을 만들고, 다음 작업으로
넘어가기 전 **사람의 go/no-go 게이트에서 멈춘다**(human-in-the-loop v1).

## 사용

```
/sustain-loop:run <상위-티켓-URL-또는-키> [--auto] [--max N]
```

또는 자연어 + 티켓 링크: "이 티켓 하위작업 루프 돌려서 PR까지 만들어줘".

- `--auto` : 작업 간 게이트 생략(full-auto). 세이프티 계약 확인 후에만.
- `--max N` : 이번 런에서 N개만.

## 한 iteration

`discover(미해결→백로그) → implement(크기별 적응 하네스) → validate(green 증거) →
draft PR → go/no-go 게이트에서 정지`

## 전제

- **Jira 접근**: Atlassian MCP(`searchJiraIssuesUsingJql`/`getJiraIssue` 등) 연결 필요.
- **PR**: `gh` CLI.
- **하네스**(선택): `hns` 플러그인이 있으면 실질 기능 구현에 `/hns:start` 파이프라인 활용.

## 세이프티

draft PR 게이트 · 작업마다 정지 · Jira 쓰기는 게이트 뒤 · self-merge/기본 브랜치 직접 커밋/force-push
금지 · **레포에 맞는 git 아이덴티티로만 커밋**(개인/회사 혼용 금지) · Jira 조직과 레포 소유자가
어긋나면 정지·확인 · 검증 반복 실패 시 중단.

## 기반 개념

- **Loop engineering** — 에이전트를 반복 호출하는 루프 설계(하네스를 감싸는 바깥 계층).
- **Ralph 패턴** — fresh-context 반복 + 상태 외부화(git/진척파일).
