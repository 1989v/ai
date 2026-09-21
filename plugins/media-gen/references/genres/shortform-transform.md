# shortform-transform — 인물 사진 → 변신 숏폼

**원본 영상 = 움직임 담당, 인물 사진 = 외모 담당.** 사진에서 「변신 전」과 「변신 후」 정지 이미지를 먼저 만들고,
레퍼런스 영상의 움직임·타이밍을 그 둘 사이에 입힌다(모션 트랜스퍼). 실패의 대부분은 **얼굴이 바뀌거나
팔다리가 길어지거나 나이가 드는 것**이라, 모든 프롬프트가 정체성·체형 고정 블록을 갖는다.

구조는 공개 튜토리얼(아이 마법소녀 변신 영상, 2026-09)에서 가져왔고 프롬프트는 주제 슬롯으로 일반화했다.

## 단계와 계획

| 단계 | 입력 | 모델(기본) | count | 산출물 |
|---|---|---|---:|---|
| 1 IMAGE 1 앵커 | 원본 사진 1~3장 | `nano-banana-pro` | 2 | `outputs/image1-<n>.png` — 정면 전신, 검정 단색 배경, 원본 그대로 |
| 2 IMAGE 2 변신 후 | IMAGE 1 | `nano-banana-pro` | 2 | `outputs/image2-<n>.png` — 같은 얼굴·체형, 의상만 목표 룩 |
| 3 모션 트랜스퍼 | REFERENCE VIDEO + IMAGE 1 + IMAGE 2 | `genjutsu-motion-transfer-720p-15s` | 1 | `outputs/video-<n>.mp4` |

plan.json 예: `[{"stage":"IMAGE 1","model":"nano-banana-pro","count":2},{"stage":"IMAGE 2","model":"nano-banana-pro","count":2},{"stage":"모션 트랜스퍼","model":"genjutsu-motion-transfer-720p-15s","count":1}]`

₩0 수동 경로: 웹 UI 에서 (1) 이미지 생성/편집 도구로 IMAGE 1·2 를 만들고, (2) **Genjutsu → 모션 트랜스퍼**에
레퍼런스 영상을 「모션을 추출할 레퍼런스 영상」에, IMAGE 1·2 를 「캐릭터 추가」에 넣고 아래 3단계 프롬프트를 붙인다.

## 슬롯

| 슬롯 | 값 |
|---|---|
| `{{SUBJECT}}` | `baby` / `child` / `adult` (+ 성별이 필요하면 `girl`/`boy`/`woman`/`man`) |
| `{{IDENTITY_CARD}}` | ① 에서 쓴 아이덴티티 카드 영어 요약 (hair, skin tone, age band, distinctive features, clothing in the photo) |
| `{{TARGET_LOOK}}` | 변신 후 의상 한 줄 — 사용자가 말한 것만. 예: `a cute and stylish magical-girl hero costume` |
| `{{PROPORTION_PROFILE}}` | 아래 체형 프로필 블록 중 하나 |
| `{{ENVIRONMENT}}` | 기본 = 아래 DREAMCORE COSMIC 블록. 사용자가 다른 분위기를 말하면 그 문단으로 교체 |
| `{{ENDING_POSE}}` | 기본 `a cute and confident final ending pose inspired by the final pose and timing of the REFERENCE VIDEO` |

### 체형 프로필 블록

**toddler (유아, ~5세)**
```text
Maintain a naturally cute toddler physique with a relatively large head, short neck, compact torso, short chubby arms, short chubby legs, small hands, and small feet.
The arms and legs must remain visibly short and baby-like throughout the entire sequence.
```
**child (아동, 6~12세)**
```text
Maintain a natural child physique: head noticeably larger relative to the body than an adult's, slender but not adult-like limbs, short neck, small hands and feet.
Preserve the child's real height impression — never lengthen the legs or torso toward adult proportions.
```
**adult (성인)**
```text
Maintain the person's real build, height impression, shoulder width and limb length exactly as in the reference photographs.
Do not slim, elongate, idealize, or restyle the body.
```

## 단계 1 — IMAGE 1 (앵커) 프롬프트

원본 사진 전부를 참조 이미지로 넣는다. 얼굴이 잘 보이는 사진이 여러 장이면 재현이 낫다.

```text
Using the attached photographs as strict identity references, create a full-body photograph of the same {{SUBJECT}} standing naturally and facing the camera directly.
Keep the face, facial features, hairstyle, skin tone, body shape and age exactly as in the attached photographs. Do not reinterpret the face as a new person.
{{IDENTITY_CARD}}
The whole body must be visible from head to toe, in a relaxed natural standing pose, arms at the sides.
Keep the clothing as seen in the photographs.
Background: clean solid black. No text, no props, no other people.
Portrait orientation 9:16.
```

검수(IMAGE 1): 머리~발끝 전부 보임 · 검정 단색 · 얼굴이 원본과 같은 사람 · 팔다리 비율이 원본과 같음 · 옷이 원본 · 손가락 5개.

## 단계 2 — IMAGE 2 (변신 후) 프롬프트

IMAGE 1 을 참조 이미지로 넣는다.

```text
Using the attached image as the strict reference, keep the {{SUBJECT}}'s face, facial features, hairstyle, skin tone, age and natural body proportions exactly the same, and change ONLY the clothing into {{TARGET_LOOK}}.
{{PROPORTION_PROFILE}}
The {{SUBJECT}} stands at attention facing the camera, whole body visible from head to toe.
Do not make the {{SUBJECT}} look older, taller, thinner, or more adult-like. Do not reinterpret or alter the face.
Background: clean solid black. No text, no props, no other people. Portrait orientation 9:16.
```

검수(IMAGE 2): IMAGE 1 검수 항목 전부 + **의상만** 바뀜 · 키·비율 동일 · 얼굴 동일 · 추가 소품 없음.

## 단계 3 — 모션 트랜스퍼 프롬프트

REFERENCE VIDEO = 레퍼런스 영상, IMAGE 1 = 변신 전, IMAGE 2 = 변신 후. 이 셋을 도구가 받는 순서·이름대로 넣는다.

```text
Use the provided REFERENCE VIDEO as the primary and fixed reference for the transformation sequence, transformation timing, cinematic energy, camera motion, visual progression, transformation choreography, final reveal, ending pose, and overall pacing.

Use the TWO PROVIDED IMAGES as strict appearance references.
IMAGE 1 = BEFORE TRANSFORMATION REFERENCE. The {{SUBJECT}} must start exactly as shown in IMAGE 1.
IMAGE 2 = AFTER TRANSFORMATION REFERENCE. The transformation must finish with the {{SUBJECT}} exactly as shown in IMAGE 2.
Do not reinterpret, redesign, simplify, alter, or introduce additional details to either appearance.
Throughout the entire sequence, maintain the exact same facial identity, age, hairstyle, facial proportions, body shape, and natural proportions shown in the provided reference images.
The {{SUBJECT}} must NEVER become taller, thinner, older, or more adult-like at any point during the transformation.

# ==================================================
BODY PROPORTIONS — EXTREMELY IMPORTANT
{{PROPORTION_PROFILE}}
Do not extend or lengthen the arms or legs for dramatic posing or cinematic movement.
Preserve the original leg-to-body ratio and arm-to-body ratio shown in the provided photographs.
Every body movement and pose must respect the {{SUBJECT}}'s realistic anatomy and natural physical proportions.
The hands must remain anatomically natural, with exactly five fingers on each hand. The feet must remain anatomically natural, with exactly five toes on each foot.
No additional fingers, missing fingers, fused fingers, stretched fingers, extra toes, malformed hands, malformed feet, twisted limbs, elongated limbs, duplicated limbs, or altered body proportions.

# ==================================================
TRANSFORMATION SEQUENCE
The {{SUBJECT}} starts exactly as shown in IMAGE 1.
Follow the transformation progression, rhythm, motion, and visual energy established by the REFERENCE VIDEO.
A gentle magical glow gradually begins to appear around the body. Tiny shimmering particles and delicate points of light begin drifting through the surrounding space.
Glowing ribbons of pale blue, soft white, silver, iridescent pastel light, and subtle cosmic energy gently move around the body. The magical energy should flow naturally around the body without altering or stretching the anatomy.
The appearance shown in IMAGE 1 gradually transitions into the appearance shown in IMAGE 2. The transition must feel smooth and continuous rather than resembling a sudden image replacement.
Elements from IMAGE 1 gently dissolve into sparkling light particles while the corresponding elements from IMAGE 2 naturally emerge through the magical glow.
Do not create intermediate costumes, accessories, hairstyles, or visual elements that are not supported by the provided images. Avoid sudden replacements or hard cuts between IMAGE 1 and IMAGE 2.
During the transformation, use graceful sparkling trails, luminous outlines, translucent magical ribbons, small star-like particles, cosmic dust, soft lens glints, iridescent reflections, and subtle waves of glowing energy. Keep the effects visually beautiful and cinematic rather than explosive or aggressive.
Do not cover or obscure the face for extended periods. The face must remain recognizable and visually consistent whenever it is visible.

# ==================================================
ENVIRONMENT
{{ENVIRONMENT}}

# ==================================================
CAMERA
Follow the overall camera language and cinematic progression established by the REFERENCE VIDEO while prioritizing the {{SUBJECT}}'s anatomy and identity.
Keep the {{SUBJECT}} centered during the main transformation moments. Prefer full-body framing whenever possible so the natural proportions remain clearly visible.
Camera movement should feel smooth, floating, magical, and cinematic. The camera may gently orbit, move closer, pull back, or float around the {{SUBJECT}} whenever appropriate to the reference transformation.
Do not use perspective distortion that makes the legs appear longer. Do not use extreme low-angle shots. Do not stretch or distort the body to fill the frame.

# ==================================================
FINAL REVEAL & ENDING POSE — IMPORTANT
Once the transformation is fully complete, clearly reveal the {{SUBJECT}} exactly as shown in IMAGE 2. Do not end the video immediately once the transformation is finished.
Include a distinct FINAL HERO MOMENT after the transformation has been completed. The magical energy gradually settles and opens, clearly revealing the complete transformed appearance shown in IMAGE 2.
The {{SUBJECT}} then naturally moves into {{ENDING_POSE}}. The ending pose must remain physically appropriate and realistic for this {{SUBJECT}}: simple, stable, and achievable with the real arm and leg length — no exaggerated superhero stance, no unnaturally wide stance, no anatomically difficult position.
During the final pose, gently pull the camera backward or stabilize it into a clean full-body hero composition. A soft celestial halo or luminous glow appears behind the {{SUBJECT}}; shimmering particles and light trails gradually settle.
Clearly hold the completed pose for a brief moment so the viewer can recognize the final IMAGE 2 appearance. Finish with the {{SUBJECT}} holding the final pose while the surrounding particles and glow gradually fade away.

# ==================================================
CRITICAL CONSISTENCY RULES
Only one {{SUBJECT}}. The same {{SUBJECT}} from beginning to end.
IMAGE 1 is strictly the BEFORE reference. IMAGE 2 is strictly the AFTER reference.
Do not describe, assume, or introduce specific clothing, colors, accessories, or styling beyond what is actually visible in IMAGE 1 and IMAGE 2.
No facial morphing. No identity changes. No age progression. No body growth. No altered proportions. No elongated arms or legs. No oversized hands or feet. No anatomical deformation. No additional or missing fingers or toes. No duplicated limbs. No distorted face. No gender changes. No random hairstyle alterations. No random accessories. No invented clothing. No additional characters.
The transformation may alter the appearance from IMAGE 1 into IMAGE 2, but it must NEVER alter the identity, age, facial structure, or natural anatomy.
```

### 기본 ENVIRONMENT — DREAMCORE COSMIC
```text
Create a surreal and dreamy cosmic transformation environment — an ethereal, dreamlike universe rather than a realistic physical setting.
Use deep midnight blue, indigo, violet, pale blue, and subtle pastel tones. Surround the {{SUBJECT}} with distant stars, drifting particles, soft cosmic dust, dreamy nebulous clouds, translucent waves of light, faint celestial glows, and subtle iridescent gradients.
The background should feel endless, weightless, surreal, nostalgic, whimsical, and dreamcore. Soft glowing halos and circular waves of light may appear behind the {{SUBJECT}} during important transformation moments; small stars and particles may drift across different depths to create dimensionality.
Keep the environment spacious; the {{SUBJECT}} must always remain the strongest visual focus.
Avoid realistic rooms, furniture, buildings, streets, text, logos, crowds, or other distracting elements.
```

검수(영상): 처음 1초가 IMAGE 1 · 마지막 정지 포즈가 IMAGE 2 · 중간에 얼굴이 딴 사람이 되는 구간 없음 · 팔다리가 길어지는
구간 없음 · 인물 하나 · 텍스트/로고 없음. 프레임 확인 방법은 `review-checklist.md`.

## 자주 나는 실패와 손잡이

| 증상 | 바꿀 것 하나 |
|---|---|
| 다리가 길어진다 / 나이가 든다 | 체형 프로필을 한 단계 어리게(child→toddler) 두거나, IMAGE 1·2 를 더 정면·전신으로 다시 |
| 얼굴이 딴 사람 | IMAGE 1 을 원본 사진 2~3장으로 다시 만든다 (한 장짜리 앵커가 원인인 경우가 많다) |
| 변신 후 옷이 IMAGE 2 와 다르다 | IMAGE 2 의 의상이 실루엣으로 구분되는지 본다 — 검정 배경에 검정 옷이면 바꾼다 |
| 변신이 순간 교체처럼 보인다 | 레퍼런스 영상의 변신 구간이 너무 짧다 — 다른 레퍼런스(3~30초 안에서 더 긴 변신) |
| 마지막 포즈 없이 끝난다 | 레퍼런스 영상 끝에 정지 포즈가 있는지 본다 — 없으면 있는 영상으로 |
