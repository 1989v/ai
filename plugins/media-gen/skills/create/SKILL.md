---
name: create
description: Use when the user wants AI-generated media — a transformation short from a person's photo, game character sheets or backgrounds, a stylized image, a wallpaper — or before calling any Higgsfield MCP tool.
when_to_use: 변신 영상, 숏폼 만들어, 캐릭터 디자인 뽑아, 배경 이미지 생성, 힉스필드, Genjutsu, motion transfer, 미디어 생성
argument-hint: "<shortform-transform|game-character|game-background|image|background-photo> [--out DIR]"
---

# media-gen — 미디어 생성 파이프라인

인물 사진 변신 숏폼, 게임 캐릭터·배경, 이미지, 배경 사진을 **같은 네 단계**로 만든다.
장르는 `references/genres/<장르>.md` 의 프롬프트 파일만 다르다.
생성 자체는 MCP(힉스필드 등)나 사용자의 웹 UI 가 한다 — 이 스킬은 **입력을 갖추고, 비용을 알리고,
정체성을 고정한 프롬프트를 만들고, 결과를 검수하는** 절차다.

## 하드 룰

1. **필수 리소스 없이 생성 단계로 가지 않는다.** `intake.py new` 가 종료 코드 2 를 내면 거기서 멈추고
   사용자에게 없는 것을 요청한다. 자리 표시자·추정 이미지로 대신하지 않는다.
2. **유료 호출 전에 비용표를 보이고 사용자가 고른다.** 승인 기록(`approval.json`)은 사용자의 답을 받은
   **뒤에만** `budget.py approve` 로 쓴다. 힉스필드 도구는 이 기록이 없으면 플러그인 훅이 거부한다 —
   우회하지 않는다(승인 기록을 미리 쓰는 것이 우회다).
3. **원본에 없는 것을 지어내지 않는다.** 의상·색·소품·헤어는 입력 이미지와 사용자가 말한 목표만 근거로 쓴다.
   프롬프트의 정체성 고정 블록(얼굴·나이·체형 비율)은 장르 파일의 것을 **그대로** 쓰고 주제 슬롯만 채운다.
4. 인물 사진은 외부 서비스로 올라간다 — 본인·가족 사진만, 인테이크에서 그 사실을 한 줄 알린다.

이 스킬이 도는 동안 superpowers 의 brainstorming 같은 외부 프로세스 스킬은 자동 호출하지 않는다.

## 파일

- `P=${CLAUDE_PLUGIN_ROOT}` · `INTAKE="python3 $P/scripts/intake.py"` · `BUDGET="python3 $P/scripts/budget.py"` (`--help`)
- 단가표 `$P/scripts/pricing.json` (검증일 · 모델별 크레딧 · 무료 경로) — 단일 원본
- 작업 폴더 `$MEDIA_GEN_HOME`(기본 `~/media-gen`)`/<날짜>-<슬러그>/` — `inputs/` `outputs/` `job.json` `estimate.md` `approval.json` `job.md`
- 훅 `$P/hooks/guard-higgsfield.py` — `mcp__*higgsfield*` 유료 도구를 승인 기록 없이는 deny
- 장르 파일 `$P/references/genres/` · 프로바이더 `$P/references/providers.md` · 검수 `$P/references/review-checklist.md`

## 절차

### ① 인테이크 — 리소스를 한 번에 받는다

1. 장르를 정한다(인자 또는 요청에서). 모호하면 다섯 중 하나를 고르게 한다.
2. `$INTAKE requirements --genre <장르>` 출력(필수/선택 표)을 **그대로** 사용자에게 보이고, 빠진 것을
   **한 번에** 요청한다 — 첨부 이미지는 보고 판단하는 데는 쓰되, 생성 도구에 넘기려면 **로컬 경로**가 있어야
   한다. 첨부만 있으면 경로를 받는다.
3. 다 모이면 `$INTAKE new --genre … --slug … --source … [--ref-video …] [--concept "…"] [--aspect …]`
   (인자 `--out DIR` 는 `--home DIR` 로 넘긴다).
   종료 코드 2 → 하드 룰 1. 경고(짧은 변 512px 미만 · 20KB 미만 자리 표시자 의심 · 영상 3~30초 밖)는
   사용자에게 보이고 진행 여부를 묻는다.
4. 인물이 있으면 원본 사진을 `Read` 로 열어 **아이덴티티 카드**를 `job.md` 에 적는다 — 성별·나이대·헤어(길이/색/스타일)·
   피부톤·얼굴 특징(안경·점·눈매)·체형 비율(유아/아동/성인 프로필 중 하나)·사진 속 옷. 이 카드가 모든 프롬프트의 근거다.

### ② 프로바이더·비용 — 부르기 전에 얼마인지 안다

1. `ToolSearch "+higgsfield"` 로 실제 도구를 찾는다. 없으면 `references/providers.md` 의 다른 접두어를 시도하고,
   아무것도 없으면 **₩0 수동 경로**만 남는다(설치 안내는 providers.md).
2. 찾은 도구의 스키마를 읽고 셋을 확인한다 — 입력이 **경로인가 URL 인가**(URL 이면 providers.md 의 업로드 절차),
   **잔액·비용 조회 도구**가 있는가(있으면 그 값이 `pricing.json` 을 이긴다 — 표를 갱신한다), 결과를 받는 방법.
   처음 보는 도구 목록은 providers.md 의 표에 적어 둔다.
3. 장르 파일의 단계 표대로 `plan.json` 을 쓴다 — `[{"stage","model","count"}]`. count 는 **1차 시도 횟수**다
   (재시도 여유는 스크립트가 ×1.5 로 얹는다).
4. `$BUDGET estimate --provider higgsfield --plan plan.json --job <작업 폴더>` 출력을 **그대로** 보인다.
   종료 코드 3(단가표 오래됨) → 요금 페이지를 `WebFetch` 로 확인해 `pricing.json` 의 `verified`·단가를 고친 뒤 다시.
   종료 코드 4(모르는 모델) → 도구 스키마·요금표에서 단가를 찾아 추가한 뒤 다시.
5. `AskUserQuestion` 으로 (a) MCP 유료 (b) 구독 잔량 (c) ₩0 수동 (d) 중단 을 고르게 한다.
   - (a)/(b) → `$BUDGET approve --job <작업 폴더> --calls <견적의 승인 요청 횟수> --answer "<사용자 답 원문>"`.
     잔액 도구가 있으면 잔액 ≥ 견적인지 먼저 본다.
   - (c) → ③ 에서 호출 대신 **프롬프트·순서·웹 UI 경로**를 `job.md` 에 써서 넘긴다.
   - (d) → `job.json` 의 `status` 를 `cancelled` 로 두고 끝낸다.

### ③ 생성 — 단계마다 검수한다

장르 파일의 단계 순서대로. 단계마다:

1. 프롬프트 = 장르 파일 템플릿 + 아이덴티티 카드 + 입력 이미지 역할(IMAGE 1/IMAGE 2/REFERENCE VIDEO). 쓴 프롬프트는
   `outputs/<단계>-prompt.txt` 로 남긴다.
2. 호출 → 작업 대기(폴링 도구) → 결과를 `outputs/<단계>-<n>.<ext>` 로 받는다.
3. `references/review-checklist.md` 로 검수한다 — 이미지는 `Read` 로 열어 항목을 하나씩 본다. 판정과 근거를
   `job.md` 에 쓰고, 결과를 사용자에게 보여 **OK 를 받은 뒤** 다음 단계로 간다.
4. 재생성은 **바꿀 것 하나**를 정해서 한다(프롬프트 한 줄 또는 입력 이미지). 승인 횟수를 다 쓰면 훅이 막는다 —
   ② 로 돌아가 다시 견적·승인.

수동 경로(c)면 이 단계는 「사용자가 웹 UI 에서 만든 결과 파일을 `outputs/` 에 넣어 주면 검수」로 바뀐다.

### ④ 기록

`job.md` 에 산출물 목록(경로·해상도·길이), 실제 쓴 호출 수(`approval.json` 의 `calls`)와 크레딧(잔액 도구가 있으면
전후 차이), 쓴 프롬프트 링크, 검수 결과, 다음에 같은 인물·캐릭터로 만들 때 **재사용할 앵커 이미지**를 적는다.
`job.json` 의 `status` 를 `done` 으로.

## 산출물 계약 (사용자에게 보이는 것)

| 시점 | 반드시 보이는 것 |
|---|---|
| ① 끝 | 작업 폴더 경로 · 받은 입력 표(정규 이름 ← 원본, 해상도/길이) · 경고 · 아이덴티티 카드 |
| ② 끝 | 비용 견적 표 원문 + 선택지 넷 · 선택 결과와 승인 횟수 |
| ③ 각 단계 | 결과 파일 경로 · 검수 판정(항목별 ○/×) · OK 여부 질문 |
| ④ | 산출물 표 · 실제 호출 수/크레딧 · 재사용 앵커 |

## 흔한 실수 (스킬 없는 기준선에서 실제로 난 것)

| 실수 | 대신 |
|---|---|
| 레퍼런스 영상 없이 사진 한 장으로 image-to-video 한 번 | 숏폼은 **IMAGE 1 → IMAGE 2 → 모션 트랜스퍼** 세 단계. 영상이 움직임 담당이다 |
| "요금을 몰라서 숫자를 안 낸다" | `pricing.json` 이 있다. 오래됐으면 확인해서 갱신하고 낸다 |
| 프롬프트에 "흰 세일러복·파란 칼라" 처럼 원본에 없는 의상을 넣는다 | 변신 후 모습은 IMAGE 2 가 정의한다. 프롬프트는 "exactly as shown in IMAGE 2" |
| 작업 폴더·프롬프트 기록 없이 채팅에만 남긴다 | `intake.py new` 가 폴더를 만든다. 프롬프트는 `outputs/*-prompt.txt` |
| 승인 없이 호출하거나, 승인 기록을 먼저 써 둔다 | 하드 룰 2 — 훅이 막고, 우회는 규칙 위반이다 |
