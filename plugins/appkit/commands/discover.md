---
description: "외부 발견성 부스트: awesome-* 리스트 PR, Product Hunt, Reddit, Hacker News 포스팅 초안 생성. Trigger: 홍보, 외부 노출, awesome list, product hunt, reddit, show hn"
---

# /appkit:discover

Layer 3 발견성 — 레포 밖으로 나가서 적극적 유입 경로 확보.

## Usage

```
/appkit:discover             # 전체 채널 체크리스트 + 초안 생성
/appkit:discover --channel awesome    # 특정 채널만
/appkit:discover --channel reddit
/appkit:discover --channel hn
/appkit:discover --channel ph
```

## 1. awesome-* 리스트 PR

도메인 매칭되는 리스트에 한 줄 추가 PR.

**찾는 법**:
```bash
# GitHub 검색
gh search repos "awesome-{domain}" --sort stars --limit 20
```

**자주 쓰는 리스트**:

| 리스트 | 범위 |
|---|---|
| [awesome-macos](https://github.com/iCHAIT/awesome-macOS) | macOS 앱 전반 |
| [awesome-menu-bar-apps](https://github.com/muan/awesome-menu-bar-apps) | 메뉴바 앱 |
| [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Claude Code 생태계 |
| [awesome-tauri](https://github.com/tauri-apps/awesome-tauri) | Tauri 앱 |
| [awesome-swift](https://github.com/matteocrippa/awesome-swift) | Swift 프로젝트 |
| [awesome-rust](https://github.com/rust-unofficial/awesome-rust) | Rust 프로젝트 |
| [awesome-cli-apps](https://github.com/agarrharr/awesome-cli-apps) | CLI 도구 |
| [awesome-opensource](https://github.com/bayandin/awesome-oss) | OSS 일반 |

**PR 템플릿**:
```markdown
- [APP_NAME](https://github.com/OWNER/APP_NAME) - ONE_LINER (macOS, Stack).
```

- 알파벳 순서 유지
- 기존 포맷 그대로 (대시/백틱/링크 스타일)
- 설명 최대 ~100자
- PR title: `Add APP_NAME`

**fork → edit → PR** 흐름:

```bash
gh repo fork OWNER/awesome-list --clone
cd awesome-list
# README.md 수정
git checkout -b add-APP_NAME
git commit -am "Add APP_NAME"
git push -u origin add-APP_NAME
gh pr create --title "Add APP_NAME" --body "..."
```

## 2. Product Hunt

**적합성 판단**:
- ✅ 완성도 있는 소비자/개발자 앱
- ✅ 스크린샷 + GIF 풍부
- ❌ MVP 수준, 기능 부족

**준비물**:
- Tagline (60자 이내): `The [X] for [Y]`
- Description (260자): 한 문제 → 해결 → 차별점
- Gallery (1~5장): 대표 스크린샷 + 배너
- Demo video (선택, 30~60초)

**런칭 타이밍**: Tuesday/Wednesday PST 오전 (상위 노출 유리)

**URL**: https://www.producthunt.com/posts/new

## 3. Reddit

도메인별 서브:

| 서브 | 주제 |
|---|---|
| r/MacApps | macOS 앱 |
| r/ClaudeAI | Claude 사용자 |
| r/LocalLLaMA | AI 개발자 |
| r/tmux | tmux 사용자 |
| r/rust | Rust 프로젝트 |
| r/swift | Swift 프로젝트 |
| r/opensource | 일반 OSS |
| r/selfhosted | 셀프호스팅 관련 |

**제목 공식**: `[Category] Project-Name — one-line benefit`

**본문 구조**:
```
I built X because Y (pain point).

- Feature 1
- Feature 2
- Feature 3

GitHub: https://...
Homebrew: brew install --cask ...

Tech stack: Tauri/Swift/...

Open to feedback!
```

**주의**:
- 각 서브의 self-promotion 규칙 먼저 확인 (오래된 계정 / karma 필요)
- 홍보만 올리지 말고 커뮤니티 참여 후 올리는 게 환영 받음
- 같은 내용 여러 서브에 동시 X-post 금지 (스팸 신고)

## 4. Hacker News — "Show HN"

**형식**:
```
Show HN: APP_NAME – One-line description
```

**본문**:
```
Hi HN,

I built APP_NAME because I was frustrated by X.

- 주요 기능 1
- 주요 기능 2
- 주요 기능 3

It's open source (MIT) on GitHub: https://github.com/...
brew install --cask OWNER/tap/APP_NAME

I'd love feedback — especially on [specific area].
```

**타이밍**: 오전 9시 PST 근처 (HN 트래픽 피크 시작)
**본인 첫 댓글**: 맥락 설명 + 질문 유도 (관례)
**URL**: https://news.ycombinator.com/submit

## 5. Twitter/X / LinkedIn

**짧은 형식** (280자):
```
Built APP_NAME: ONE_LINER.

Why: one-sentence problem
How: one-sentence solution

OSS: github.com/OWNER/APP_NAME
brew install --cask OWNER/tap/APP_NAME

#macOS #tmux #rust (#해시태그 3-5개)
```

GIF 또는 스크린샷 첨부 필수 — engagement 크게 차이남.

## 6. 체크리스트

```
□ awesome-* 리스트 1~3개 선정 → 각각 PR
□ Product Hunt 런치 (Tuesday/Wednesday PST)
□ Reddit 1~2개 서브 포스팅 (규칙 확인 후)
□ Hacker News Show HN (오전 9시 PST)
□ Twitter/X / LinkedIn 개인 계정
□ (선택) 개인 블로그 글 / Dev.to / Medium
□ (선택) 커뮤니티 Discord/Slack 공유
```

## 측정

런치 후 2주간:
- GitHub stars / forks 변화
- Homebrew downloads (`brew analytics --cask OWNER/APP_NAME`)
- Referrer 분석: Repo Insights → Traffic

피드백 모음 → 다음 버전 우선순위 결정에 활용.

## 참고

- [awesome 리스트 maintainer 가이드](https://sindresorhus.com/awesome/)
- [Show HN guidelines](https://news.ycombinator.com/showhn.html)
- [Product Hunt launch guide](https://www.producthunt.com/launch)
