# Exported Modules

`claude-md-analyzer` 가 외부(특히 idea #16 — CLAUDE.md 프로필 토글러)에 공개하는 내부 모듈 인터페이스. 변경 시 semver patch 가 아닌 minor bump 필요.

## 1. `collect-layers.sh`

**입력**: cwd 경로 (positional `$1`)

**출력**: stdout 으로 JSON 배열. 각 항목:

```json
{
  "path": "<absolute>",
  "layer": "global" | "user" | "project" | "ancestor" | "local",
  "bytes": 1234,
  "modified": "ISO8601",
  "token_estimate": 320
}
```

**호환성 보장**:
- 출력 JSON 의 필드 이름은 추가만 되고 제거되지 않음 (semver minor)
- `layer` enum 은 신규 추가될 수 있음 (`global` / `user` / `project` / `local` 는 영구)
- 빈 인벤토리 시 `[]` 반환

**사용 예 (#16 토글러)**: 토글링 대상 파일 후보 enumeration. 사용자가 "글로벌 CLAUDE.md 만 토글" 선택 시 `layer === "global"` 항목 필터링.

## 2. `hash-context.sh`

**입력**: 인벤토리 JSON (file path or `-` for stdin)

**출력**: stdout 으로 단일 SHA256 hex digest (64 chars)

**호환성 보장**:
- 입력 인벤토리가 동일하고 참조된 파일들의 내용이 동일하면 같은 hex 반환 (deterministic)
- 누락 파일은 `:missing` 마커로 처리되어 해시에 포함

**사용 예 (#16 토글러)**: 토글링 전후 상태의 컨텍스트 fingerprint 비교 (예: `claude_origin.md` 와 토글된 `CLAUDE.md` 의 합산 상태가 같은지 검증).

## 3. `verify-source.sh`

**입력**:
```
verify-source.sh <path> <start> [end]
verify-source.sh --match <path> <start> <end> <expected_substr>
```

**출력**:
- non-match 모드: stdout 으로 추출된 라인 텍스트
- match 모드: stdout 없음, 종료 코드만

**Exit codes**:
- `0`: OK (file exists, line in range, substring matched if --match)
- `1`: file missing
- `2`: line out of range
- `3`: substring mismatch (--match only)
- `64`: usage error

**사용 예 (#16 토글러)**: 토글링 전 원본 라인이 예상 텍스트와 일치하는지 확인 (충돌 방지 가드).

## 4. `detect-dead-stale.sh`

**입력**: rules JSON (file path, positional `$1`) + cwd (positional `$2`)

**출력**: stdout 으로 동일 스키마의 rules JSON. 각 rule 에 다음 필드 주입:

- `stale_reason`: `"path-missing"` | `"line-out-of-range"` | null
- `dead_reason`: `"path-bound-irrelevant"` | `"permanently-overridden"` | null
- summary 의 `stale` / `dead` 카운트 자동 갱신

**호환성 보장**:
- `unreferenced` 휴리스틱은 본 스크립트가 처리하지 않음 (introspect 책임)
- 추가 reason 값은 신규 추가 가능 (위 두 enum 은 영구)

**사용 예 (#16 토글러)**: "토글링 대상이 이미 dead 인지" 사전 점검. 사용자가 dead 룰을 토글링하려 하면 경고.

## 5. Cache 디렉토리 구조

**경로**: `~/.claude/projects/{slug}/cma-cache/{hash}.json`

**slug**: cwd 의 `/` 를 `-` 로 치환 (예: `/Users/foo/proj` → `-Users-foo-proj`)

**hash**: hash-context.sh 출력값

**JSON 스키마**: 본 README `## 페이로드 스키마` 섹션 참조 (`skills/cache-manager/SKILL.md`)

**호환성 보장**:
- 외부 모듈이 캐시 파일을 직접 읽어도 무방 (read-only)
- 외부 모듈의 쓰기는 권장하지 않음 — `cache-manager` skill 경유 필요 시 별도 인터페이스 추가

## 6. Snapshot 디렉토리 구조

**경로**: `~/.claude/projects/{slug}/cma-snapshots/{YYYYMMDD}T{HHMMSS}Z-{event}.json`

**JSON 스키마**:
```json
{
  "event": "SessionStart"|"PreToolUse"|"unknown",
  "timestamp": "ISO8601",
  "cwd": "<absolute>",
  "context_hash": "<sha256>",
  "inventory": [ ... ]   // collect-layers.sh 출력과 동일
}
```

**호환성 보장**:
- 외부 모듈이 스냅샷 파일을 직접 읽어도 무방
- retention: 최근 50개 유지 (FIFO trim, `cma-snapshot.sh` 자동 관리)

## Versioning

본 export 인터페이스는 `claude-md-analyzer` 의 plugin.json `version` 과 함께 관리.

- patch (0.0.x): 버그 수정, 출력 형식 미세 조정
- minor (0.x.0): 신규 필드/enum/스크립트 추가 (기존 호환)
- major (x.0.0): 기존 인터페이스 제거/시그니처 변경

`#16` 토글러는 자기 `package.json` 또는 `plugin.json` 의 `peerDependencies` 에 `claude-md-analyzer >=1.0.0 <2.0.0` 같은 형태로 lock 권장.
