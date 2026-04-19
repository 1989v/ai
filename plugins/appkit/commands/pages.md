---
description: "GitHub README 스크린샷 첨부 + GitHub Pages 랜딩 페이지 배너 이미지 셋업. docs/assets/ 이미지 저장 전략 포함. Trigger: 배너, 스크린샷, 캡쳐 추가, github pages, 랜딩 페이지, 프로젝트 페이지"
---

# /appkit:pages

레포에 배너/스크린샷 이미지를 **어디에 어떻게 저장하고 노출할지** 전체 전략 가이드.

## 3가지 이미지 노출 층위

```
[Layer A] README.md 내 스크린샷         ← 방문자가 레포 열었을 때 첫인상
[Layer B] Social preview (링크 카드)    ← Slack/Twitter 공유 시 썸네일
[Layer C] GitHub Pages 랜딩 페이지      ← 별도 도메인 (owner.github.io/app)
```

## Layer A — README.md 스크린샷

### 저장 위치 결정 (어디에 커밋?)

| 전략 | 경로 | 장점 | 단점 |
|---|---|---|---|
| **레포 내 커밋** (추천) | `docs/assets/*.png` | 이미지+코드 원자적, fork 시 함께 복제, 영구 보존 | 레포 사이즈 증가 |
| **별도 브랜치** | `gh-pages` or `assets` 브랜치 | main 크기 영향 X | 관리 복잡, 링크 깨질 위험 |
| **GitHub Issue 업로드** | `https://user-images.githubusercontent.com/...` | 즉시 URL 생성, 용량 무관 | issue 삭제 시 URL 사라짐, 외부 의존 |
| **외부 CDN** (S3/Cloudinary) | 자체 호스팅 | 대용량 OK | 비용, 관리 |

**결론**: 대부분 **레포 내 커밋** 이 정답. 조건:
- 이미지 총 크기 < 10MB
- `docs/assets/` 에 일괄 저장
- PNG 권장 (스크린샷), GIF 는 압축해서 용량 체크

### 이미지 준비

**필수 스크린샷** (macOS 메뉴바 앱 기준):
1. `screenshot-menu-bar.png` — 메뉴바 아이콘 상태들 (확대)
2. `screenshot-panel.png` — 패널 전체 뷰 (기능 한눈에 보이게)
3. `screenshot-preview.png` — 특화 기능 (hover, bulk, 등)

**권장**:
- Retina 해상도로 캡처 (2x) → 작은 화면에서도 선명
- `cmd+shift+5` → 창 선택 → 저장
- 용량 줄이기: `pngcrush`, ImageOptim, 또는 `sips -s format png -s formatOptions 70`

**데모 GIF** (optional but impactful):
- Kap.app 또는 Gifox 로 30초 이내
- 핵심 워크플로: icon click → 기능 사용 → 결과
- 저장: `docs/assets/demo.gif`
- 용량: < 10MB (GIF 는 쉽게 커짐 — 프레임률 낮추고 해상도 조정)

### README 임베드

```markdown
## 스크린샷

![Menu bar panel](docs/assets/screenshot-panel.png)

![Live demo](docs/assets/demo.gif)
```

**상대 경로**: `docs/assets/...` 로 시작 (루트 기준).
GitHub 가 자동으로 raw.githubusercontent 로 렌더링.

**다크모드 대응** (선택):
```markdown
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/screenshot-dark.png">
  <img src="docs/assets/screenshot-light.png" alt="Panel">
</picture>
```

### 커밋

```bash
git add docs/assets/
git commit -m "docs: 스크린샷 + 데모 GIF 추가"
git push
```

## Layer B — Social preview

`/appkit:seo` 에서 다룸. 웹 UI 로 1280×640 px 업로드.

## Layer C — GitHub Pages 랜딩 페이지

**용도**: README 보다 더 풍부한 랜딩. 배너 + 스크린샷 + CTA + 데모 임베드.

### Option 1: `docs/` 폴더 기반 (가장 쉬움)

1. 레포 Settings → Pages
2. **Source**: Deploy from a branch
3. **Branch**: `main` / **Folder**: `/docs`
4. Save → URL 발급: `https://OWNER.github.io/REPO/`

그 후 `docs/index.md` 또는 `docs/index.html` 만들면 자동 호스팅.

**index.md 템플릿** (간단):

```markdown
---
layout: default
title: APP_NAME
---

<p align="center">
  <img src="assets/banner.png" width="720" alt="APP_NAME banner">
</p>

# APP_NAME

ONE_LINER 설명

[![Download DMG](https://img.shields.io/badge/Download-.dmg-blue)](https://github.com/OWNER/APP_NAME/releases/latest)
[![Homebrew](https://img.shields.io/badge/Homebrew-cask-orange)](https://github.com/OWNER/homebrew-tap)

## 스크린샷

![panel](assets/screenshot-panel.png)

## 설치

\```bash
brew install --cask OWNER/tap/APP_NAME
\```

## 문서

- [README](https://github.com/OWNER/APP_NAME)
- [변경 이력](https://github.com/OWNER/APP_NAME/releases)
```

### Option 2: Jekyll 테마 사용

Settings → Pages → **Theme chooser** 로 minimal/Cayman/Slate 등 선택.
`docs/_config.yml` 자동 생성, 디자인 프리셋 적용.

### Option 3: 정적 사이트 생성 (Astro/Next.js)

프로젝트 규모 커지면:
- `web/` 서브폴더에 Astro/Next.js
- GitHub Actions 로 빌드 후 `gh-pages` 브랜치 deploy
- `docs:` 출처 대신 `gh-pages` branch 사용

### 배너 이미지 만들기

**사이즈 권장**: 1200×400 px (README 에서 잘 보임)
**도구**:
- [socialify.git.ci](https://socialify.git.ci) — 자동 생성 (README 용으로도 사용 가능)
- Figma — 앱 아이콘 + 이름 + 한 줄 설명 배치
- Screenshot + Crop — 앱 실행 화면에서 일부 잘라 배너화

**저장**: `docs/assets/banner.png` (README/Pages 둘 다 재사용)

### 커스텀 도메인 (선택)

Pages settings → Custom domain → `app.example.com`
DNS 의 CNAME 을 `OWNER.github.io` 로 설정.
HTTPS 체크박스 활성화.

## 체크리스트

```
□ 스크린샷 최소 2~3장 docs/assets/ 에 커밋
□ 데모 GIF (선택이지만 강력 추천) docs/assets/demo.gif
□ README 에 ![](docs/assets/...) 로 임베드
□ 배너 이미지 docs/assets/banner.png 생성
□ GitHub Pages 활성화 (Settings → Pages → main/docs)
□ docs/index.md 또는 최소 랜딩 페이지 작성
□ (선택) 커스텀 도메인 연결
```

## 비용 / 한도

- **레포 용량 권고**: 1GB 미만 (이미지 총합)
- **파일 1개 최대**: 100MB
- **GitHub Pages 제공 대역폭**: 100GB/월 (소프트 limit, 실무 충분)

## 참고

- [GitHub Pages 공식](https://pages.github.com/)
- [GitHub Flavored Markdown picture tag (다크모드 대응)](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#specifying-the-theme-an-image-is-shown-to)
- [Jekyll themes 선택](https://pages.github.com/themes/)
