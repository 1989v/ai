# game-character — 게임 캐릭터 디자인 시트

콘셉트 한 장을 **앵커**로 삼고, 나머지(3면·표정·포즈·idle 클립)는 전부 그 앵커를 참조 이미지로 넣어
같은 캐릭터임을 고정한다. 숏폼의 IMAGE 1 과 같은 역할이다. 앵커가 흔들리면 뒤가 전부 흔들리므로
**앵커에서 사용자 OK 를 받기 전엔 2단계로 가지 않는다.**

이 장르는 **래스터 생성물**(사진풍·페인팅·픽셀)이 필요할 때 쓴다. 벡터·UI·아트보드 시안은 클로드 디자인 흐름을 그대로 쓴다.

## 단계와 계획

| 단계 | 입력 | 모델(기본) | count | 산출물 |
|---|---|---|---:|---|
| 1 콘셉트(앵커) | 콘셉트 문장 + 스타일 참조(선택) | `nano-banana-pro` | 3 | `outputs/concept-<n>.png` — 정면 전신 A-포즈, 단색 배경 |
| 2 3면 턴어라운드 | 앵커 | `nano-banana-pro` | 2 | `outputs/turnaround-<n>.png` — 정면·측면·후면 한 장 |
| 3 표정·포즈 시트 | 앵커 | `nano-banana-pro` | 2 | `outputs/expressions-<n>.png` · `outputs/poses-<n>.png` |
| 4 idle 클립(선택) | 앵커 | `kling-3.0-720p-5s` | 1 | `outputs/idle-<n>.mp4` — 제자리 호흡·미세 동작 루프 |

plan.json 예: `[{"stage":"콘셉트","model":"nano-banana-pro","count":3},{"stage":"턴어라운드","model":"nano-banana-pro","count":2},{"stage":"표정·포즈","model":"nano-banana-pro","count":2}]`

## 슬롯

| 슬롯 | 값 |
|---|---|
| `{{CONCEPT}}` | 사용자 콘셉트 문장 그대로(영어로 옮김) — 종족·직업·실루엣·주색 2~3개·분위기 |
| `{{STYLE_LOCK}}` | 스타일 참조가 있으면 `Match the attached style reference: line weight, shading, palette saturation, level of detail.` 없으면 사용자가 말한 스타일 한 줄(예: `clean 2D game illustration, cel shading, no outlines`). 프로젝트에 스타일 가이드(DESIGN.md 등)가 있으면 그 색 토큰을 여기 적는다 |
| `{{PALETTE}}` | 주색 hex 2~3개 (앵커에서 뽑아 2단계부터 고정) |
| `{{BG}}` | 기본 `flat neutral grey (#808080) background` — 누끼 딸 때 편하다. 흰 옷이면 회색, 어두운 옷이면 밝은 회색 |

## 단계 1 — 콘셉트(앵커)
```text
Full-body character concept art of {{CONCEPT}}.
Front view, standing in a relaxed A-pose, arms slightly away from the body, feet visible, whole body from head to toe, centered.
{{STYLE_LOCK}}
Strong readable silhouette; design details that would still read at 64 px tall.
{{BG}}. No text, no logos, no watermark, no props on the ground, single character only.
```
검수: 실루엣이 한눈에 읽힘 · 전신 · 손가락 5개 · 좌우 대칭이 맞아야 할 곳(갑옷·장식)이 맞음 · 텍스트 없음.
사용자에게 3장을 보이고 **하나를 고르게** 한다 → 그것이 앵커. 앵커의 주색을 `{{PALETTE}}` 로 적는다.

## 단계 2 — 3면 턴어라운드
앵커를 참조 이미지로.
```text
Character turnaround sheet of the exact same character as the attached reference image: front view, side (profile) view, back view, side by side on one canvas, same scale, feet on one baseline.
Keep every design element, proportion, color and material identical to the reference. Palette: {{PALETTE}}.
{{STYLE_LOCK}}
Neutral A-pose in all three views. {{BG}}. No text, no labels, no arrows.
```
검수: 세 뷰의 키가 같은 기준선 · 소품·장식 위치가 뷰 간 일치 · 팔레트 동일 · 뒷면에 앞면 요소가 새지 않음.

## 단계 3 — 표정·포즈 시트
```text
Expression sheet of the exact same character as the attached reference: 6 head-and-shoulders portraits in a 3×2 grid — neutral, happy, angry, surprised, sad, determined. Identical face, hair and colors. {{STYLE_LOCK}} {{BG}}. No text.
```
```text
Action pose sheet of the exact same character as the attached reference: 4 full-body poses in a row — idle, run, attack, hit/damaged. Same proportions, outfit and palette {{PALETTE}}. {{STYLE_LOCK}} {{BG}}. No text, no effects that hide the body.
```
검수: 얼굴이 6칸 모두 같은 사람 · 포즈 4개에서 팔다리 길이 동일 · 손가락·무기 잡는 손 정상.

## 단계 4 — idle 클립(선택)
앵커를 입력 이미지로, 5초.
```text
The character stands in place breathing gently — subtle chest rise, slight weight shift, hair and cloth sway lightly. Camera locked, no zoom. Loopable: first and last frame nearly identical. {{BG}} stays flat and unchanged. No text.
```
검수: 카메라 고정 · 배경 불변 · 첫/끝 프레임 유사(루프) · 얼굴 유지.

## 자주 나는 실패와 손잡이

| 증상 | 바꿀 것 하나 |
|---|---|
| 턴어라운드에서 뒷면이 딴 캐릭터 | 앵커를 더 단순한 실루엣으로 고르거나, 2단계 프롬프트에 앵커의 특징 3개를 문장으로 적는다 |
| 스타일이 장마다 흔들린다 | `{{STYLE_LOCK}}` 에 스타일 참조 이미지를 실제로 첨부한다 — 말로 쓴 스타일은 약하다 |
| 배경이 그림자·바닥을 만든다 | `{{BG}}` 에 `no ground shadow, no floor` 를 붙인다 |
