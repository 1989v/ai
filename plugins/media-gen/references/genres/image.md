# image — 일반 이미지 (썸네일 · 제품 컷 · 스타일 변환 · 인물 스타일화)

한 단계짜리 장르. 인물이 들어가면 **정체성 고정 블록**을 붙이고, 없으면 목적·비율·스타일만 적는다.

## 단계와 계획

| 단계 | 입력 | 모델(기본) | count | 산출물 |
|---|---|---|---:|---|
| 1 생성 | 콘셉트 (+ 인물 사진 · 스타일 참조) | `nano-banana-pro` (사진풍 인물은 `soul-2.0`) | 3 | `outputs/image-<n>.png` |
| 2 업스케일(선택) | 고른 1장 | 도구의 upscale (단가는 스키마에서) | 1 | `outputs/image-final.png` |

plan.json 예: `[{"stage":"생성","model":"nano-banana-pro","count":3}]`

## 프롬프트
```text
{{PURPOSE}} — {{CONCEPT}}.
{{STYLE_LOCK}}
Aspect {{ASPECT}}. {{COMPOSITION}}
No text, no logos, no watermark.
```
- `{{PURPOSE}}`: `YouTube thumbnail` · `product hero shot on seamless background` · `blog header illustration` 처럼 **용도**를 먼저.
- `{{COMPOSITION}}`: 썸네일이면 `subject fills 60% of frame, high contrast, readable at 200 px wide`; 제품이면 `three-quarter angle, soft studio light, subtle ground reflection`.
- 인물이 있으면 사진을 참조로 넣고 이 블록을 앞에 붙인다:
```text
Using the attached photographs as strict identity references, keep the person's face, facial features, hairstyle, skin tone, age and body proportions exactly the same. Do not reinterpret the face as a new person. Change only: {{WHAT_CHANGES}}.
```

검수: 텍스트 없음(썸네일 글자는 나중에 얹는다) · 비율 · 인물이면 얼굴·비율 동일 · 손가락 5개 · 용도에 맞는 여백(썸네일은 글자 자리).
사용자가 3장 중 1장을 고른 뒤에만 업스케일한다.
