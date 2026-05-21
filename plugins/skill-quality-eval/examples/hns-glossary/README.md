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

7 개 용어:

| name | type | category | 근거 |
|---|---|---|---|
| Order | Aggregate | order-lifecycle | `order/Order.kt:12` |
| OrderId | VO | order-lifecycle | `order/OrderId.kt:8` |
| OrderItem | Entity | order-lifecycle | `order/OrderItem.kt:8` |
| OrderPlaced | Domain Event | order-lifecycle | `order/OrderPlaced.kt:9` |
| Product | Aggregate | product-catalog | `product/Product.kt:6` |
| Sku | VO | product-catalog | `product/Sku.kt:8` |
| InventoryService | Domain Service | inventory | `product/InventoryService.kt:7` |
| WarehousePort | Port | inventory | `product/InventoryService.kt:18` |

(8 entries — InventoryService 와 WarehousePort 는 같은 파일에 있지만 별개 타입이라 둘 다 추출)

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
