---
name: glossary
description: Use when building or evolving the project's domain glossary — defines 5 modes (Bootstrap/Grilling/Conflict/Scan/Review), inline update discipline, and ADR offer rules
user-invocable: false
---

# /hns:glossary — Skill Procedure

## Reference
`@references/language-reference.md` — 포맷·규칙의 단일 출처. 충돌 시 reference가 우선.

## Iron Laws

1. **Inline update**: 용어가 확정되는 *그 순간* `glossary.md`를 갱신. 배치 금지.
2. **Domain-expert vocabulary only**: 구현 디테일(Repository/DTO/Handler/Service 등) 등재 금지.
3. **Avoid section mandatory**: 폐기된 동의어를 반드시 기록 — 회귀 차단.
4. **Conflict surfaces silence**: 사용자가 사전과 모순되는 용어를 쓰면 즉시 질의. 침묵 진행 금지.
5. **One question at a time** (Grilling Mode): 결정 트리를 한 가지 분기씩 내려간다.

---

## PHASE A: Bootstrap Mode

`glossary.md`가 없을 때.

1. **Scan candidates**:
   - `agent-os/product/mission.md`에서 명사 추출
   - 코드베이스 패키지/디렉토리 이름 중 도메인 후보 (Spring 패키지의 `domain/` 하위, 클래스 이름 빈도)
   - 기존 `docs/specs/*/spec.md`에서 자주 등장하는 명사
2. **Cluster & rank**:
   - 동일 개념의 표기 변종 그룹화 (예: `order` / `Order` / `주문`)
   - 빈도순 정렬, 상위 5-10개 선정
3. **Grill user (1 term at a time)**:
   - 후보 제시 → 사용자 정의 요청 → Definition / Avoid / Code 매핑 채움
   - 추천 답안 먼저 제시 후 수정 받기
4. **Initialize `agent-os/product/glossary.md`**:
   - reference의 포맷 그대로 작성
5. **Detect multi-BC need**:
   - 후보가 2개 이상의 명확히 다른 도메인으로 갈리면 → 사용자에게 *"context를 분리할까요?"* 질의
   - 승인 시 `docs/context-map.md` 작성 + BC별 glossary 위치 지정

## PHASE B: Grilling Mode

`glossary.md`가 있고 새 용어/모호 용어를 받았을 때.

1. **Load context**: 기존 glossary + 충돌 후보 검색
2. **One question at a time**:
   - "이 용어는 기존 X와 어떻게 다른가요? 같은 거라면 Avoid에 등재할까요?"
   - "이 단어를 쓸 때 사용자/도메인 전문가도 같은 의미로 쓰나요?"
   - 각 질문에 추천 답안 동반
3. **Inline update**: 한 용어 확정 시 즉시 파일 갱신
4. **Loop**: 미확정 용어가 남아 있으면 다음 용어로

## PHASE C: Conflict Mode

`--conflict {term}` 호출 또는 다른 스킬이 충돌을 감지해 트리거.

1. **Locate conflict source**:
   - glossary의 해당 용어 정의
   - 충돌이 발견된 위치 (spec.md / 코드 / 사용자 발언) 인용
2. **Present options**:
   - (a) glossary 정의 유지, 충돌 측 수정
   - (b) glossary 정의 갱신, 충돌 측 유지
   - (c) 새 용어로 분리 (둘 다 다른 개념이었음)
3. **Apply choice inline**
4. **Cross-update**: 옵션 (b)/(c) 선택 시 영향받는 spec/코드 위치를 사용자에게 알림

## PHASE D: Scan Mode

`--scan` 호출. Bootstrap의 1-2단계만 수행 + 결과를 사용자 검토 큐에 적재.

1. 코드/문서 스캔 → 후보 추출
2. 기존 glossary와 매칭 → 등재 / 충돌 / 신규로 분류
3. `agent-os/product/glossary-candidates.md` 작성:
   ```
   ## To Decide
   - {term} (occurrences: file:line, file:line) → similar to existing {existing}?
   ## Likely Domain Terms
   - {term} (occurrences) → propose Definition: ...
   ## Likely Implementation (skip)
   - {term}
   ```
4. 사용자에게 *"검토 후 /hns:glossary로 재진입하세요"* 안내

## PHASE E: Review Mode

`--review` 호출. 3자 정합성 점검.

1. **Glossary vs Code**:
   - 각 용어의 Code 매핑이 실제 코드에 존재하는가? (grep)
   - 매핑 누락 / 식별자 리네이밍 감지
2. **Glossary vs Specs**:
   - `docs/specs/*/spec.md`에서 Avoid 단어 사용 발견 → 경고
   - spec에 등장하는 도메인 명사 중 glossary 미등재 → 큐 적재
3. **Output**: `agent-os/product/glossary-review.md`
   - Critical / Warning / Info 분류
   - 각 항목에 file:line 증거

---

## PHASE Z: ADR Offer (모든 mode 공통, 종료 직전)

이번 세션에서 확정한 용어 중 다음 셋 **모두 참**인 것만:

1. **Hard to reverse** — 마이그레이션 비용
2. **Surprising without context** — 미래 독자가 의문
3. **Real trade-off** — 다른 후보가 있었음

→ 사용자에게 *"ADR로 기록할까요?"* 제안. 셋 중 하나라도 빠지면 묻지 않는다 (glossary 등재만으로 충분).

---

## NEVER

- 배치 갱신 (PR 끝에 모아서 한 번에 — 금지)
- 사용자 답 없이 추정으로 등재
- 구현 디테일을 도메인 용어로 등재
- Avoid 섹션 비워두기
- 한 번에 여러 질문 (One question at a time 위반)
- 사전 충돌 감지하고 침묵 진행
