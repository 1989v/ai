# Glossary Extraction Rules

> `/hns:glossary --deep` (hns v0.9.0+)이 도메인 용어를 자동 추출할 때 적용하는 결정 기준.
> 이 문서가 *"왜 이 용어는 등재되고 저 용어는 누락되었는가"* 에 대한 단일 출처다.

---

## 0. Why explicit rules

이전 버전(`--scan`)은 entity/vo 디렉토리만 보고 클래스명을 등재했다. 한계:

- 어떤 기준으로 포함/제외했는지 불투명
- sealed class 하위 타입, enum 값, 도메인 예외에 숨은 invariant 누락
- 패키지명·Kafka topic·테스트 시나리오에서 비즈니스 어휘 추출 안 됨
- 기술 어댑터(`*Adapter`)와 도메인 추상(`*Port`)이 같은 무게로 다뤄짐

본 문서는 결정 규칙을 명문화하여 **재현 가능한 사전 생성**을 가능하게 한다.

---

## 1. Term Classification (도메인 용어 분류)

추출된 후보는 다음 7 종 중 정확히 하나로 분류:

| Type | 특징 | 예 |
|---|---|---|
| **Aggregate** | 트랜잭션 경계·invariant 보유 루트. 일반적으로 식별자(Id)와 child collection을 가짐 | `Order(OrderItem 보유)`, `Inventory`, `Strategy` |
| **Entity** | 동일성 식별이 있으나 Aggregate 내부 또는 다른 Aggregate 종속 | `OrderItem`, `TrancheSlot` |
| **Value Object** | 식별 없이 값 동치성 | `Money`, `ExpiryDate`, `BanditKey` |
| **Domain Service** | 여러 Aggregate에 걸친 도메인 로직 | `ScoreNormalizer`, `ConversationDomainService`, `KimchiPremiumCalculator` |
| **Domain Event** | 도메인이 외부에 알리는 사실 | `InventoryEvent`, `OrderEvents`, `ProductIndexEvent` |
| **Policy** | 의사결정 규칙. sealed class / enum / Exception에서 invariant 추출 | `ExpiryAlertPolicy`, `OrderStatus 전이 규칙`, `LeverageAttemptException` |
| **Port** | Domain → 외부 추상화 인터페이스 | `PaymentPort`, `OAuthClientPort`, `KillSwitchStatePort` |

분류 불가 후보는 **등재하지 않고** Flagged ambiguities로 넘긴다.

---

## 2. Inclusion Rules

후보를 사전에 등재하기 위한 충분 조건. **하나 이상** 만족하면 포함.

1. **도메인 모듈에 존재** (`{bc}/domain/src/main/kotlin/.../**`)
   - 단, `*JpaEntity`는 도메인 모듈에 있어도 제외 (3절 참조)
2. **sealed class 또는 그 하위 타입** (sealed hierarchy 전체가 도메인 어휘)
3. **public enum** 및 그 값들 (enum 값 자체가 정책 표현)
4. **도메인 예외명** (`*Exception`, `IllegalXyzException`) — exception을 통해 강제되는 invariant 추출
5. **Port 인터페이스** (`*Port`, `*RepositoryPort`) — 도메인이 외부에 요구하는 능력
6. **Use Case 이름의 동사+명사 페어** — 동사·명사 각각 별도 사전 항목 후보
7. **Kafka 토픽명에 등장하는 도메인 명사** (예: `order.order.completed` → `Order`, `Completed`)
8. **패키지명** (`bandit`, `share`, `promotion` 등) — 패키지가 곧 BC 내부 sub-context면 등재
9. **CLAUDE.md / mission.md / spec / ADR에 등장하는 비즈니스 명사** — 코드에 없어도 의미가 있으면 등재 (Flagged: code mapping TBD)

---

## 3. Exclusion Rules

다음은 도메인 어휘가 **아니므로** 제외. 등재 시 사전 품질 저하.

| 패턴 | 이유 |
|---|---|
| `*JpaEntity`, `*JpaRepository` | 영속화 기술 표현 (도메인 ↔ JPA 매핑 어댑터) |
| `*Adapter`, `*Config`, `*Configuration` | 인프라 어댑터 / Spring 설정 |
| `*Dto`, `*Request`, `*Response` | API 계약. 별도 *API Contract* 섹션에서 다룸 |
| `*Controller`, `*Service` (Spring), `*Application` | 응용 진입점·Spring stereotype. 동작은 Usecase로 추상화 |
| `*Mapper`, `*Converter` | 변환 유틸 |
| `*Properties`, `*Header`, `*Filter`, `*Resolver` | 횡단 관심사 |
| `In-memory*`, `Stub*`, `NoOp*` | 테스트/임시 구현체 |
| 단일 메서드 `*Calculator`, `*Helper`, `*Util` | 기술 유틸 (단, 도메인 의미가 명확하면 Domain Service로 재분류 가능, e.g. `KimchiPremiumCalculator`) |

**Exception**: 위 패턴이라도 *도메인 의미가 명확한 경우* 분류를 바꿔 등재한다 (예: `ScoreNormalizer`는 Service가 아니라 Domain Service로 등재).

---

## 4. Source Coverage (어디서 어휘를 추출하는가)

`--deep` 모드는 다음 8 소스를 모두 본다. `--scan`은 1번만 본다.

| # | Source | 추출 대상 |
|---|---|---|
| 1 | **`{bc}/domain/src/main/kotlin/**.kt`** | Aggregate / Entity / VO / Domain Service / Event / Port |
| 2 | **클래스 본문** (각 `.kt` 첫 100줄) | data class 속성, sealed subtypes, companion 상수, KDoc 주석 |
| 3 | **enum & sealed subtypes** | 정책 분기 (예: `OrderStatus.PENDING/CONFIRMED/CANCELLED`) |
| 4 | **`*Exception` 클래스** | 예외 메시지·생성자 인자에서 invariant 추출 |
| 5 | **`{bc}/app/.../usecase/*.kt`** | Use Case 이름의 동사+명사 분리 |
| 6 | **Kafka 토픽 상수** (코드 grep `topic`, `@KafkaListener`) | 이벤트 이름 + 페이로드 클래스 |
| 7 | **테스트 BehaviorSpec given/when/then** | 비즈니스 시나리오에서 도메인 표현 추출 |
| 8 | **문서**: `{bc}/CLAUDE.md`, `agent-os/product/mission.md`, `docs/architecture/*`, `docs/adr/*`, `docs/specs/*` 중 BC 관련 | 비즈니스 컨텍스트·정책 결정·전이 규칙 |

---

## 5. Per-Term Metadata Schema

각 용어는 다음 8 필드를 가진다. 추출 못한 필드는 명시적 TBD.

```markdown
### {Term}
**Type.** Aggregate | Entity | VO | Domain Service | Domain Event | Policy | Port
**Definition.** {1-2문장. 도메인 전문가가 이해 가능한 표현}
**Lifecycle.** {only for Aggregate/Entity/Event — created → ... → terminated}
**Invariants.** {Aggregate/Entity면 필수. Exception/sealed에서 추출된 규칙 N개}
**Related events.** {emits: [...], consumes: [...]} (해당 시)
**Avoid.** {기존에 쓰였거나 헷갈리는 동의어. 없으면 "—"}
**Code.** `{FQN}` (1개 또는 다수)
**Found in.** {domain, app/usecase, consumer, batch, docs/adr/* 등 출처 표시}
**References.** {ADR 번호, spec 경로, CLAUDE.md section}
```

---

## 6. Category Order (BC별 동일 구조 강제)

모든 BC glossary는 다음 카테고리 순서를 따른다. 빈 섹션은 `— (이 BC에 해당 없음)` 표시.

1. **Bounded Context Overview** — 1문단 (mission/CLAUDE.md 통합 요약)
2. **Aggregates & Entities** — 트랜잭션 경계 보유 객체
3. **Value Objects** — 식별 없는 도메인 값
4. **Domain Services** — Aggregate 간 또는 stateless 도메인 로직
5. **Domain Events** — emit 이벤트 (consume은 Cross-Context에서)
6. **Policies & Invariants** — sealed / enum / exception에서 추출된 규칙
7. **Ports** — Inbound (Use Case) / Outbound (Repository/External)
8. **Use Cases** — 동사+명사 페어 사전
9. **API Contracts** — Request/Response 명사 (선택, 외부 노출 시만)
10. **Acronyms & Abbreviations** — DART, FX, OHLCV 등
11. **Cross-Context Integration** — 다른 BC와 공유/충돌 용어
12. **Flagged Ambiguities** — grilling 필요 사항

---

## 7. Quality Gates (생성 후 자동 검증)

생성된 glossary는 다음을 만족해야 *완성*으로 간주.

- [ ] BC당 **최소 1개 Aggregate** 식별 (없으면 BC 정의가 잘못됐을 가능성 → Flagged)
- [ ] 모든 Domain Event는 emit 트리거 명시
- [ ] 모든 Aggregate는 Invariants 1개 이상 (없으면 TBD로 명시)
- [ ] 모든 Term은 Type 필드 채워짐
- [ ] Avoid 섹션이 비어있으면 "—" 명시 (생략 금지)
- [ ] Code FQN이 grep 가능 (실제 파일·클래스 존재 검증)
- [ ] Cross-Context Shared Term은 *양쪽 BC*에 등재되었는지 매칭 확인

자동 검증 실패 시 보고서에 표시.

---

## 8. NEVER

- `*JpaEntity` 도메인 용어로 등재
- 한 클래스를 두 Type으로 동시 분류
- Type 필드 누락
- Definition 없이 (draft) 등재 — 최소 1문장 추정 정의 필수
- 사용자 grilling 없이 Invariants를 완성으로 표시 (반드시 grilling 후 (verified) 마크)
- 동일 단어가 BC 간 다른 의미인데 Cross-Context Integration에 미등재
