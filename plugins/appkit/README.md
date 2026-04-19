# appkit

**신규 데스크톱 앱 launch kit** — scaffold → SEO → release → discoverability 까지 한 번에.

## 설치

```bash
claude marketplace add https://github.com/1989v/ai.git --name ai-common  # 최초 1회
claude plugins install appkit@ai-common
```

## 커맨드

| 명령 | 용도 |
|---|---|
| `/appkit:start` | 현재 디렉토리 상태 진단 → 다음 phase 자동 라우팅 |
| `/appkit:init` | 빈 레포에 boilerplate 일괄 생성 (README / LICENSE / Distribution) + 토큰 치환 |
| `/appkit:seo` | GitHub topics / description / social preview 가이드 + `gh` 명령 제시 |
| `/appkit:release` | `.dmg` 빌드 + GitHub Release 생성 + Homebrew tap 업데이트 |
| `/appkit:discover` | awesome-* PR / HN / Reddit 포스팅 초안 생성 |
| `/appkit:check` | Phase 0~9 대비 현재 레포 완성도 진단 |

## 지원 앱 유형 (v0.1)

- ✅ macOS 메뉴바 앱 (Tauri, SwiftUI 등 스택 무관)
- 🔜 macOS 일반 앱
- 🔜 Windows 트레이 앱
- 🔜 CLI 도구

## 검증 사용처

- [muxbar](https://github.com/1989v/muxbar) — Swift/SwiftUI tmux 세션 관리
- [aieye](https://github.com/1989v/aieye) — Tauri+React AI CLI 세션 모니터링

## 설계 철학

3-Layer 발견성:
1. **Layer 1 — GitHub 메타데이터**: Topics, Description, Social preview
2. **Layer 2 — README 품질**: Quick start, 언어 스위처, 스크린샷, Badge
3. **Layer 3 — 외부 인덱스**: Homebrew cask, awesome-* PR, Product Hunt, HN, Reddit

자세한 근거: [docs/philosophy.md](docs/philosophy.md) · 체크리스트: [docs/CHECKLIST.md](docs/CHECKLIST.md)

## 하네스 통합 (옵션)

`hns` 플러그인이 함께 설치된 경우 `/appkit:init --with-harness` 로 하네스 엔지니어링 문서(CLAUDE.md, agent-os/, docs/adr) 도 초기 생성. 자세한 내용: [references/harness-integration.md](references/harness-integration.md)
