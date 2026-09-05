---
name: spec-evolution
description: Use while implementing a spec-driven feature when a new edge case, contract gap, or requirement change is discovered — governs open-questions.yml and append-only spec amendments.
user-invocable: false
---

# Spec Evolution

## 원칙
- **Unknown first**: 예상 밖 발견은 코드로 해결하기 전에 `context/open-questions.yml` 에 적는다.
- 승인된 스펙 본문은 고치지 않는다. `## Amendments` 섹션에 append 한다.
- 버그·수정안·보류를 같은 무게로 다루지 않는다.

## 분류
| category | 뜻 |
|---|---|
| `pre-impl` | 구현 전에 반드시 해소 (열려 있으면 구현 차단) |
| `impl-discovery` | 구현 중 발견 |
| `test-discovery` | 테스트 중 발견 |
| `closure` | 완료 경계가 모호 |
| `waiver-revisit` | 지금은 수용, 나중에 재검토 |

## Amendment 승격 기준 (하나라도 해당)
- 조용한 데이터 손상 가능
- 외부 계약(API·이벤트·스키마) 변경
- AC 의 의미 변경
- 재시도·락·멱등성 의미 변경

## 읽을 것
`spec.md` · `context/key-decisions.md` · `context/open-questions.yml`(없으면 생성) · `tasks.md`

## NEVER
- 발견을 코드에만 반영
- open-questions.yml 없이 진행
- 승인된 스펙 전면 재작성
