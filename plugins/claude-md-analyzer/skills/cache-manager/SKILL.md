---
name: cache-manager
description: "컨텍스트 파일들의 SHA 해시를 키로 분석 결과를 디스크에 캐시/조회한다. 파일 하나라도 변경되면 자동 무효화. user-invocable: false."
---

# cache-manager (background skill)

`/claude-md:analyze` 의 분석 결과를 컨텍스트 파일 해시 기반으로 영구 캐시.

## 캐시 위치

```
~/.claude/projects/{slug}/cma-cache/{hash}.json
```

- `slug` = cwd 를 Claude Code 가 사용하는 형식으로 인코딩 (`/` → `-`, leading `/` 제거)
  - 예: `/Users/foo/IdeaProjects/msa` → `-Users-foo-IdeaProjects-msa`
- `hash` = 인벤토리에 포함된 모든 파일의 SHA256 합산 해시 (`scripts/hash-context.sh` 산출물)

## 동작

### get(hash)
1. 캐시 파일 경로 계산
2. 존재 + 읽기 가능 → 내용 반환 (JSON parse)
3. 그 외 → null

### put(hash, payload)
1. 디렉토리 없으면 `mkdir -p`
2. payload 를 atomic write (`.tmp` → `mv`)
3. 파일에 `cached_at` ISO8601 메타 자동 주입

### prune(older_than_days)
- M3 이후 hook 어댑터 활성 시: 파일 변경 감지 즉시 prune 호출
- M1: 사용자가 `--force` 로 명시 갱신할 때만 invalidate

## 페이로드 스키마

```json
{
  "cached_at": "2026-05-21T13:45:00Z",
  "cwd": "/Users/.../msa",
  "inventory_files": ["path1", "path2", ...],
  "summary": { "total_rules": 42, "conflicts": 5, "unverifiable": 0, "stale": 0 },
  "rules": [ ... ]
}
```

## 무효화 규칙

- 컨텍스트 파일 중 하나라도 SHA 가 바뀌면 hash 자체가 달라지므로 자동 miss
- 컨텍스트 파일이 추가/삭제되어도 인벤토리가 달라지므로 hash 자체가 달라짐
- `--no-cache`: 캐시 조회 자체 skip, put 도 skip
- `--force`: 캐시 조회 skip, put 은 수행 (강제 갱신)

## 사용 패턴

```text
1. analyze 커맨드 진입
2. collect-layers.sh → 인벤토리 JSON
3. hash-context.sh <인벤토리 JSON> → 해시
4. cache-manager.get(해시):
   - hit → 결과 그대로 출력 (3단계 introspect 생략)
   - miss → introspect + verify → cache-manager.put(해시, 결과)
5. 출력 렌더링
```

## 구현 노트

- 캐시는 단일 머신 / 단일 사용자 로컬 디스크 한정
- 동시 접근은 atomic write 로 충분, lock 불필요
- 캐시 디렉토리 자체가 없는 경우 자동 생성
- 캐시 파일 손상(JSON parse 실패) 시 silent 무시하고 miss 처리
