# appkit 철학 — 왜 이 3-Layer 인가

## 설계 원칙

appkit 은 **"제품 완성도 ≠ 발견 가능성"** 을 전제로 한다. 좋은 OSS 가 발견되지 않는 이유는 대개 기술 문제가 아니라 **유통(distribution) 에 대한 무관심**이다. 이 플러그인은 muxbar·aieye 를 실제로 출시하며 적용한 "노출 3-Layer" 를 체계화한다.

## Layer 1 — GitHub 메타데이터 (수동적 발견)

**가정**: 사용자는 검색한다. `topic:claude-code` 로, `macos menu bar` 로, `tauri session` 으로.

**대응**:
- **Topics** 10~15개 — 도메인/스택/플랫폼/통합 대상 전 방향 커버
- **Description** — 한 줄에 핵심 키워드 전부 포함 (검색 결과 리스트에 바로 보임)
- **Social preview 1280×640** — 링크 공유 시 시각적 카드 (Slack/Twitter 뷰)

**Miss 시 비용**: 검색 유입 0. 입소문 의존.

## Layer 2 — README 품질 (초초깊은 퍼널)

**가정**: 방문자는 3초 안에 "써볼 만한가" 판단한다.

**대응**:
- **Quick start 블록** 최상단 — 스크롤 불필요, 복붙 3줄
- **Badge** — 신뢰 신호 (라이선스, 플랫폼, 버전)
- **언어 스위처** — 글로벌 타겟이면 영/한 병행
- **스크린샷 / GIF** — 텍스트 설명보다 10배 강력
- **Feature matrix** — 버전/모드별 지원 범위 표로

**Miss 시 비용**: 방문은 하지만 이탈. stars / install 전환 떨어짐.

## Layer 3 — 외부 인덱스 (능동적 유입)

**가정**: 특정 커뮤니티는 그들의 루틴 (awesome-list / 서브레딧 / HN) 을 먼저 본다.

**대응**:
- **Homebrew cask** — macOS 사용자 "brew search" 루틴에 노출
- **awesome-* 리스트 PR** — 도메인 매칭 유입
- **Hacker News / Reddit / Product Hunt** — 타이밍 마케팅 (런치 데이)

**Miss 시 비용**: 새 유입 파이프라인 없음. 기존 팬 이상 커뮤니티 확장 불가.

## 왜 "앱 개발" 과 분리하는가

- **작업의 결이 다름**: 기능 구현(hns 도메인) vs 레포 런치(appkit 도메인)
- **대상 사용자 다름**: 자체 프로젝트 개발자 vs 외부 OSS 공개자
- **도구의 리듬 다름**: 기능은 여러 번 반복 / 런치는 한 번 + 후속 버전

두 흐름을 하나의 플러그인에 섞으면 **원칙이 얽혀 둘 다 흐려짐**. 그래서 appkit 은 독립 플러그인.

## 검증 사례

| 프로젝트 | Stack | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---|---|
| [muxbar](https://github.com/1989v/muxbar) | Swift/SwiftUI | ✅ Topics 12개 | ✅ Bilingual + Badge | 진행 중 |
| [aieye](https://github.com/1989v/aieye) | Tauri+React | 진행 중 | ✅ Bilingual + Badge | 진행 중 |

## 반례 — 흔한 실수

- **"README 는 개발자용이니까 한국어만"** → 글로벌 유입 0
- **"topics 나중에 하지"** → 검색 노출 기회 손실 (topic 페이지 트래픽)
- **"릴리스는 dmg 만 올리면 되지"** → Homebrew 사용자 스킵 (macOS 인스톨의 70%)
- **"스크린샷은 나중에"** → 방문 → README → 이탈 루프

appkit 은 이 4개 실수를 **체크리스트로 강제**한다.
