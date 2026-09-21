---
name: artifact-catalog
description: Use when the user wants to see, list, group, search or refresh the catalog of Claude artifacts their account has published — "아티팩트 목록", "아티팩트 카탈로그", "발행한 아티팩트 정리·갱신", "artifact catalog" — or right after publishing a new artifact that the catalog page should now include.
argument-hint: "[--no-publish]"
---

# Artifact Catalog — 발행한 아티팩트의 등록부와 카탈로그 페이지

`Artifact list` 는 **최근 50건 창**만 보여 주고 그 밖은 사라진다. 이 스킬은 볼트별 `claude/artifact/catalog.json` 을
**누적 등록부**로 유지하고, 볼트마다 프로젝트별 섹션 + 검색이 되는 카탈로그 페이지 한 장을 발행한다.

## 하드 룰 — 회사와 개인은 섞이지 않는다

등록부도 페이지도 **볼트 단위**다. 회사 볼트의 아티팩트와 개인 볼트의 아티팩트는 같은 `catalog.json` 에도,
같은 페이지에도 들어가지 않는다. 「전체」 혼합 페이지는 만들지 않는다.
이건 문서 규칙이 아니라 구조다 — 페이지 설정은 `vault` **하나**만 받고, `vaults` 목록이나 다른 볼트를
가리키는 값은 스크립트가 시작 전에 거부한다. 우회해서 합치지 않는다.
분류가 모호한 아티팩트는 추정하지 말고 사용자에게 묻는다 — 공개용 개인 페이지에 회사 것이 실리는 쪽이
개인 것이 회사 페이지에 실리는 것보다 나쁜 실수다.

## 계속 동기화 — 이 플러그인이 켜져 있는 동안

이 플러그인이 설치·활성인 세션에서는 **이후에 발행되는 아티팩트가 빠짐없이 카탈로그로 들어간다.** 장치는 셋이다.

- **발행 훅** `hooks/on-artifact-publish.sh` (PostToolUse · `Artifact`) — `publish` 가 끝날 때마다
  `catalog.py record` 로 **대기열**(`~/.claude/artifact-catalog.queue.json`)에 적는다. 셸이 결정론적으로 하므로
  세션이 잊어도 남고, `Artifact list` 의 50건 창과 무관하다. 제목은 발행 파일의 `<title>`, 볼트는 작업 레포의
  origin 소유자(설정 `owners`, 예: `1989v → 1989v`, `myrealtrip → work`)로 미리 채운다 — 레포 밖이면 비워 둔다.
  이미 등록된 것의 재발행은 갱신일만 올린다. `list`·`read`·에셋 업로드·**카탈로그 페이지 자신의 재발행**에는 침묵한다.
  같은 호출이 세션 컨텍스트에 「/artifact-catalog 를 돌려라」도 넣는다.
- **Stop 훅** `hooks/on-stop.sh` — 대기열에 등록부에 없는 항목이 남아 있으면 **세션 종료를 막는다**(`decision: block`).
  「지시만 넣는」 버전은 지켜지지 않아서 넣었다. 한 번 막아 이어진 턴(`stop_hook_active`)은 통과시켜 무한 루프를 막고,
  `ARTIFACT_CATALOG_STOP_GATE=off` 로 끌 수 있다. 카탈로그에 안 넣기로 한 것은 `catalog.py queue --drop <id>` 로 뺀다.
- **이 스킬** — 카탈로그 페이지는 `Artifact` 도구로만 다시 발행되므로 이 절반은 세션 몫이다. sync 가 대기열을
  후보에 합치고, assign 이 등록부에 넣으며 대기열을 비운다. 같은 세션에서 여러 번 발행해도 **마지막에 한 번**이면 된다.

발화 여부를 확인하려면 `ARTIFACT_CATALOG_HOOK_LOG=<파일>` 을 환경에 두고 세션을 연다 — 호출마다 한 줄 남는다.

## 파일

- 설정 `~/.claude/artifact-catalog.json` (`$ARTIFACT_CATALOG_CONFIG` 로 바꿀 수 있다):
  `vaults.<name> = <볼트 경로>`, `pages.<page> = { title, vault }` (페이지당 볼트 하나),
  `owners.<github owner> = <name>` (선택 — 발행 훅이 작업 레포로 볼트를 미리 고른다)
- 대기열 `~/.claude/artifact-catalog.queue.json` (`$ARTIFACT_CATALOG_QUEUE`) — 발행 훅이 쓰고 assign 이 비운다.
  볼트 밖에 두는 이유: 볼트를 아직 모르는 항목(레포 밖 발행)도 잃지 않으려고
- 등록부 `<볼트>/claude/artifact/catalog.json` — `entries[]` + 그 볼트 페이지의 `pages.<page> = URL`
- 읽기 전용 입력 `<볼트>/claude/artifact/index.md` — 발행일·노트 링크·이모지의 출처이자, 새 항목이 **어느 프로젝트 줄기인지** 볼
  선례. 이 스킬은 여기에 쓰지 않는다(사용자 하네스의 볼트 사본 규칙이 카탈로그 페이지 행을 넣는 것은 그 규칙의 몫이고, sync 가 걸러 낸다)
- 훅 `${CLAUDE_PLUGIN_ROOT}/hooks/on-artifact-publish.sh`(PostToolUse `Artifact`) · `on-stop.sh`(Stop) — `hooks/hooks.json`
- 스크립트 `${CLAUDE_PLUGIN_ROOT}/scripts/catalog.py` — 아래에서 `CAT` 으로 줄여 쓴다:
  `CAT="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/catalog.py"` (`$CAT --help`). 템플릿 `templates/catalog.html`

설정이 없으면 볼트 경로와 페이지 구성을 사용자에게 묻고 먼저 만든다.

## 절차

작업 폴더 `W` 는 세션 스크래치패드 아래 `artifact-catalog/` — **절대 경로**로 잡고 `mkdir -p` 한다.

1. **목록 저장** — `Artifact` 도구 `action: list`, `limit: 50` 을 부르고 결과 텍스트를 **그대로** `W/list.txt` 에 쓴다
   (`- (mine) 제목 — URL — updated 날짜` 줄을 스크립트가 읽는다. 제목에 ` — ` 가 있어도 된다).
2. **sync** — `$CAT sync --list W/list.txt --out W`
   기존 항목의 갱신일·URL 형식은 여기서 바로 반영되고, **처음 보는 것만** `W/pending.json` 에 남는다.
   발행 훅이 넣어 둔 대기열 항목도 여기 합쳐진다(`source: hook`, vault 는 훅이 채운 값) — 목록 창 밖이어도 들어온다.
3. **pending 채우기** — 비어 있으면 건너뛴다. 항목마다:
   - `vault`: null 이면 정한다. 판정 기준은 아티팩트의 **주제가 어느 볼트 소유인가**(회사 시스템·티켓·사내 지표 → 회사 볼트,
     개인 프로젝트 → 개인 볼트). 모호하면 위 하드 룰대로 묻는다.
   - `project`: **필수**. sync 가 찍어 준 「쓰던 프로젝트명」을 먼저 재사용한다 — 어느 이름인지는 **선례로 정한다**:
     같은 볼트 `catalog.json` 에서 비슷한 제목이 어느 프로젝트에 있는지, `index.md` 제목의 괄호 주석이 같은 줄기를
     가리키는지 본다(예: 게임이 게임마다 프로젝트를 갖고 있으면 새 게임도 제 이름으로). 새 이름은 산출물 종류가 아니라
     **제품·주제 이름**으로 2~4어절 (「전란」「검색 인프라」— 「시안」「분석」이 아니다).
   - `sameAs`: 목록 항목과 `source: index` 행이 제목만 다른 **같은 아티팩트**면, 목록 쪽 항목에
     `"sameAs": "<index 행 id>"` 를 넣는다. assign 이 발행일·노트·이모지를 흡수하고 행을 합친다.
   - 선택: `tags[]`, `summary`(한 줄), `icon`(**이모지 하나** — 등록부의 icon 은 index.md 에서 오는 이모지와 같은 자리다.
     5단계 Artifact 도구의 `icon` 인자와는 다른 것이다).
   확인 표는 sync 표에 `project` 열을 더한 것(`vault · project · published · source · title`), 볼트별로 나눠 보여 준다.
   사용자에게 **한 번** 확인받은 뒤 `$CAT assign W/pending.json`.
   빈 `project`·모르는 `vault` 는 스크립트가 거부한다.
4. **build** — `$CAT build --out W` → 페이지마다 `W/<page>.html` 과 `page → URL | (첫 발행)` 한 줄.
5. **publish** — `--no-publish` 면 여기서 멈추고 파일 경로를 알린다. 아니면 페이지마다:
   - URL 이 있으면 `Artifact` `publish` 에 `file_path` + `url` (같은 주소 갱신, `icon` 생략)
   - `(첫 발행)` 이면 `publish` 에 `file_path` + `icon: "catalog"`(도구 인자, 단어) + 한 문장 `description`, 결과 URL 을
     `$CAT page-url <page> <URL>` 로 기록한다 — 안 하면 다음 실행이 새 아티팩트를 또 만든다.
6. **보고** — 페이지별 URL · 건수 · 이번에 새로 들어간 항목. 사용자 하네스에 「발행 즉시 볼트 사본」 규칙이 있으면
   각 페이지의 사본은 **그 페이지의 볼트에만** 남긴다.

## 하지 않는 것

- `index.md` 를 고치지 않는다. 등록부에만 쓴다. (볼트 사본 규칙이 거기 카탈로그 행을 넣는 건 별개고, sync 가 URL·제목으로 걸러 낸다)
- 등록부에서 항목을 지우지 않는다 — 삭제된 아티팩트도 「있었다」는 기록이다. 필요하면 사용자가 직접 뺀다.
- 카탈로그 페이지 자체는 등록부에 넣지 않는다 — sync 가 기록된 URL·설정 제목으로 거른다.
- 두 볼트의 내용을 섞어 한 볼트·한 페이지에 쓰지 않는다 (위 하드 룰).
