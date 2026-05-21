# Snapshot Layout (정답셋 · 평가 산출물 디렉토리 규약)

평가 1회 = 스냅샷 디렉토리 1개. 그 시점의 스킬 사본·schema·정답·결과·diff 가 한 곳에 모이는 **자체 완결 감사 단위**.

## Top-level 디렉토리

```
goldset/{skill-id}/
├── schema/
│   ├── output.schema.json        # 평가용 JSON 계약 (스킬당 1)
│   └── matching-policy.json      # 필드별 매칭 모드 / sort-by / match-by
├── fixtures/                      # 코드베이스 의존 스킬의 입력 픽스처 (옵션)
├── snapshots/
│   ├── {YYYY-MM-DD-tag}/         # 스냅샷 디렉토리 (시간순)
│   └── ...
└── current -> snapshots/{baseline-tag}    # 활성 baseline (심볼릭 링크)
```

**Skill ID 표기**: 콜론을 하이픈으로 (`hns:glossary` → `hns-glossary`).

## 스냅샷 디렉토리 (baseline)

```
snapshots/2026-05-22-baseline/
├── source-skill/                  # 그 시점 원본 스킬 사본 (감사용, read-only)
│   └── SKILL.md
├── forked-skill/                  # source-skill + JSON overlay (실제 실행체 사본)
│   └── SKILL.md
├── cases/
│   └── case-001/
│       ├── input.yml              # 스킬 호출 인자 (사람 작성)
│       └── expected.json          # 정답 (사람 1회 컨펌 후 박힘)
├── report.md                       # 사람용 리포트
└── report.json                     # 머신 리더블 리포트
```

baseline 스냅샷은 **`expected.json` 만 보유** (실제 실행 결과는 baseline 이 곧 정답이므로 별도 저장 안 함).

## 스냅샷 디렉토리 (after-fix, 자동)

```
snapshots/2026-05-23-after-fix/
├── source-skill/                  # 그 시점 (변경된) 원본 스킬 사본
│   └── SKILL.md
├── forked-skill/                  # 변경본 + overlay
│   └── SKILL.md
├── cases/
│   └── case-001/
│       ├── actual.json            # 실제 출력 (schema 검증된 JSON)
│       └── diff.md                # expected vs actual 사람용 diff
├── diff-vs-baseline.md            # 회귀 케이스 종합 (case-by-case PASS/FAIL/diff)
├── report.md
└── report.json
```

후속 스냅샷은 **`actual.json` + `diff.md`** 보유. baseline 의 `expected.json` 과 비교한 결과가 `diff-vs-baseline.md`.

## 명명 규칙

스냅샷 디렉토리 이름: `{YYYY-MM-DD}-{tag}`

| Tag 예시 | 용도 |
|---|---|
| `baseline` | 사람 컨펌 baseline. `current` 심볼릭 링크 대상 |
| `after-{change}` | 스킬 수정 후 자동 평가 (예: `after-fix`, `after-refactor`) |
| `auto-{N}` | tag 미지정 시 자동 생성 (예: `auto-001`) |

## `current` 심볼릭 링크

활성 baseline 을 가리킴. 후속 스냅샷의 매칭 대상은 항상 `current/cases/*/expected.json`.

baseline 갱신은 명시적 `/skill-eval:promote {skill-id} {snapshot-id}` 만 가능 — cyclic 자동 갱신 차단.

## report.json 스키마

```json
{
  "skill_id": "hns-glossary",
  "snapshot_id": "2026-05-23-after-fix",
  "created_at": "2026-05-23T14:30:00Z",
  "baseline_id": "2026-05-22-baseline",
  "summary": {
    "total_cases": 5,
    "pass": 4,
    "fail": 1,
    "format_fail": 0
  },
  "cases": [
    {
      "case_id": "case-001",
      "result": "pass | fail | format-fail",
      "match_mode": "strict",
      "diff_summary": "0 fields differ"
    }
  ]
}
```
