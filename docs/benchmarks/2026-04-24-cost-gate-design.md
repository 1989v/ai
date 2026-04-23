# Cost Gate Design — docs-health 워크플로 비용 스위치 (2026-04-24)

## 배경
`docs-health.yml` 워크플로는 3개 지점에서 Claude API를 호출한다:
- `stale-doc-update` (push-triggered): 커밋 빈도에 비례하여 토큰 소비 — **폭주 가능**
- `doc-quality-gc` (weekly cron): 주당 1회, 비용 제한적
- `doctor-check` (weekly cron + FAIL/WARN 시만): 주당 1회 조건부

pre-commit hook / hygiene job / doctor 진단은 로컬 Python이라 무료.

## 문제
기존 스위치(`inputs.jobs` 콤마 리스트, `schedule_*` cron)만으로는:
- 변경이 워크플로 파일 수정 PR을 통해서만 가능 → 긴급 kill-switch 불가
- 환경별(staging/dev) 차등 설정 어려움
- 예산 ceiling 도달 시 "진단만 유지하고 auto-fix만 중단" 같은 계단식 비활성 불가

## 설계
### Repo-level variable
`HNS_DOCS_HEALTH_MODE` (GitHub Actions variable, not secret)

| 값 | 동작 |
|---|---|
| `full` (default) | 전체 실행 — 진단 + Claude auto-fix |
| `diagnose` | 진단 job 모두 실행. Claude 호출 step은 **모두 skip** (토큰 0) |
| `off` | 워크플로 최상단 early-exit. 모든 job skip |

Settings → Secrets and variables → Actions → **Variables** 탭에서 즉시 변경 가능.
PR / 코드 변경 없이 적용.

### 구현 포인트
1. `resolve-config` job이 `vars.HNS_DOCS_HEALTH_MODE`를 읽어 `autofix_enabled` output 계산
2. `off` 모드: 모든 `run_*` output을 `false`로 강제 설정 → 의존하는 후속 job이 자동으로 skip
3. `diagnose` 모드: `autofix_enabled=false` 로 설정 → 3개 Claude 호출 step이 gate에서 skip
4. 각 Claude 호출 step의 `if:` 조건에 `needs.resolve-config.outputs.autofix_enabled == 'true'` 추가
5. 알 수 없는 값은 `full`로 fallback + warning 로그

### gate 적용 위치
- `Run Claude — Stale Doc Fix` (line ~301)
- `Run Claude — Doc Quality GC` (line ~370)
- `Run Claude — Doctor Auto-fix` (line ~478)

pre-commit 훅은 gate 없음 — 로컬 실행이라 비용 제로. 강제 비활성 원하면 `git commit --no-verify`.

## 사용 시나리오
- **정상 운영**: variable 미설정 또는 `full`. 자동화 full-on.
- **비용 폭주 감지**: `off` 즉시 설정 → 다음 실행부터 전부 차단. 원인 조사 후 `full` 복귀.
- **월 예산 초과 임박**: `diagnose` 설정 → Claude 호출 중단, 진단만 유지. DOCTOR_REPORT는 계속 생성되어 수동 검토 가능.
- **staging/dev 레포**: `off` 설정 후 방치.
- **CI debug**: `diagnose` 로 실행해서 진단 결과 확인, PR 없이 검토.

## 비용 추정 (참고)
2026-04 현재 `claude-sonnet-4-5` 기준, 평균 세션당:
- stale-doc-update 1회: $0.05~0.20 (변경 파일 수에 비례)
- doc-quality-gc 1회: $0.10~0.50 (docs/ 규모에 비례, 120분 제한)
- doctor-check auto-fix 1회: $0.05~0.30

주당 총 예상: $0.20~1.00 + push 빈도에 따라 stale-doc가 $1~$10 추가.
월 환산 $5~$50 범위. 대규모 docs/ + 빈번한 push 시 $100+도 가능.

**→ 월 $50 예산 기준, stale-doc가 예산의 60~80% 차지. 폭주 위험 가장 큼.**
첫 배포 후 1~2주는 `diagnose` 모드로 관찰하는 것을 권장.

## 미해결 / 향후 개선
- 일일/월별 실행 횟수 카운트 기반 자동 `diagnose` 전환 (현재 수동)
- Claude 호출 전후 토큰 usage 로깅 (metrics_repo 활용 가능)
- 팀/org 단위 전역 mode 전파 (repo별 variable 설정 필요 — org-level var 도입 검토)

## 변경 요약 (2026-04-24)
- `plugins/hns/templates/ci/docs-health.yml`: `vars.HNS_DOCS_HEALTH_MODE` 읽는 `resolve-config` 확장, `autofix_enabled` output 신설, 3개 Claude step에 gate 추가
- 헤더 주석에 모드 사용법 명시
