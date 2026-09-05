# Prompting Tone Guide

Claude 5(Fable 5.1·Opus 5·Sonnet 5)는 지시 준수율이 높다. 강조 표현은 과잉 발화를 부르고, 리마인더 체크리스트는 모델이 이미 아는 것을 다시 말한다.

## 원칙
강한 어조 대신 **조건이 명확한 지시**. "언제" 를 적고 "얼마나 중요한지" 는 적지 않는다.

| 이전 | 지금 |
|---|---|
| `CRITICAL: You MUST use this tool when...` | `Use this tool when...` |
| `EXTREMELY IMPORTANT: NEVER skip...` | `Do not skip...` |
| `This is not negotiable.` | (삭제) |
| "400줄 이하인지 확인했나요?" 리마인더 | 규칙 문장 하나: "400줄을 넘기면 이유를 적는다" |
| "8가지 상태를 모두 구현했나요?" | 검사 스크립트로 (판단이 아니라 기계적 확인이면 코드로) |

## 강한 어조가 맞는 곳
- 데이터 손실·보안 등 안전 제약
- Iron Law(검증 루프 3회 실패 시 STOP, 증거 없는 완료 없음)
- 사용자 승인 게이트(L3)

## 스킬 작성
- `description` 은 **언제 쓰는지**만. 절차를 요약하면 모델이 본문을 읽지 않고 요약대로 움직인다.
- 본문은 호출된 뒤 턴마다 컨텍스트에 남는다. 한 줄이 반복 비용이다.
- 모델이 아는 것은 쓰지 않는다("PDF 란…"). 모델이 모르는 프로젝트 사실·판단 기준만.

출처: Anthropic *Effective context engineering for AI agents* ("smarter models require less prescriptive engineering"), Claude Code skills 문서.
