# game-background — 게임 배경 · 환경

키아트 한 장을 앵커로 두고, 패럴랙스 층과 지면 타일을 **그 키아트를 참조 이미지로** 파생시킨다.
층마다 지평선 높이·팔레트·광원 방향이 같아야 겹쳤을 때 한 장면이 된다.

## 단계와 계획

| 단계 | 입력 | 모델(기본) | count | 산출물 |
|---|---|---|---:|---|
| 1 키아트(앵커) | 장면 설명 + 비율 + 스타일 참조(선택) | `nano-banana-pro` | 3 | `outputs/keyart-<n>.png` |
| 2 패럴랙스 3층 | 앵커 | `nano-banana-pro` | 3 (층당 1) | `outputs/layer-far-<n>.png` · `layer-mid` · `layer-near` |
| 3 지면 타일 | 앵커 | `nano-banana-pro` | 2 | `outputs/ground-tile-<n>.png` — 가로 반복 |

plan.json 예: `[{"stage":"키아트","model":"nano-banana-pro","count":3},{"stage":"패럴랙스 3층","model":"nano-banana-pro","count":3},{"stage":"지면 타일","model":"nano-banana-pro","count":2}]`

## 슬롯

| 슬롯 | 값 |
|---|---|
| `{{SCENE}}` | 장소·시간대·날씨·카메라 높이 (예: `a mountain fortress at dusk, light snow, camera at eye level of a walking character`) |
| `{{ASPECT}}` | 뷰포트 비율 (`16:9` · `9:16` · `3:2`) — 타일은 `4:1` |
| `{{STYLE_LOCK}}` | game-character 와 같음. 게임 캐릭터가 이미 있으면 그 시트를 스타일 참조로 첨부한다 — 배경과 캐릭터가 같은 손으로 그린 듯해야 한다 |
| `{{HORIZON}}` | 앵커에서 잰 지평선 높이 (예: `horizon at 55% from the top`) — 2·3단계에 고정 |

## 단계 1 — 키아트
```text
Game background key art: {{SCENE}}.
{{STYLE_LOCK}}
Wide establishing composition, {{ASPECT}}. Clear depth: distinct far background, middle ground and near foreground.
Consistent single light source. No characters, no creatures, no text, no logos, no UI.
```
검수: 인물·텍스트 없음 · 원/중/근경이 구분됨 · 비율 맞음. 사용자가 1장 고름 → 앵커. 지평선 높이를 재서 `{{HORIZON}}`.

## 단계 2 — 패럴랙스 3층
앵커를 참조 이미지로, 층마다 한 번씩.
```text
From the attached key art, render ONLY the far background layer (sky, distant mountains/skyline, atmosphere) as a standalone image, {{ASPECT}}, {{HORIZON}}. Same palette, same light direction, same style. Leave the middle and near ground empty — plain flat transparent-friendly {{FILL}} where they would be. No characters, no text.
```
`{{FILL}}` 은 누끼용 단색(`#00FF00` 크로마 또는 흰색) — 도구가 알파를 지원하면 `transparent`.
mid: `ONLY the middle ground layer (main structures, trees, terrain) … sky and far distance empty`.
near: `ONLY the near foreground layer (edge props, rocks, foliage that a character walks in front of or behind) … everything else empty`.

검수: 세 층을 겹쳐 보면 키아트와 같은 장면 · 지평선 일치 · 팔레트 일치 · 층 경계에 잘린 물체 없음.
겹쳐 보기: 세 파일을 `<img>` 로 겹친 HTML 한 장을 만들어 `Read` 하거나 사용자가 본다.

## 단계 3 — 지면 타일
```text
Seamlessly tileable horizontal ground strip matching the attached key art's ground: {{ASPECT 4:1}}, the left edge must continue perfectly into the right edge. Same material, palette and light. No characters, no text, no strong unique landmarks (they reveal the repeat).
```
검수(이음새): 같은 이미지를 두 장 이어 붙여 본다 — `magick tile.png tile.png +append seam.png`(ImageMagick 있을 때),
없으면 `<img>` 둘을 붙인 HTML. 이음새에 선·색 단차가 보이면 재생성.

## 자주 나는 실패와 손잡이

| 증상 | 바꿀 것 하나 |
|---|---|
| 층을 겹치면 지평선이 안 맞는다 | `{{HORIZON}}` 을 퍼센트 숫자로 적었는지 본다 — "same horizon" 만으로는 안 지킨다 |
| 타일 반복이 눈에 띈다 | 프롬프트에 `no strong unique landmarks` 가 있는지, 없으면 넣고 특징적 물체를 뺀다 |
| 캐릭터와 배경의 그림체가 다르다 | 캐릭터 시트를 스타일 참조로 **첨부**한다 |
