---
description: "Install doctor pre-commit hook + docs-health CI workflow in user project. 훅 설치, 프리커밋, CI 설치, setup hooks, precommit"
---

# /hns:setup-hooks

## Purpose
사용자 프로젝트에 doctor 헬스체크의 **pre-commit 훅**과 **docs-health CI 워크플로**를
one-shot으로 설치한다.

## Required Inputs
- 프로젝트 루트 접근 권한 (git repo 여야 함)
- 선택: 플러그인 레포 경로 (CI 워크플로가 참조할 org/repo)

## Expected Outputs
- `.git/hooks/pre-commit` 수정 (doctor 호출 append)
- `.github/workflows/docs-health.yml` (템플릿 복사)
- `.gitignore` 에 `docs/verify/` 추가 (doctor 산출물 제외)

---

## Execution

### Step 1 — pre-commit 훅 설치
```bash
python3 ai/plugins/hns/scripts/doctor.py . --setup-precommit
```
기존 pre-commit이 있어도 덮어쓰지 않고 append.
훅은 `--warn-only` 모드로 호출하므로 FAIL이어도 commit은 성립.

### Step 2 — CI 워크플로 복사
```bash
mkdir -p .github/workflows
cp ai/plugins/hns/templates/ci/docs-health.yml .github/workflows/docs-health.yml
```

그 후 `.github/workflows/docs-health.yml`을 `workflow_call`로 호출하는
얇은 래퍼를 작성한다. 예시:

```yaml
# .github/workflows/docs-health-trigger.yml
name: Docs Health

on:
  pull_request:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 1 * * 1'  # quality-gc
    - cron: '0 1 * * 3'  # doctor-check
  workflow_dispatch:

jobs:
  docs-health:
    uses: ./.github/workflows/docs-health.yml
    with:
      plugin_repo: <org>/<repo>    # hns 플러그인이 있는 레포
      plugin_ref: main
    secrets:
      ANTHROPIC_API_KEY_FOR_WORKFLOWS: ${{ secrets.ANTHROPIC_API_KEY_FOR_WORKFLOWS }}
      RUNNER_GH_TOKEN: ${{ secrets.RUNNER_GH_TOKEN }}
```

### Step 3 — .gitignore 갱신
```bash
grep -qxF 'docs/verify/' .gitignore || echo 'docs/verify/' >> .gitignore
```

### Step 4 — 필수 시크릿 안내
GitHub → Settings → Secrets and variables → Actions 에서 등록:
- `ANTHROPIC_API_KEY_FOR_WORKFLOWS` (필수)
- `RUNNER_GH_TOKEN` (선택, 없으면 `GITHUB_TOKEN` 사용)

---

## Idempotency
- **pre-commit**: 이미 등록된 경우 재 append 하지 않음 (marker 체크)
- **workflow 파일**: 존재하면 덮어쓸지 확인 프롬프트 필요
- **.gitignore**: 중복 line 추가하지 않음

## Interactive flow
1. git repo 인지 확인 → 아니면 abort
2. 위 4단계 수행, 각 단계 전 사용자 확인
3. 완료 후 `/hns:doctor` 실행 권장 메시지

## Uninstall
```bash
# pre-commit 제거
sed -i '' '/doctor.py.*--warn-only/d' .git/hooks/pre-commit
# CI 워크플로 제거
rm -f .github/workflows/docs-health.yml
```

## NEVER
- 사용자 확인 없이 파일 덮어쓰기 금지
- 기존 pre-commit 전체 교체 금지 (항상 append)
- CI 시크릿 값을 파일에 하드코딩 금지
