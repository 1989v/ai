# Output Format — Hybrid (default)

`/claude-md:analyze` 의 디폴트 출력은 **요약 헤더 + Conflict-only** 하이브리드 뷰다.

## 콘솔 (default)

```
📊 42 rules / ⚠ 5 conflicts / ❓ 0 unverifiable / 🗂 0 stale
─────────────────────────────────────────────────────────────────────────
주제                | 승자                       | 패자                          | 근거
────────────────────|───────────────────────────|───────────────────────────────|────────
테스트 작성 규칙     | CLAUDE.md:42 (project)    | ~/.claude/CLAUDE.md:17 (global) | project > global
@Transactional 규칙 | order/CLAUDE.md:88 (local)| CLAUDE.md:120 (project)        | local > project
...
```

### 헤더 아이콘 의미

| 아이콘 | 카운트 | 의미 |
|--------|-------|------|
| 📊 | total_rules | 추출된 룰 총 개수 |
| ⚠ | conflicts | Overridden 상태의 충돌 룰 개수 |
| ❓ | unverifiable | evidence 검증 실패 룰 개수 (warn 모드에서 결과에 포함된 것만) |
| 🗂 | stale | 참조 path 가 없어진 룰 개수 (M2) |

### 본문 컬럼

| 컬럼 | 내용 |
|------|------|
| 주제 | introspect 가 분류한 룰 주제 (자유서술) |
| 승자 | 적용 중인 룰의 `path:line` + `(layer)` 약식 |
| 패자 | 덮어써진 룰의 `path:line` + `(layer)` |
| 근거 | Claude Code 우선순위 규칙에 따른 결정 근거 (예: `local > project`) |

### unverifiable 행 표시

evidence 검증 실패 항목은 행 우측에 `❓` 아이콘 추가:

```
주제           | 승자                | 패자                | 근거             |   |
모킹 금지 규칙 | CLAUDE.md:??:hint  | global:17 (global) | project > global | ❓
```

## `--all` 옵션

기본 출력 아래에 Active 룰 섹션 추가:

```
... (conflicts 표) ...

✅ Active rules (37):
────────────────────
주제              | 위치                       | 레이어
도메인 분리 원칙  | CLAUDE.md:8                | project
@Transactional   | order/CLAUDE.md:88         | local
...
```

## `--unverifiable` 옵션

unverifiable 룰만 별도 표시:

```
❓ Unverifiable rules (3):
────────────────────
주제              | 보고된 위치                | 검증 실패 사유
TDD 규칙          | CLAUDE.md:??              | line out of range
로깅 규칙         | global:17                  | text mismatch
...
```

## `--by-topic` 옵션

주제별 그룹 + 각 주제 안에서 Active/Overridden 표시:

```
📌 테스트 작성 규칙
   ⚠ Overridden — CLAUDE.md:42 (project)  ▶  ~/.claude/CLAUDE.md:17 (global)
                  근거: project > global
   ✅ Active     — domain/test-rules.md:8 (local)

📌 @Transactional 규칙
   ⚠ Overridden — order/CLAUDE.md:88 (local)  ▶  CLAUDE.md:120 (project)
                  근거: local > project
   ✅ Active     — common/CLAUDE.md:55 (local)
...
```

## `--tree` 옵션

레이어 계층 트리:

```
🌐 global (~/.claude/)
  ├─ CLAUDE.md           14 rules  (3 overridden)
  └─ memory/MEMORY.md    8 rules   (0 overridden)
📁 project (msa/)
  ├─ CLAUDE.md           22 rules  (5 winner)
  └─ order/CLAUDE.md     6 rules   (2 winner)
```

## JSON export (`--json`)

```json
{
  "summary": {
    "total_rules": 42,
    "conflicts": 5,
    "unverifiable": 0,
    "stale": 0,
    "rejected": 0
  },
  "rules": [
    {
      "topic": "...",
      "status": "Active"|"Overridden",
      "winner": { "source": "path:line", "text": "...", "layer": "..." },
      "loser": { "source": "path:line", "text": "...", "layer": "..." } | null,
      "resolution": "local > project" | null,
      "verification": { "status": "verified"|"unverifiable", "reason": "..." }
    }
  ],
  "cached_at": "ISO8601",
  "context_hash": "<sha256>"
}
```

## 컬러 컨벤션

- ⚠ Overridden: 노랑/주황
- ✅ Active: 녹색
- ❓ Unverifiable: 회색
- 🗂 Stale: 빨강
- 헤더 아이콘 좌측은 굵게 (`\e[1m`)

terminal 이 컬러를 지원하지 않으면 (`NO_COLOR=1` / pipe 출력) 평문으로 fallback.
