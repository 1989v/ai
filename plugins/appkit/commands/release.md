---
description: "신규 릴리스 컷: semver git tag → .dmg 빌드 → GitHub Release 업로드 → SHA256 계산 → Homebrew tap 업데이트. Trigger: 릴리스, release 만들어, 배포, 태그, dmg 빌드"
---

# /appkit:release

앱 첫 릴리스 / 신규 버전 릴리스 전체 파이프라인 실행.

## Usage

```
/appkit:release 0.1.0                  # v0.1.0 릴리스
/appkit:release 0.2.0 --draft          # 초안만 생성
/appkit:release --dry-run              # 명령만 미리보기
```

## 사전 체크

- `./Distribution/Release.sh` 존재?
- `create-dmg` 설치됨? (`brew install create-dmg`)
- `gh` 로그인 되어있음? (`gh auth status`)
- Git working tree 깨끗? uncommitted 있으면 경고
- 현재 branch 가 `main` 인지 확인
- 버전이 semver 형식인지 검증 (`^\d+\.\d+\.\d+(-\w+)?$`)
- 해당 버전이 이미 태그 존재하면 중단

## 단계

### 1. Git tag 생성

```bash
# 변경사항 전부 커밋 확인
git status
git log --oneline main..HEAD

# tag 생성 (annotated)
git tag -a v0.1.0 -m "aieye 0.1.0

- 주요 변경사항
- 주요 변경사항
"

# push
git push origin v0.1.0
# 또는: git push --tags
```

**규칙**:
- Tag 형식: `v<major>.<minor>.<patch>[-<pre>]` (ex. `v0.1.0`, `v0.2.0-rc1`)
- Annotated tag 사용 (`-a` flag) — tag 에 메시지 포함
- Pre-release 는 `-rc1`, `-beta1`, `-alpha1` 등 suffix
- Release tag 는 영구 보존 — 삭제/교체 금지 (문제 시 patch 버전 올림)

### 2. `.dmg` 빌드

```bash
./Distribution/Release.sh 0.1.0
```

결과: `dist/<app>-0.1.0.dmg` + SHA256 출력.

### 3. GitHub Release 생성

**release notes 초안**:

```bash
# 이전 태그부터 현재까지 커밋 추출
git log v0.0.x..v0.1.0 --pretty=format:"- %s" --reverse

# Release 생성
gh release create v0.1.0 dist/<app>-0.1.0.dmg \
    --title "<app> 0.1.0" \
    --notes "$(cat <<'EOF'
## What's new

- feature A
- fix B

## Installation

```bash
brew install --cask OWNER/tap/<app>
```

또는 DMG 직접 다운로드 후 우클릭 → 열기 (ad-hoc 서명).
EOF
)"
```

**draft 옵션**: `--draft` 추가하면 초안만 생성 → 웹 UI 에서 검토 후 publish.

### 4. SHA256 기록

```bash
# DMG 의 SHA256
shasum -a 256 dist/<app>-0.1.0.dmg | awk '{print $1}'
```

`Distribution/HomebrewTap/<app>.rb` 의 `sha256` 필드를 이 값으로 업데이트.

### 5. Homebrew tap 반영

```bash
# tap repo clone (최초 1회)
git clone https://github.com/OWNER/homebrew-tap.git ~/homebrew-tap
cd ~/homebrew-tap

# cask 파일 복사
cp <project>/Distribution/HomebrewTap/<app>.rb Casks/<app>.rb

# 커밋 & 푸시
git add Casks/<app>.rb
git commit -m "<app>: 0.1.0"
git push
```

**검증**:
```bash
brew tap OWNER/tap
brew install --cask <app>
<app>  # 실행 확인
brew uninstall --cask <app>  # cleanup (zap 섹션 확인)
```

### 6. 체크리스트

```
✓ git tag v0.1.0 생성 + push
✓ dist/<app>-0.1.0.dmg 생성
✓ GitHub Release 공개 (draft 아닐 때)
✓ SHA256 Homebrew cask 업데이트
✓ homebrew-tap repo push
✓ brew install --cask OWNER/tap/<app> 검증

다음 단계:
  /appkit:discover   — awesome-* / HN / Reddit 포스팅
  /appkit:pages      — GitHub Pages 랜딩 페이지 (배너 공개)
```

## Rollback

릴리스에 문제 발생 시:
- **Release 취소**: `gh release delete v0.1.0 --cleanup-tag`
- **Tag 만 삭제**: `git tag -d v0.1.0 && git push origin :refs/tags/v0.1.0`
- **Homebrew tap 롤백**: 이전 커밋으로 revert

단, **푸시된 tag 는 가급적 유지** — 사용자 install 이력에 영향. 문제 있으면 patch 버전 (`0.1.1`) 으로 수정본 배포 권장.
