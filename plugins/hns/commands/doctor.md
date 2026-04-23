---
description: "Run layered docs/harness health check — 4-layer diagnostic with PASS/WARN/FAIL + score. 문서 헬스체크, 독터, doctor, 진단"
---

# /hns:doctor

## Purpose
프로젝트 문서/하네스 구조를 4개 레이어로 진단한다.
각 레이어는 독립적으로 PASS / WARN / FAIL 판정을 내고,
가중 평균으로 0-100 score가 계산된다.

## Layers
| ID | 이름 | 검사 내용 | Weight |
|---|---|---|---|
| L1 | Index Integrity | `docs/index.yml` 존재, 등록 파일 실재, orphan 문서 유무 | 30 |
| L2 | Agent Guidance | `CLAUDE.md` 존재 + build/test/run 섹션 | 25 |
| L3 | Harness Alignment | broken internal link, stale `harness-gc-report.md` | 25 |
| L4 | Evidence Coverage | `docs/specs/`, `docs/standards/` 문서의 `<!-- source: ... -->` 인용 비율 | 20 |

## Required Inputs
- 프로젝트 루트 접근 권한

## Expected Outputs
- 콘솔 리포트 (기본)
- `docs/verify/DOCTOR_REPORT.md` (`--output-md` 시)
- `docs/verify/DOCTOR_REPORT.json` (`--output-json` 시, CI용)
- Exit code: `0` PASS / `1` FAIL / `2` WARN

## Execution

### 기본
```bash
python3 ai/plugins/hns/scripts/doctor.py .
```

### CI 모드 (strict + 파일 저장)
```bash
python3 ai/plugins/hns/scripts/doctor.py . \
  --strict \
  --output-md docs/verify/DOCTOR_REPORT.md \
  --output-json docs/verify/DOCTOR_REPORT.json
```

### pre-commit 모드 (non-blocking)
```bash
python3 ai/plugins/hns/scripts/doctor.py . --warn-only
```

## Idempotency
여러 번 실행해도 같은 입력이면 같은 리포트. 파일 출력은 덮어쓴다.
산출물(`DOCTOR_REPORT.md/json`)은 git에 커밋 금지 — `.gitignore` 에 추가 권장.

## Flags
- `--strict` — WARN을 FAIL로 취급 (exit 1)
- `--warn-only` — FAIL이어도 exit 0 (pre-commit 용)
- `--json` — JSON을 stdout으로
- `--output-md PATH` — Markdown 리포트 파일
- `--output-json PATH` — JSON 리포트 파일
- `--setup-precommit` — git pre-commit 훅 설치 후 종료 (one-shot)

## Triage guide
- **L1 FAIL**: `docs/index.yml`을 먼저 만들거나 등록 누락 문서 추가. `/hns:init` 로 템플릿 주입 가능.
- **L2 FAIL**: `CLAUDE.md` 최상위에 Build / Commands 섹션 추가.
- **L3 FAIL (broken link)**: 실제 경로 확인 후 링크 교정. 템플릿 placeholder(`{...}`)는 자동 제외됨.
- **L3 WARN (stale harness-gc-report)**: `/hns:gc` 실행.
- **L4 FAIL**: spec/standard 문서 상단에 `<!-- source: path/to/code.ext -->` 추가.

## Related
- `/hns:gc` — 전체 청소 (doctor 이후 자동 수정용)
- `/hns:setup-hooks` — pre-commit 훅 + CI 워크플로 설치
- `/hns:validate` — docs↔code drift 검증

## NEVER
- 사용자 확인 없이 auto-fix 수행 금지 (doctor는 진단만)
- `docs/verify/` 산출물을 git에 커밋 금지
