---
description: "두 레포지토리의 합성된 CLAUDE.md/메모리/settings 컨텍스트를 비교한다. 공통/단독/상충 룰을 가시화하여 글로벌 정책의 레포 간 일관성을 점검. 자연어 트리거: 레포 룰 비교, 클로드 컨벤션 diff, 프로젝트 간 룰 차이."
argument-hint: "<repo-A-path> <repo-B-path> [--strict|--warn|--loose] [--by-topic|--tree]"
---

# /claude-md:diff

두 레포의 합성된 컨텍스트를 비교하여 **공통 / 단독 / 상충(divergent)** 룰을 분류한다.

## 사용 예

```bash
# msa 와 kafka-lens 의 글로벌+프로젝트 룰 비교
/claude-md:diff ~/IdeaProjects/msa ~/IdeaProjects/kafka-lens

# 현재 cwd 와 다른 레포 비교 (cwd 가 A 로 자동 사용)
/claude-md:diff . ~/IdeaProjects/quant-tools
```

## 옵션

| Flag | 의미 |
|------|------|
| `--strict` / `--warn` / `--loose` | evidence 검증 강도 (analyze 와 동일) |
| `--by-topic` | 주제별 그룹화 출력 |
| `--tree` | 레이어 트리 비교 |
| `--json` | raw JSON 출력 |

## 실행 흐름

### 1. 각 레포 분석

각 레포 경로에 대해 `/claude-md:analyze --json --source=auto` 동작을 내부적으로 수행:

- `scripts/collect-layers.sh <repo-path>` → 인벤토리
- 컨텍스트 해시 + 캐시 조회 (있으면 재사용)
- introspect → rule list (Active + Overridden, 각 항목에 source/topic/text)
- evidence 검증 (모드에 따라)

두 레포에 대해 `{repo, rules[], summary}` 두 묶음을 얻는다.

### 2. 주제 매칭 (LLM 의미 매핑)

두 레포의 rule list 를 **topic 기준 의미 매핑**. introspect 에 직접 위임:

- A 의 룰 텍스트 + B 의 룰 텍스트를 함께 보고
- 같은 주제(동의어/패러프레이즈 포함) 룰끼리 짝지움
- 결과를 다음 4개 버킷으로 분류:
  - `shared`: 같은 주제 + 같은 지시 (Active 끼리 일치)
  - `divergent`: 같은 주제 + 다른 지시 (양쪽 모두 Active 인데 텍스트 충돌)
  - `only_A`: A 에만 존재
  - `only_B`: B 에만 존재

### 3. 출력 (디폴트)

```
🔀 diff: msa  ▶◀  kafka-lens
─────────────────────────────────────────────────────────────────
✅ shared (12)     │ 양쪽이 같은 지시
⚠ divergent (3)   │ 양쪽이 충돌하는 지시
🅰 only msa (8)    │ msa 에만 존재
🅱 only kl (5)     │ kafka-lens 에만 존재

⚠ divergent rules:
주제                | msa 측                  | kafka-lens 측             | 비고
테스트 작성 규칙     | CLAUDE.md:42 (project) | CLAUDE.md:18 (project)   | 정책 표류 의심
@Transactional      | order/CLAUDE.md:88     | (없음)                    | A 만 정의
로깅 형식           | CLAUDE.md:120          | CLAUDE.md:55              | 한쪽이 outdated 가능
```

`--by-topic` 면 각 divergent 주제 안에 양쪽 텍스트를 같이 표시.
`--tree` 면 레이어 계층 트리 두 개를 좌우 병치.
`--json` 면 raw 출력:

```json
{
  "diff": {
    "repo_a": "/Users/.../msa",
    "repo_b": "/Users/.../kafka-lens",
    "summary": { "shared": 12, "divergent": 3, "only_a": 8, "only_b": 5 },
    "shared":     [ { "topic": "...", "text_a": "...", "text_b": "..." } ],
    "divergent":  [ { "topic": "...", "text_a": "...", "text_b": "...", "note": "..." } ],
    "only_a":     [ { "topic": "...", "text": "...", "source": "..." } ],
    "only_b":     [ ... ]
  }
}
```

## 구현 노트

- 두 레포 분석은 캐시 활용 — 같은 컨텍스트 해시면 introspect 생략
- 비교 단계는 introspect 한 번에 양쪽 rule list 를 전달해 매핑 (별도 alignment 알고리즘 없음)
- divergent 항목의 `note` 필드는 introspect 가 자유 서술 (예: "정책 표류 의심", "한쪽이 outdated 가능") — 사용자가 정성적 판단에 활용
- 결과를 어느 한쪽에 자동 적용하지 않음 (관찰만, 수정은 별도 도구 #16 토글러 책임)
