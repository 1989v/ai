---
description: "신규 앱 레포에 boilerplate 일괄 생성: README(ko/en), LICENSE, .gitignore, Distribution/, docs/guides/, docs/ 구조. 토큰 치환까지. Trigger: 앱 초기화, scaffold, boilerplate 생성, init app"
---

# /appkit:init

빈 디렉토리 / 새로 만든 레포에 muxbar·aieye 패턴의 coarse 표준 파일을 일괄 생성.

## Usage

```
/appkit:init
/appkit:init --type macos-menubar          # 기본값 (v0.1 유일)
/appkit:init --with-harness                # hns 설치된 경우 하네스 문서까지
/appkit:init --dry-run                     # 생성할 파일 목록만 보고 실행 X
```

## 1. Collect inputs

사용자에게 묻기 (이미 알고 있으면 스킵):

```
? 앱 이름 (영문 소문자, 바이너리/디렉토리명):  ex. aieye
? 표시용 이름 (로고/문서):                      ex. aieye (같음 ok)
? GitHub owner/org:                             ex. 1989v
? Bundle identifier:                            ex. com.1989v.aieye
? 한 줄 설명 (영어):
? 한 줄 설명 (한국어):
? 최소 macOS 버전:                              default 13.0
? 스택 뱃지 (markdown lines, 선택):             ex. Tauri v2 / React 19
? License 저작자:                               default $(git config user.name)
? License 연도:                                 default 현재 연도
```

## 2. Generate files

토큰 치환 후 다음 파일 생성 (이미 있으면 **덮어쓰기 전 확인**):

```
./README.md
./README.ko.md
./LICENSE
./.gitignore                 (기존에 있으면 추가 항목만 append)
./Distribution/README.md
./Distribution/Release.sh    (chmod +x)
./Distribution/HomebrewTap/{{APP_NAME}}.rb
./docs/README.md             (없을 때만)
./docs/guides/github-discoverability.md
./docs/assets/.gitkeep
```

**토큰** (템플릿 내 `{{...}}` 전부):

| Token | 의미 |
|---|---|
| `{{APP_NAME}}` | 앱 이름 (소문자) |
| `{{APP_DISPLAY}}` | 표시 이름 |
| `{{GITHUB_OWNER}}` | GitHub user/org |
| `{{BUNDLE_ID}}` | macOS bundle identifier |
| `{{ONE_LINER}}` | 영어 한 줄 |
| `{{ONE_LINER_KO}}` | 한국어 한 줄 |
| `{{TOPICS_CSV}}` | GitHub topics (콤마) |
| `{{MIN_MACOS}}` | 최소 macOS 버전 |
| `{{STACK_BADGES}}` | shields.io badges |
| `{{YEAR}}` | License 연도 |
| `{{AUTHOR}}` | License 저작자 |

## 3. `--with-harness` (옵션)

`hns` 플러그인이 설치되어 있으면:
- `CLAUDE.md` — 하네스 규칙 stub (hns:init 에서 참조)
- `agent-os/` 디렉토리 기본 골격
- `docs/adr/`, `docs/plans/`, `docs/specs/` 스텁 생성

없으면 flag 무시하고 경고만 출력 (설치 방법 제시).

## 4. Output

```
✓ 생성된 파일: N개
✓ 토큰 치환 완료
✓ Git init 필요시: git init && git add . && git commit -m "chore: initial scaffold via /appkit:init"

다음 단계: /appkit:seo  (GitHub topics / description / social preview)
```

## 템플릿 위치

플러그인 내부 `templates/` 디렉토리:
- `templates/README.md.tmpl`
- `templates/README.ko.md.tmpl`
- `templates/LICENSE.tmpl`
- `templates/gitignore.tmpl`
- `templates/Distribution-README.md.tmpl`
- `templates/Release.sh.tmpl`
- `templates/HomebrewTap-cask.rb.tmpl`
- `templates/github-discoverability.md.tmpl`

## 주의사항

- **기존 파일 덮어쓰기 금지** — 충돌 시 반드시 사용자에게 확인
- **.gitignore 는 병합** — 완전 교체 말고 누락 항목만 append
- **README 이미 있는 경우** — 백업(`README.md.bak`) 후 신규 생성, 또는 사용자가 병합 선택
