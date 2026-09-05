---
name: evolve
description: Use to encode a repeated agent failure or a user correction into the harness so it does not recur — routes it to auto memory, a path-scoped rule, a hook, CLAUDE.md, or a skill, and records the change.
disable-model-invocation: true
argument-hint: "[failure description]"
---

# /hns:evolve

## 입력
실패 설명(사용자 제공 또는 최근 세션에서 감지: 검증 루프 3회 초과, spec-review BLOCK, verify 실패, "이거 하지 마").

## 분류 → 대상
| 교정의 성격 | 대상 | 이유 |
|---|---|---|
| 취향·선호·한 번의 교정 | **auto memory** (`feedback` 타입) — Claude 가 스스로 적는다 | 가장 싸고, 세션마다 로드 |
| 특정 경로에서만 지켜야 하는 규칙 | `.claude/rules/{topic}.md` + `paths:` | 그 파일을 읽을 때만 컨텍스트 소모 |
| 매 세션 항상 참인 사실·명령 | CLAUDE.md (200줄 상한) | 항상 로드 |
| 특정 시점에 **반드시** 검사·차단 | 훅 (`references/hooks-reference.md`) | 컨텍스트는 강제가 아니다 |
| 도구·명령 자체 금지 | `permissions.deny` | 클라이언트가 강제 |
| 다단계 절차 | 스킬 (`disable-model-invocation` 로 트리거 통제) | 호출될 때만 로드 |
| 리뷰가 놓친 스펙 결함 | `skills/spec-review/reviewers/{dim}/` 체크리스트 | 다음 리뷰부터 |

## 절차
1. 실패를 한 문장으로 적고, 위 표에서 대상을 **하나** 고른다. 두 곳에 같은 규칙을 쓰지 않는다.
2. 제안(규칙 문장 + 대상 파일 + 이유)을 보여주고 승인을 받는다.
3. 적용. 훅이면 실패 입력을 주입해 빨간불을 본 뒤에만 켰다고 한다(`templates/hooks/README.md`).
4. `docs/changelog/harness-changelog.md`: `[date] [evolve] [{target}: {rule}] [근거: {failure}]`.

## NEVER
- 한 번의 실패로 여러 규칙 추가 (최소 제약)
- 검증되지 않은 패턴을 규칙으로
- 사용자 확인 없이 CLAUDE.md·settings 수정
