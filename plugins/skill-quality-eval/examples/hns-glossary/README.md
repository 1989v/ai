# Example: hns-glossary

skill-quality-eval v0.1 의 첫 dogfooding 대상 `hns:glossary` 평가용 reference goldset.

## 디렉토리

```
hns-glossary/
├── schema/
│   ├── output.schema.json        # 평가용 JSON 계약
│   └── matching-policy.json      # field-level 매칭 정책
├── fixtures/
│   └── toy-domain/               # 6 개 Kotlin 파일 (작은 commerce 도메인)
│       ├── order/{Order,OrderId,OrderItem,OrderPlaced}.kt
│       └── product/{Product,Sku,InventoryService}.kt
└── cases/
    └── case-001/input.yml        # /hns:glossary 호출 인자
```

## 예상 추출 결과 (baseline 컨펌 시 사용자가 확인할 정답 후보)

### `--shallow` 모드 (cases/case-001 디폴트) — 7 terms

shallow 는 **파일명 스캔만** 한다 (속도 우선). fixture 의 7 파일 각각에서 1 term:

| name | type | category | 근거 |
|---|---|---|---|
| Order | Aggregate | order-lifecycle | `order/Order.kt` |
| OrderItem | Entity | order-lifecycle | `order/OrderItem.kt` |
| OrderId | VO | order-lifecycle | `order/OrderId.kt` |
| OrderPlaced | Domain Event | order-lifecycle | `order/OrderPlaced.kt` |
| Product | Aggregate | product-catalog | `product/Product.kt` |
| Sku | VO | product-catalog | `product/Sku.kt` |
| InventoryService | Domain Service | inventory | `product/InventoryService.kt` |

### `--deep` 모드 (v0.2+ case 후보) — 8 terms

deep 는 파일 body 까지 스캔하여 같은 파일 안의 추가 타입까지 잡아낸다. 위 7 + 다음:

| name | type | category | 근거 |
|---|---|---|---|
| WarehousePort | Port | inventory | `product/InventoryService.kt:18` (인터페이스, 같은 파일 내) |

## 평가 정책 요점

- `terms[*].name` / `type` / `category` — **strict** (값 완전 일치)
- `terms[*].description` / `evidence` — **structural** (값 변동 허용, 형식만 검증)
- 배열 순서 무관 (`match-by: name`)
- `metadata.skill_version` 도 structural — 버전 bump 가 회귀로 잡히지 않게

## 사용법

평가 대상 프로젝트 루트에서:

```bash
# 1) 이 example 을 goldset 으로 복사
mkdir -p goldset/hns-glossary
cp -r ai/plugins/skill-quality-eval/examples/hns-glossary/* goldset/hns-glossary/

# 2) baseline 박기 (사람 컨펌 1회)
/skill-eval:baseline hns:glossary

# 3) hns:glossary 수정 후 회귀 측정
/skill-eval:run hns:glossary
```
