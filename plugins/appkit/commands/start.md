---
description: "appkit 통합 진입점. 현재 디렉토리 진단 후 다음 phase(init/seo/release/discover) 자동 라우팅. Trigger: 새 앱 만들래, 앱 출시, 배포 준비, OSS 런치, app kit"
---

# /appkit:start

신규 데스크톱 앱 출시 워크플로우의 통합 진입점.
현재 디렉토리 상태를 진단해서 다음으로 진행할 phase를 자동 판단한다.

## Usage

```
/appkit:start                    # 진단 후 자동 라우팅
/appkit:start --force init       # phase 건너뛰고 강제로 init
/appkit:start --with-harness     # 하네스 엔지니어링 문서 포함 (hns 설치 시)
```

## PHASE 0 — Diagnose

현재 디렉토리를 조사:

1. **Git 상태**
   - `.git/` 존재? remote origin 설정? 푸시된 커밋 있음?
2. **코어 파일**
   - `README.md`, `LICENSE`, `.gitignore` 존재?
   - `README.ko.md` 등 언어 스위처?
3. **배포 인프라**
   - `Distribution/Release.sh`, `Distribution/HomebrewTap/*.rb` 존재?
4. **문서**
   - `docs/guides/github-discoverability.md`, `docs/assets/*.png`?
5. **GitHub 메타데이터** (gh CLI 있으면)
   - `gh repo view --json repositoryTopics,description`
   - Topics 개수, Description 존재 여부
6. **릴리스 이력**
   - `dist/*.dmg`, `gh release list` 결과
7. **Homebrew tap**
   - `1989v/homebrew-tap` 같은 별도 레포 존재?

## PHASE 1 — Route

진단 결과에 따라 다음 phase 제시:

| 현재 상태 | 다음 단계 |
|---|---|
| README/LICENSE 없음 | → `/appkit:init` |
| 코어 파일 있음, Topics 미설정 | → `/appkit:seo` |
| SEO 완료, 릴리스 없음 | → `/appkit:release <version>` |
| 릴리스 있음, Homebrew tap 없음 | → `/appkit:release` (tap 업데이트) |
| 다 있음, 외부 노출 안함 | → `/appkit:discover` |
| 다 완성 | → "축하! 필요한 작업 없음. 진단 리포트만 표시" |

사용자에게 진단 리포트 (O/X/~) 와 다음 명령을 함께 제안한 뒤, 선택 확인.

## PHASE 2 — Hand-off

사용자가 다음 phase 선택하면 해당 명령으로 hand-off:
- 추가 정보 필요하면 (app 이름, GitHub owner 등) 먼저 수집
- 하위 명령(`/appkit:init` 등) 호출 — 또는 사용자가 직접 실행하도록 명령어만 제시

## 핵심 원칙

- **한 번에 하나의 phase만 실행** — 결과 확인 후 다음으로
- **파괴적 동작은 반드시 확인** (기존 파일 덮어쓰기 등)
- **진단 결과 먼저 보여주기** — 사용자가 상황 파악하게
- **hns 통합은 옵셔널** — hns 플러그인이 있으면 `--with-harness` flag 로만 동작
