---
name: glossary
description: Use when building or evolving the project's domain glossary — 8-phase deep analysis (file scan → class body → JPA → enum/sealed → events/Kafka → tests → docs/ADR → cross-check), with explicit Include/Exclude rules and 12-category output
user-invocable: false
---

# /hns:glossary — Skill Procedure (v0.9.0+)

## References (단일 출처)
- `@references/glossary-extraction-rules.md` — Include/Exclude, 7 Type 분류, 12 카테고리, Quality Gates
- `@references/language-reference.md` — 사전 포맷 + Module Language

충돌 시 `glossary-extraction-rules.md`가 우선.

## Modes

| Mode | Trigger | 절차 |
|---|---|---|
| **Deep** (기본 from v0.9.0) | `/hns:glossary` 또는 `/hns:glossary --deep` | PHASE 1~8 모두 수행 |
| **Shallow** (legacy v0.8.x) | `/hns:glossary --shallow` | 파일명 스캔만 (속도 우선) |
| **Conflict** | `/hns:glossary --conflict {term}` | 단일 용어 충돌 해소 |
| **Review** | `/hns:glossary --review` | 기존 사전 ↔ 코드 정합성 점검 |
| **Bootstrap** | glossary 없을 때 | Deep 모드 + 사용자 grilling으로 첫 5-10 용어 확정 |

---

## Iron Laws

1. **Inline update**: 용어 확정 시 즉시 파일 갱신. 배치 금지.
2. **Type-first classification**: 모든 용어는 7 Type(Aggregate/Entity/VO/Domain Service/Domain Event/Policy/Port) 중 정확히 하나로 분류. 미분류 시 등재하지 않고 Flagged.
3. **Exclude rule strict**: `*JpaEntity` / `*Adapter` / `*Config` / `*Dto` / `*Controller` 등은 자동 제외. 도메인 의미가 명확하면 Type 재분류 후 등재.
4. **8-source coverage**: Deep 모드는 8 소스(파일명/본문/JPA/enum-sealed/Exception/Kafka/Test/Docs)를 모두 본다. 누락 시 보고서에 명시.
5. **Quality Gate enforce**: 생성 후 Quality Gate 검증 자동 수행. 실패는 보고서에 표시.
6. **One question at a time** (grilling): 결정 트리를 한 가지 분기씩.

---

## PHASE 1: Scope Resolution

1. 단일 BC 인지 멀티 BC 인지 결정:
   - `agent-os/product/glossary.md` 존재 → 단일 BC 경로
   - `docs/context-map.md` 존재 → 멀티 BC, 표를 따라 각 BC 처리
2. 대상 BC 디렉토리 확정 (사용자 인자 또는 전체)
3. 출력 경로 결정 (`{bc}/glossary.md` 또는 `agent-os/product/glossary.md`)

## PHASE 2: Source Inventory

각 BC에 대해 다음 8 소스의 존재 여부 및 경로를 인벤토리화:

| # | Path pattern | 필수/선택 |
|---|---|---|
| 1 | `{bc}/domain/src/main/kotlin/**/*.kt` | 필수 |
| 2 | (위 .kt 각각의 첫 100줄) | 필수 |
| 3 | `{bc}/{domain,app}/src/main/kotlin/**/*JpaEntity.kt` | 선택 (JPA 사용 시) |
| 4 | enum/sealed 패턴 grep | 필수 (있을 때) |
| 5 | `{bc}/{domain,app}/src/main/kotlin/**/*Exception.kt` | 선택 |
| 6 | `{bc}/{app,consumer,batch}/src/main/kotlin/**/{Kafka*,*Consumer,*Producer}.kt` + topic 상수 | 선택 (이벤트 사용 시) |
| 7 | `{bc}/{domain,app}/src/test/kotlin/**/*.kt` (BehaviorSpec) | 선택 |
| 8 | `{bc}/CLAUDE.md`, `{bc}/docs/**`, `agent-os/product/mission.md`, `docs/adr/*`, `docs/specs/*` | 선택 |

누락된 소스는 보고서에 `(no source)` 마크.

## PHASE 3: Raw Candidate Extraction

각 소스에서 후보 명사를 추출 (분류 전):

- **Source 1 (파일명)**: 모든 `.kt` basename (제외 패턴 적용 후)
- **Source 2 (본문)**: 각 파일 상단 100줄에서:
  - `data class X(...)` → property 명사 추출 (예: `Order(val customerId, val items)` → `customerId`, `items`)
  - `sealed class X { class Y : X() }` → subtype 전부
  - `companion object { const val MAX_X = ... }` → 정책 상수
  - KDoc `/** ... */` → 자연어 정의 후보
- **Source 3 (JPA)**: `@Entity`, `@Column`, `@JoinColumn`, `@UniqueConstraint` → 관계·invariant
- **Source 4 (enum/sealed)**: `enum class X { A, B }` → 정책 분기 표현, sealed subtypes → 알고리즘 변형
- **Source 5 (Exception)**: 예외 클래스명 + 생성자 인자에서 invariant 단서
- **Source 6 (Kafka)**: `@KafkaListener(topics=...)`, `KafkaTemplate.send("topic.name", ...)` → 토픽 도메인 명사
- **Source 7 (test BehaviorSpec)**: `Given("...") When("...") Then("...")` → 비즈니스 시나리오
- **Source 8 (docs)**: 비즈니스 명사·acronym·정책 결정

원본 인용을 잃지 않기 위해 각 후보는 출처 위치(file:line)와 함께 보관.

## PHASE 4: Classification (7 Type)

`glossary-extraction-rules.md §1 §3` 적용:

각 후보에 대해:
1. Exclude 패턴 매칭 (`*JpaEntity` 등) → **제외** (단, 도메인 의미 명확 시 Type 재분류 후 진행)
2. 후보를 7 Type 중 하나에 매핑:
   - 트랜잭션 경계 + invariant 보유 → Aggregate
   - 식별자 있고 다른 Aggregate 종속 → Entity
   - 식별 없고 값 동치 → Value Object
   - stateless 도메인 로직 (여러 Aggregate 관여) → Domain Service
   - 사실 통보 → Domain Event
   - 의사결정 규칙 → Policy
   - 외부 추상화 인터페이스 → Port
3. 분류 불가 → Flagged Ambiguities (등재 X)

## PHASE 5: Metadata Enrichment

각 분류된 Term에 8필드 metadata 채움:

| 필드 | 출처 |
|---|---|
| Type | PHASE 4 결과 |
| Definition | KDoc → mission/CLAUDE.md → test BehaviorSpec given/when → 추정 (`(draft)`) |
| Lifecycle | sealed status enum, exception 메시지, 테스트 시나리오 |
| Invariants | Exception 클래스명·메시지, JPA constraints, sealed 분기 |
| Related events | Kafka topic mapping, `@EventListener`, `Outbox` 등 |
| Avoid | 코드 내 동의어 (예: `User` vs `Member`), spec의 deprecated 단어 |
| Code | FQN. 다수면 콤마로 |
| Found in | 모듈 디렉토리 + docs path |

추출 못한 필드는 명시적으로 `TBD` (생략 X).

## PHASE 6: Category Assembly (12 카테고리)

`glossary-extraction-rules.md §6` 순서대로 작성:

1. **Bounded Context Overview** — mission/CLAUDE.md 1문단 통합
2. **Aggregates & Entities** — Aggregate, Entity Term
3. **Value Objects** — VO Term
4. **Domain Services** — Domain Service Term
5. **Domain Events** — Domain Event Term + Kafka 토픽 매핑
6. **Policies & Invariants** — Policy Term + sealed/enum/Exception 표
7. **Ports** — Port (Inbound = Use Case Port, Outbound = Repository/External)
8. **Use Cases** — Use Case 클래스명에서 Verb+Noun 분리 사전
9. **API Contracts** (optional) — 외부 노출 API의 명사 (`*Request`, `*Response` 중 의미 있는 것)
10. **Acronyms & Abbreviations** — DART, FX, OHLCV, TOTP 등
11. **Cross-Context Integration** — context-map.md 참조 + 본 BC가 emit/consume 하는 이벤트
12. **Flagged Ambiguities** — 분류 불가, 추가 grilling 필요 사항

빈 섹션은 `— (이 BC에 해당 없음)` 표시.

## PHASE 7: Quality Gates (자동 검증)

생성 후 다음을 자동 점검 (`glossary-extraction-rules.md §7`):

- [ ] BC당 Aggregate ≥ 1 (없으면 보고서 경고)
- [ ] 모든 Domain Event는 emit trigger 명시
- [ ] 모든 Aggregate는 Invariants ≥ 1 (없으면 TBD 표기 후 Flagged)
- [ ] 모든 Term은 Type 필드 있음
- [ ] Avoid는 비어있어도 `—` 명시
- [ ] Code FQN이 실제 파일에 존재 (grep verify)
- [ ] Cross-Context Shared Term은 상대 BC에도 등재되었는지 매칭

검증 결과를 작성하여 사용자에게 보고.

## PHASE 8: Grilling & ADR Offer

자동 추출로 채워지지 않은 항목 (특히 Invariants, Avoid 후보) 에 대해 사용자에게 grilling.
- One question at a time
- 추천 답안 동반
- 답변 즉시 inline 갱신

ADR 트리거 (3 조건 모두 참 시 제안):
1. Hard to reverse
2. Surprising without context
3. Real trade-off

## Output Report (모든 모드 공통, 종료 직전)

```
Glossary updated: {path}

Mode:        Deep | Shallow | Conflict | Review | Bootstrap
Type counts: Aggregate {n}, Entity {n}, VO {n}, Service {n}, Event {n}, Policy {n}, Port {n}
Use Cases:   {n}
Acronyms:    {n}
Cross-context flags: {n}

Quality Gates:
  ✓ Aggregate ≥ 1
  ✓ All Events have emit trigger
  ⚠ {Aggregate X} missing Invariants (Flagged)
  ✓ FQN grep verified
  ⚠ Cross-context "Order" not matched in commerce BC

Next:
  - Resolve {n} Flagged Ambiguities (run again or grill)
  - Consider ADR for: {term-list if any}
```

---

## NEVER

- 8 소스 중 일부만 보고 Deep 모드라 보고
- Type 분류 없이 등재
- Exclude 패턴(`*JpaEntity`)을 도메인 용어로 등재
- Quality Gate 결과 누락
- Definition 없이 빈 항목 등재 (최소 추정 정의 + `(draft)` 마크 필수)
- 한 번에 여러 질문 grilling
- 검증 없이 (verified) 표시
