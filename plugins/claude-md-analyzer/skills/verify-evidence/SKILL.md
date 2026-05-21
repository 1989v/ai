---
name: verify-evidence
description: "introspect 결과의 source(file:line) 인용이 실제 파일에 존재하는지 cross-check 한다. --strict 모드는 검증 실패 항목을 제외, --warn 은 unverifiable 마킹 후 유지. user-invocable: false."
---

# verify-evidence (background skill)

introspect 가 보고한 룰 항목의 `source(file:line)` 인용을 fs 와 cross-check 하여 할루시네이션을 막는 게이트.

## 입력

```json
{
  "mode": "strict" | "warn" | "loose",
  "rules": [
    { "topic": "...", "status": "Active"|"Overridden", "winner": {"source":"path:line","text":"..."}, "loser": {...} }
  ]
}
```

## 출력

```json
{
  "verified": [...],
  "rejected": [...],         // strict 모드에서 검증 실패한 룰
  "unverifiable_count": 3
}
```

## 검증 알고리즘

각 룰 항목의 `winner.source` 와 `loser.source` (있다면) 에 대해:

1. **포맷 파싱**: `path:line` 또는 `path:start-end`
   - path 가 절대경로가 아니면 `unverifiable`
   - line 이 정수 아니면 `unverifiable`

2. **존재 확인**: `test -f "$path"` — 없으면 `unverifiable` (Stale 후보)

3. **라인 추출**: `scripts/verify-source.sh <path> <start> <end>` 호출
   - 파일을 읽어 해당 라인 범위 텍스트 반환
   - 라인이 파일 범위 초과면 `unverifiable`

4. **텍스트 매칭**: 추출한 라인 텍스트와 룰의 `text` 필드 비교
   - 정확 일치 → `verified=true`
   - 80% 이상 substring overlap → `verified=true` (introspect 가 요약/번역한 경우 허용)
   - 그 외 → `unverifiable=true, reason="text mismatch"`

5. **결과 적용**:
   - `mode=strict`: unverifiable 룰 전체를 `rejected` 로 이동
   - `mode=warn`: unverifiable 룰의 항목에 `verification.status="unverifiable"` 마킹 후 `verified` 에 유지
   - `mode=loose`: 검증 자체 skip, 모두 `verified` 로 패스스루

## 텍스트 매칭 휴리스틱

- 공백 정규화 (연속 공백 → 단일 공백, trim)
- 마크다운 기호 제거 (`-`, `*`, `#` 시작 부호 무시)
- 한글/영어 정규화 (소문자화)
- 80% overlap = (공통 트라이그램 수) / (룰 text 트라이그램 수)

## 구현 노트

- 본 스킬은 LLM 호출 없음 — 순수 bash + 텍스트 비교
- `mode=warn` 이 default 이며, CI 환경은 `mode=strict` 권장
- 검증 실패율(unverifiable_count / total) 이 30% 초과 시 도구가 사용자에게 introspect 신뢰도 경고 표시 (호출자 책임)
