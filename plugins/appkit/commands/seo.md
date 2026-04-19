---
description: "GitHub 레포 메타데이터 세팅: Topics, Description, Social preview 업로드 가이드. gh CLI 명령 직접 실행. Trigger: topics 추가, github seo, 레포 메타데이터, 발견성"
---

# /appkit:seo

레포의 발견성 Layer 1 설정: **Topics + Description + Social preview**.

## Usage

```
/appkit:seo                 # 대화형
/appkit:seo --apply          # topics/description 바로 적용 (social은 웹 UI 안내)
```

## 1. 현재 상태 조회

```bash
gh repo view --json name,nameWithOwner,description,repositoryTopics -q '.'
```

- 이미 설정된 topics 개수 / description 내용 확인 → 사용자에게 요약 제시

## 2. Topics 제안

사용자의 스택 / 도메인 / 플랫폼 기반으로 10~15개 제안.

**카테고리별 예시**:

| 카테고리 | macOS 메뉴바 앱 예시 |
|---|---|
| 기술 스택 | `rust`, `tauri`, `react`, `typescript`, `swift`, `swiftui`, `appkit` |
| 플랫폼 | `macos` |
| 도메인 | `menu-bar`, `menu-bar-app`, `{도메인-specific}` |
| 통합 대상 | `homebrew-cask` |
| 넓은 카테고리 | `developer-tools`, `productivity` |

**지켜야 할 규칙**:
- 최대 20개 (GitHub 제한)
- 너무 일반: `app`, `tool`, `utility` — 유입 효과 미미
- 관련 없는 트렌드 남발 금지 (스팸 판정)

## 3. Description 공식

```
[핵심 정체성] — [주요 특징 1-3개], [특징 2], [특징 3].
```

**길이**: 한 줄, 최대 ~350자. 검색 결과/About 사이드바에 그대로 노출.

예시 생성: 사용자의 프로젝트 README 첫 문장 + 주요 기능 2~4개를 추출해 초안 제시.

## 4. Apply

```bash
# Topics
gh repo edit OWNER/REPO --add-topic tag1,tag2,tag3,...

# Description
gh repo edit OWNER/REPO --description "..."

# 확인
gh repo view OWNER/REPO --json repositoryTopics -q '.repositoryTopics[].name'
gh repo view OWNER/REPO --json description -q '.description'
```

## 5. Social preview 가이드

**웹 UI 전용** (gh CLI로 불가):

경로:
```
https://github.com/OWNER/REPO/settings#social-preview
```

이미지 옵션 (1280×640 px):

1. **socialify.git.ci** (추천 — 제로 디자인):
   ```
   https://socialify.git.ci/OWNER/REPO/image?font=JetBrains+Mono&pattern=Floating+Cogs&theme=Dark&description=1
   ```
   브라우저 방문 → 커스터마이즈 → Download → 설정 업로드

2. **직접 디자인** — Figma/Sketch 로 1280×640, 앱 스크린샷 + 이름 + 한 줄 설명 배치

3. **README 상단 이미지로 대체** — Social preview 업로드 안해도 README 첫 이미지가 링크 카드로 사용됨

**검증**:
```
https://opengraph.githubassets.com/1/OWNER/REPO
```
(캐시 갱신 30초 ~ 몇 분)

## 6. Output 체크리스트

```
✓ Topics 등록 완료 (N개)
✓ Description 업데이트 완료
□ Social preview 업로드 — 웹 UI 직접 업로드 필요
  → https://github.com/OWNER/REPO/settings#social-preview

다음 단계: /appkit:release <version>  (첫 릴리스 시)
         또는 /appkit:check  (현재 완성도 진단)
```

## 참고 링크

- [GitHub Topics 공식 docs](https://docs.github.com/en/repositories/classifying-your-repository-with-topics)
- [socialify.git.ci](https://socialify.git.ci)
- [opengraph.githubassets.com](https://opengraph.githubassets.com)
