# background-photo — 배경 사진 · 월페이퍼 · 영상 배경

인물·텍스트 없는 사진풍 배경. 후보 3장 → 1장 선택 → 업스케일. 목적이 「뒤에 글자나 UI 가 올라간다」면
**비어 있는 영역**을 프롬프트에 명시한다.

## 단계와 계획

| 단계 | 입력 | 모델(기본) | count | 산출물 |
|---|---|---|---:|---|
| 1 후보 | 분위기 + 비율 (+ 스타일 참조) | `nano-banana-pro` (사진풍은 `soul-2.0`) | 3 | `outputs/bg-<n>.png` |
| 2 업스케일 | 고른 1장 | 도구의 upscale | 1 | `outputs/bg-final.png` (4K) |

plan.json 예: `[{"stage":"후보","model":"nano-banana-pro","count":3}]`

## 프롬프트
```text
Photorealistic background photograph: {{MOOD_AND_SUBJECT}}.
Aspect {{ASPECT}}. {{EMPTY_AREA}}
Natural light, shallow depth where appropriate, calm composition with no single dominant object.
No people, no animals, no text, no logos, no watermark.
```
- `{{ASPECT}}`: `16:9`(데스크톱·영상) · `9:16`(폰) · `21:9`(배너).
- `{{EMPTY_AREA}}`: 글자가 올라가면 `keep the left 40% visually quiet and low-contrast for overlaid text`; 없으면 비운다.
- 프로젝트 팔레트가 있으면 `dominant tones close to {{HEX…}}` 로 적는다.

검수: 인물·텍스트 없음 · 비율 · 지정한 빈 영역이 실제로 조용함 · 반복 패턴·인공물(잘린 물체·이중 지평선) 없음.
