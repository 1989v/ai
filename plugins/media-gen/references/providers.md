# 프로바이더 — MCP 탐색 · 입력 방식 · 힉스필드 메모

스킬은 도구 이름을 하드코딩하지 않는다. **실행 때 실제로 붙어 있는 도구를 찾고 스키마를 읽는다.**
아래 표는 그때 채운다 — 비어 있으면 아직 아무 세션도 실제 도구를 본 적이 없다는 뜻이다.

## 탐색 절차

1. `ToolSearch "+higgsfield"` → 없으면 `"+fal"`, `"+replicate"`, `"+kling"`, `"+runway"` 순으로.
2. 찾은 도구마다 스키마에서 셋을 읽는다:
   - **입력 방식** — 이미지·영상 인자가 로컬 경로를 받나, URL 만 받나, 업로드 도구가 따로 있나
   - **비용 신호** — 잔액(balance/credits) 조회 도구, 호출 결과에 소모 크레딧이 찍히는지
   - **결과 수령** — 동기 응답에 URL 이 오나, job id 를 받아 폴링하나(그 도구 이름), 다운로드 도구가 있나
3. 처음 보는 도구 목록은 아래 표에 적는다. 다음 실행이 여기서 시작한다.

### 힉스필드 실제 도구 표 (첫 인증 실행 때 채운다)

| 도구 | 종류(조회/유료) | 이미지 입력 | 결과 | 비고 |
|---|---|---|---|---|
| _(아직 없음)_ | | | | |

훅 `hooks/guard-higgsfield.py` 는 **이름이 get/list/search/wait/download… 로 시작하면 조회, 나머지는 유료**로 본다.
새 도구 이름이 이 규칙과 어긋나면(조회인데 다른 동사로 시작) 훅의 `READ_ONLY_VERB` 에 그 동사를 더하고 테스트를 돌린다.

## 로컬 파일 → URL

커뮤니티 힉스필드 MCP(`QalaLabs/claude-higgsfield-mcp`)는 이미지·영상을 **공개 HTTPS URL 로만** 받는다.
공식 MCP 도 같으면 업로드 단계가 필요하다. 순서:

1. 도구 자체 업로드가 있으면 그것.
2. 없으면 **Google Drive MCP**(이미 연결돼 있으면): `create_file` 로 올리고 `share_file` 로 「링크가 있는 모든 사용자」
   → 직접 다운로드 URL `https://drive.google.com/uc?export=download&id=<fileId>`. 작업이 끝나면 공유를 되돌린다.
3. 사용자 자체 버킷(있으면). 공개 파일 호스트에 인물 사진을 올리지 않는다 — 올려야 한다면 사용자에게 먼저 말한다.

URL 을 `job.json` 의 해당 입력에 `url` 필드로 적어 둔다.

## 힉스필드 메모 (2026-09-21 확인)

- 공식 MCP: `https://mcp.higgsfield.ai/mcp` (HTTP · OAuth). 등록 `claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp`
  → 세션에서 `/mcp` → higgsfield → Authenticate(브라우저). 인증 전엔 `tools/list` 도 401 이다.
- 모델: 이미지 Nano Banana Pro · Soul 2.0 · Seedream · FLUX · GPT Image / 영상 Kling 3.0 · Seedance 2.0 · Veo 3.1 · Sora 2 · Wan / Genjutsu(모션 트랜스퍼·오브젝트 스왑, 2026-09-01 출시)
- Genjutsu 모션 트랜스퍼: 레퍼런스 영상 **3~30초**, 참조 이미지 최대 30장. 15초 기준 480p 40cr · 720p 104cr · 1080p 144cr
- 크레딧: 탑업 $1 = 16cr. 구독 Starter $19/270cr · Plus $59/1,200cr · Ultra $129/3,000cr (월, 이월 없음). 무료 플랜은 월 크레딧 0 + 워터마크
- 웹 UI 무료 생성: 「무료 생성 사용하기」 탭이 보일 때만. 자동 로그인된 기존 계정엔 안 보일 수 있다
- Soul Character(인물 학습) 40cr — 같은 인물로 **3회 이상** 만들 때만 값이 나온다
- 단가 출처와 검증일은 `scripts/pricing.json`. 잔액·비용 조회 도구가 있으면 그 값으로 갱신한다

## 결과 파일 받기

응답이 URL 이면 `curl -L -o outputs/<이름> <url>` 로 받는다. 받은 뒤 `sips -g pixelWidth -g pixelHeight`(이미지) ·
`mdls -name kMDItemDurationSeconds -raw`(영상)로 실제 값을 `job.md` 에 적는다 — 응답이 말한 값이 아니라 파일에서 잰 값.
