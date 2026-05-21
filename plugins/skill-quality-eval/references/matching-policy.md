# Matching Policy (필드 단위 매칭 정책)

스킬마다 `goldset/{skill-id}/schema/matching-policy.json` 을 한 번 작성. 필드별로 매칭 모드 / 배열 매칭 키 / 정렬 규칙을 지정.

## v0.1 지원 매칭 모드

| 모드 | 동작 |
|---|---|
| **strict** | 정규화 후 deep-equal (필드·값 완전 일치) |
| **structural** | 키 셋·타입만 일치, 값은 type-check 만 |
| ~~semantic~~ | v0.2+ — LLM-as-judge (Haiku) — 자연어 필드 전용. v0.1 에서는 strict 또는 structural 로 강등됨 |

## 배열 비교 옵션

| 옵션 | 의미 | 예시 |
|---|---|---|
| `match-by` | 키 값으로 순서 무관 페어링 후 매칭 | `match-by: "name"` → terms[*].name 기준으로 페어링 |
| `sort-by` | 정규화 후 동일 키 기준 정렬 후 deep-equal | `sort-by: ["name"]` |
| `ordered` | 입력 순서 그대로 비교 (기본값) | — |

`match-by` 가 지정되면 그 키가 누락된 항목은 "orphan" 으로 fail.

## 정규화 (Normalization)

`normalize` 블록으로 비교 전 적용:

| 룰 | 동작 |
|---|---|
| `case: lower` | 문자열 소문자화 |
| `trim: true` | 양끝 공백 제거 |
| `collapse-whitespace: true` | 연속 공백을 한 칸으로 |
| `null-equals-missing: true` | null 과 키 없음을 동일 취급 |

## 예시: hns:glossary

```json
{
  "$root": {
    "fields": {
      "terms": {
        "match-by": "name",
        "normalize": { "case": "lower", "trim": true },
        "fields": {
          "name": "strict",
          "type": "strict",
          "description": "structural",
          "evidence": "structural"
        }
      },
      "metadata": {
        "fields": {
          "generated_at": "structural",
          "skill_version": "strict"
        }
      }
    }
  }
}
```

- `terms` 배열은 `name` 키로 페어링 (순서 무관)
- `terms[*].name` / `terms[*].type` 은 strict (완전 일치)
- `terms[*].description` / `terms[*].evidence` 는 structural (v0.1 — v0.2 에서 semantic 으로 승격 예정)
- `metadata.generated_at` 은 매번 바뀌므로 structural 로 두어 형식만 검증

## v0.1 제약

- **semantic 모드는 strict 로 강등**. matching-policy.json 에 `semantic` 이 적힌 필드는 v0.1 runner 가 경고 + strict 처리.
- **정규화 룰은 위 4가지만 지원**. 커스텀 transform 은 v0.2+.

## Default

`matching-policy.json` 이 없거나 빈 객체면 **strict (배열 ordered, 정규화 없음)** 가 디폴트.
