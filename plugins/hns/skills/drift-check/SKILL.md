---
name: drift-check
description: Use to check whether an implementation has drifted from its hns spec — document-state, contract, verification, and decision drift with file:line evidence.
user-invocable: false
---

# drift-check

입력: 스펙 폴더(`spec.md` `tasks.md` `context/*` `status.md`). 출력: `context/drift-check.md`.

## 절차
1. 문서를 모두 읽는다.
2. 스펙이 언급한 클래스·API·상태 전이를 Grep 으로 찾는다. 인용(`{file}:{line}`) 없는 finding 은 무효.
3. 네 렌즈:
   - **A 문서-상태**: status.md 와 tasks.md 의 완료 주장이 일치하는가
   - **B 계약**: API 형태·엔티티 필드·상태 전이·요청/응답 스키마 대 스펙
   - **C 검증**: AC 별 테스트 존재, 스펙에 없는 행동의 테스트, 미해결 open question
   - **D 결정**: 코드 행동 대 key-decisions.md, 결정 기록 없는 비자명 경로
4. 분류: CRITICAL(정확성·계약 파괴) / MAJOR / MINOR(문서 공백).
5. 보고서: Executive Summary · Findings(근거 포함) · Evidence Table · Recommended Next Action.

## 결론 (정확히 하나)
`ALIGNED` | `ALIGNED WITH AMENDMENTS NEEDED` | `NOT ALIGNED`
