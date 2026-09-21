# media-gen

AI 로 미디어를 만드는 파이프라인 플러그인 — 인물 사진 변신 숏폼, 게임 캐릭터·배경, 이미지, 배경 사진.
생성은 MCP(힉스필드)나 사용자의 웹 UI 가 하고, 이 플러그인은 **입력 게이트 → 비용 게이트 → 정체성 고정
프롬프트 → 단계별 검수 → 기록**을 맡는다.

```
/media-gen:create shortform-transform      # 사진 + 레퍼런스 영상 → 변신 숏폼
/media-gen:create game-character           # 콘셉트 → 앵커 → 3면 → 표정·포즈 (→ idle 클립)
/media-gen:create game-background          # 키아트 → 패럴랙스 3층 → 지면 타일
/media-gen:create image | background-photo
```

## 게이트 둘

- **인테이크** — `scripts/intake.py` 가 장르별 필수 입력을 검사하고, 없으면 작업 폴더를 만들지 않는다(종료 2).
- **비용·허락** — `scripts/budget.py estimate` 가 `pricing.json`(검증일 명시)으로 크레딧·$·₩ 표와 ₩0 대안을 내고,
  사용자가 고른 뒤 `approve` 가 승인 기록을 쓴다. **힉스필드 유료 도구는 `hooks/guard-higgsfield.py` 가 이 기록 없이는
  거부한다** — 호출마다 승인 횟수를 1 줄이고, 0 이면 다시 거부. bypass 권한 모드에서도 듣는다.

## 선행

```bash
claude mcp add --transport http --scope user higgsfield https://mcp.higgsfield.ai/mcp   # 그 뒤 /mcp 에서 Authenticate
```
`ffmpeg` 는 영상 프레임 검수에 쓴다(없으면 첫 프레임만 자동, 나머지는 사용자 확인).

## 테스트

```bash
python3 -m unittest discover -s plugins/media-gen/tests -p 'test_*.py'
```
인테이크 거부·복사, 견적 합계·오래된 단가표·모르는 모델, 승인 전제, 훅의 deny(승인 없음·만료·소진)와 allow·차감.

## 파일

`skills/create/SKILL.md` 절차 · `references/genres/*.md` 장르별 단계·프롬프트 · `references/providers.md` MCP 탐색·업로드·힉스필드 메모 ·
`references/review-checklist.md` 검수 · `scripts/{intake,budget}.py` + `pricing.json` · `hooks/` 승인 게이트
