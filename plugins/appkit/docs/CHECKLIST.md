# 신규 macOS 메뉴바 앱 출시 체크리스트

> 순서대로 따라가면 "사용자가 설치하고 쓸 수 있는 OSS 레포" 수준까지 도달.

## Phase 0 — 기본 셋업

```
□ Git repo 초기화 (로컬)
□ GitHub public repo 생성 (빈 상태)
□ 로컬 ↔ remote 연결 (git remote add / push)
□ main 브랜치 설정
```

## Phase 1 — 코어 파일

템플릿에서 복사 + 토큰 치환:

```
□ LICENSE                               templates/LICENSE.tmpl
□ .gitignore                            templates/.gitignore.tmpl (언어별 조정)
□ README.md (영어)                      templates/README.md.tmpl
□ README.ko.md (글로벌 타겟 시)         templates/README.ko.md.tmpl
□ build.sh (로컬 개발용 단일 빌드)
```

## Phase 2 — 배포 인프라

```
□ Distribution/ 디렉토리 생성
□ Distribution/README.md                templates/Distribution-README.md.tmpl
□ Distribution/Release.sh               templates/Release.sh.tmpl
  └ chmod +x Release.sh
□ Distribution/HomebrewTap/{app}.rb     templates/HomebrewTap-cask.rb.tmpl
□ create-dmg 설치 확인 (brew install create-dmg)
```

## Phase 3 — 문서

```
□ docs/README.md                        (문서 인덱스)
□ docs/specs/                           (디자인 스펙)
□ docs/adr/                             (ADR - 아키텍처 결정)
□ docs/plans/                           (구현 플랜)
□ docs/guides/github-discoverability.md templates/github-discoverability.md.tmpl
□ docs/assets/                          (스크린샷 / GIF 보관소)
```

## Phase 4 — GitHub 메타데이터 (Layer 1)

```
□ Topics 등록 (gh repo edit --add-topic)
  └ 10~15개, 관련 없는 태그 금지
□ Description 한 줄 작성 (gh repo edit --description)
□ About 사이드바 홈페이지 링크 (해당 시)
□ Social preview 이미지 업로드
  └ https://github.com/OWNER/REPO/settings#social-preview
  └ 크기 1280×640 px
  └ socialify.git.ci 또는 직접 디자인
```

## Phase 5 — 스크린샷 & 데모 (Layer 2 시각 자료)

```
□ 메뉴바 아이콘 스크린샷 (상태별)
□ 패널/창 전체 스크린샷
□ 핵심 인터랙션 GIF (Kap / Gifox 30초 이내)
□ docs/assets/ 에 저장
□ README 에 embed
```

## Phase 6 — 첫 릴리스

```
□ 버전 tag (semver, v0.1.0)
□ ./Distribution/Release.sh 0.1.0
□ dist/{app}-0.1.0.dmg 생성 확인
□ GitHub Release 생성 + .dmg 업로드
  └ gh release create v0.1.0 dist/*.dmg
□ SHA256 기록 → Distribution/HomebrewTap/{app}.rb 업데이트
```

## Phase 7 — Homebrew tap (Layer 3)

```
□ OWNER/homebrew-tap public repo 생성 (기존 것 재사용 가능)
□ Casks/{app}.rb 푸시
□ 설치 테스트: brew install --cask OWNER/tap/{app}
□ 일반 사용자가 `brew tap OWNER/tap` + `brew install --cask {app}` 으로 되는지 검증
```

## Phase 8 — 발견성 부스트 (Layer 3)

시간 여유 있을 때, 하나씩:

```
□ awesome-* 리스트 PR
  └ awesome-macos, awesome-menu-bar-apps, 도메인 별 (예: awesome-tmux)
□ Reddit 자체 규칙 확인 후 포스팅
  └ r/MacApps, 도메인 별
□ Hacker News "Show HN" 런치 (오전 9시 PST)
□ Product Hunt (Tuesday/Wednesday PST 오전)
□ Twitter/X 포스트
□ 개인 블로그/뉴스레터 커버
```

## Phase 9 — 운영 파일 (선택)

트래픽이 생기기 시작하면:

```
□ CHANGELOG.md           (semver 별 변경사항)
□ CONTRIBUTING.md        (기여 가이드)
□ CODE_OF_CONDUCT.md     (CoC, Contributor Covenant 템플릿)
□ SECURITY.md            (보안 리포트 채널)
□ .github/ISSUE_TEMPLATE/
  ├ bug_report.md
  └ feature_request.md
□ .github/PULL_REQUEST_TEMPLATE.md
□ .github/workflows/ci.yml (빌드/테스트 자동화)
□ .github/workflows/release.yml (tag push → dmg 자동 빌드)
```

---

## 체크리스트 핵심 원칙

- **"사용자 스크롤 안 하려고 한다"** → Quick start 블록을 README 최상단에
- **"키워드 미스매치 = 미발견"** → Topics + Description 에 검색어 포함
- **"한 번 공유, 여러 곳에서 유입"** → Social preview 이미지 준비
- **"설치 장벽 = 폐기"** → Homebrew cask 한 줄 설치가 최종 목표
- **"보여주는 게 설명보다 강하다"** → 스크린샷 + GIF 필수
