---
description: "View or change docs-health CI workflow mode (full/diagnose/off). 비용 모드 변경, 워크플로 끄기, 워크플로 모드, health mode, cost switch"
---

# /hns:health-mode

## Purpose
docs-health 워크플로의 `HNS_DOCS_HEALTH_MODE` GitHub repo variable을 조회/변경한다.
PR 없이 즉시 적용되며, 다음 workflow run 부터 효과 발생.

## Modes
| 값 | 동작 | 토큰 비용 |
|---|---|---|
| `full` (default) | 진단 + Claude auto-fix 전체 실행 | 정상 |
| `diagnose` | 진단만 실행. Claude 호출 step 모두 skip | **0** |
| `off` | 워크플로 전체 early-exit | **0** |

## Required Inputs
- `gh` CLI 설치 + 인증 (`gh auth status`로 확인)
- 현재 디렉토리가 git repo (또는 `--repo <owner>/<repo>` 명시)

## Expected Outputs
- 현재 모드 조회 (인자 없을 때)
- 모드 변경 완료 메시지 (인자 있을 때)

---

## Execution

### 조회 (인자 없음)
```bash
# 현재 repo의 변수 확인
gh variable list | grep HNS_DOCS_HEALTH_MODE || echo "mode=full (variable not set, using default)"
```

### 변경
```bash
# full/diagnose/off 중 하나
gh variable set HNS_DOCS_HEALTH_MODE --body "<mode>"
```

### 기본값 복귀 (variable 삭제)
```bash
gh variable delete HNS_DOCS_HEALTH_MODE
```

### 다른 레포 대상
```bash
gh variable set HNS_DOCS_HEALTH_MODE --body "diagnose" --repo <owner>/<repo>
```

---

## Interactive flow

1. **사전 검증**
   - `gh auth status` 성공 여부 확인 → 실패 시 `gh auth login` 안내
   - `.github/workflows/docs-health.yml` (또는 트리거 래퍼) 존재 확인 → 없으면 경고하되 진행 가능 (variable 만 선행 설정)

2. **현재 모드 조회**
   ```bash
   gh variable list --json name,value --jq '.[] | select(.name=="HNS_DOCS_HEALTH_MODE") | .value'
   ```
   결과 없으면 `full` (default) 로 표기.

3. **사용자 의도 확인**
   - 인자 없음 → 조회 결과만 출력하고 종료
   - `full` / `diagnose` / `off` 중 하나 지정 → 다음 단계
   - 다른 값 → 거부 + 허용 값 안내

4. **파괴적 변경 경고**
   - `off` 로 변경 시: "모든 Claude 자동 수정이 중단됩니다. 계속?" 확인
   - `diagnose` 로 변경 시: "진단은 유지되나 auto-fix PR은 생성되지 않습니다. 계속?" 확인
   - `full` 로 복귀 시: 경고 없이 진행

5. **적용**
   ```bash
   gh variable set HNS_DOCS_HEALTH_MODE --body "<mode>"
   ```
   실패 시 권한/인증 이슈 원인 분석.

6. **사후 안내**
   - 적용 시점: 진행 중인 workflow run 은 영향 없음, 다음 run 부터 적용
   - 변경 이력은 GitHub Settings 에서 추적 불가 → 감사 필요 시 커밋 로그나 PR 본문에 기록 권장

---

## Idempotency
같은 모드로 재설정 시 no-op. `gh variable set` 은 upsert 동작.

## Safety rules
- 비어있는 값(`""`)으로 설정 금지 — workflow 가 `full` fallback 처리하지만 의도 불명확
- 알 수 없는 값 설정 금지 (`partial`, `readonly` 등) — workflow 는 `full` fallback 하지만 사용자 오해 위험

## Related
- `/hns:setup-hooks` — 워크플로 최초 설치
- `docs/benchmarks/2026-04-24-cost-gate-design.md` — 모드 설계 근거

## NEVER
- GitHub Secrets 에 저장 금지 (평문 variable 이 올바른 위치)
- 워크플로 파일 직접 수정으로 모드 고정 금지 — variable 로 관리해야 즉시 반영 + 감사 가능
- 사용자 확인 없이 `off` / `diagnose` 전환 금지 (auto-fix 중단은 파괴적 효과)
