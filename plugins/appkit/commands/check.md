---
description: "현재 레포가 CHECKLIST 의 Phase 0~9 중 어디까지 완료됐는지 진단. 누락 항목 + 다음 단계 제안. Trigger: appkit 진단, 체크리스트, 완성도 확인, check launch"
---

# /appkit:check

현재 디렉토리의 레포가 **신규 앱 launch 체크리스트의 어디까지 왔는지** 진단.

## Usage

```
/appkit:check               # 전체 진단
/appkit:check --verbose     # 각 항목 세부 설명
/appkit:check --fix         # 누락 항목 자동 수정 제안 (적용 X)
```

## Phase 별 진단 항목

### Phase 0 — 기본 셋업
- `.git` 디렉토리 존재
- `origin` remote 설정
- main branch 기준 commit 1개 이상

### Phase 1 — 코어 파일
- `README.md` (영문) 존재
- `README.md` 에 Quick start 블록 (`git clone` + 설치 명령)
- `README.md` 에 Badge ≥ 2개
- `README.ko.md` (글로벌 타겟 시 권장)
- `LICENSE` 파일
- `.gitignore` (OS/빌드 아티팩트 포함)
- `build.sh` 또는 equivalent

### Phase 2 — 배포 인프라
- `Distribution/README.md`
- `Distribution/Release.sh` 또는 equivalent
- `Distribution/HomebrewTap/<app>.rb` (macOS 앱 한정)
- `create-dmg` 설치 여부 (시스템 체크)

### Phase 3 — 문서
- `docs/README.md`
- `docs/specs/` 디자인 스펙 ≥ 1개
- `docs/adr/` ADR ≥ 1개
- `docs/plans/` 구현 플랜 ≥ 1개
- `docs/guides/github-discoverability.md`
- `docs/assets/` 디렉토리 (스크린샷 보관소)

### Phase 4 — GitHub 메타데이터
- `gh repo view --json repositoryTopics` → topics ≥ 8개
- `gh repo view --json description` → description 존재 (50자+)
- Social preview 업로드 여부 (`opengraph.githubassets.com` 체크)

### Phase 5 — 스크린샷 & 데모
- `docs/assets/*.png` 이미지 ≥ 2개
- `docs/assets/*.gif` 데모 GIF (선택)
- README 내 `![...](docs/assets/...)` 임베드 ≥ 1개

### Phase 6 — 첫 릴리스
- Git tag `v*` ≥ 1개 (`git tag -l "v*"`)
- `gh release list` → 릴리스 ≥ 1개
- 릴리스에 `.dmg` / 바이너리 첨부

### Phase 7 — Homebrew tap
- `OWNER/homebrew-tap` 별도 repo 존재
- `Casks/<app>.rb` 최신 버전의 sha256 반영
- 설치 테스트 성공 (`brew install --cask` dry-run)

### Phase 8 — 발견성 부스트
- 이 항목은 수동 진단 필요 (외부 링크 체크)
- 사용자에게 yes/no 로 물어보고 마킹:
  - awesome-* 리스트 등재 ≥ 1
  - Reddit / HN / PH 포스팅 ≥ 1
  - 개인 블로그 / Twitter 공유

### Phase 9 — 운영 파일 (선택)
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/workflows/` CI

## Output 형식

```
📋 APP_NAME launch 완성도 진단

Phase 0 — 기본 셋업:              ✅ (3/3)
Phase 1 — 코어 파일:              ⚠️  (5/7) — README.ko.md, LICENSE 없음
Phase 2 — 배포 인프라:            ❌ (0/4) — Distribution/ 전체 누락
Phase 3 — 문서:                   ⚠️  (3/6)
Phase 4 — GitHub 메타데이터:      ❌ (0/3) — Topics 없음
Phase 5 — 스크린샷:               ❌ (0/3)
Phase 6 — 첫 릴리스:              ❌ (0/3)
Phase 7 — Homebrew tap:           —  (not applicable 또는 pending)
Phase 8 — 발견성:                 —  (수동)
Phase 9 — 운영 파일:              ⚠️  (1/6) — 선택 사항

전체 진행률: 12/35 (34%)

💡 다음 권장 액션 (우선순위):
1. /appkit:init                  → Phase 1~2 누락 파일 생성
2. /appkit:seo                    → GitHub topics/description 설정
3. /appkit:pages                  → docs/assets/ 에 스크린샷 추가
4. /appkit:release 0.1.0          → 첫 릴리스
```

## 기호 체계

- ✅ 완료
- ⚠️ 부분 (n/m 형태로 진행도)
- ❌ 미완
- — 해당 없음 / 수동 확인 필요

## `--fix` 옵션

누락 항목 대해 실행 가능한 커맨드 제안 (자동 실행 X, 표시만):

```
누락: Distribution/Release.sh
실행: /appkit:init
```

사용자가 선택 후 원하는 명령 직접 실행.
