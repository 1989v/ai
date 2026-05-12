---
description: "Build and evolve domain glossary with 8-phase deep analysis. Auto-classifies terms into 7 types (Aggregate/Entity/VO/Service/Event/Policy/Port), uses 8 sources (code body + JPA + enum/sealed + Kafka + tests + docs), and enforces Quality Gates. Trigger: 유비쿼터스 언어, 용어 사전, 도메인 사전, glossary, 용어 정리, 용어 충돌"
---

# /hns:glossary (v0.9.0+)

도메인 유비쿼터스 사전(`agent-os/product/glossary.md` 또는 BC별 `{bc}/glossary.md`)을 **8-phase 깊이 분석**으로 구축·갱신한다.

v0.8.x의 단순 파일명 스캔과 달리, v0.9.0+ 는 **8개 소스**(파일명 + 클래스 본문 + JPA + enum/sealed + Exception + Kafka topic + 테스트 BehaviorSpec + docs/ADR)를 종합 분석하고, 모든 용어를 **7개 Type**(Aggregate/Entity/VO/Domain Service/Domain Event/Policy/Port)로 분류한 뒤, **12개 카테고리**의 표준 구조로 출력한다.

## Usage

```
/hns:glossary                       # Deep 모드 (기본, v0.9.0+)
/hns:glossary --deep                # 명시적 Deep 모드
/hns:glossary --shallow             # Legacy 파일명 스캔만 (v0.8.x 동작, 속도 우선)
/hns:glossary --conflict {term}     # 특정 용어 충돌 해소
/hns:glossary --review              # 기존 사전 ↔ 코드 정합성 점검
/hns:glossary --bc {name}           # 특정 BC만 (멀티 BC 프로젝트)
```

## References (단일 출처)
- `@references/glossary-extraction-rules.md` — Include/Exclude, 7 Type 분류, 12 카테고리, Quality Gates
- `@references/language-reference.md` — 포맷 + Module Language

## Required Inputs
- (선택) BC 이름, 신규 용어 후보, 충돌 의심 용어

## Expected Outputs
- `agent-os/product/glossary.md` (단일 BC) 또는 `{bc}/glossary.md` (멀티 BC)
- `docs/context-map.md` (멀티 BC인데 없을 때 신규 생성)
- 필요 시 `docs/adr/{nnnn}-{term-decision}.md`
- 보고서: Type별 개수 + Quality Gate 결과 + Cross-context 매칭 + Next steps

---

## Procedure
실제 절차는 `skills/commands/glossary/SKILL.md`로 위임. 요약:

1. **PHASE 1 — Scope Resolution**: 단일/멀티 BC 결정, 출력 경로 확정
2. **PHASE 2 — Source Inventory**: 8 소스 존재 여부 확인
3. **PHASE 3 — Raw Candidate Extraction**: 8 소스 모두 스캔
4. **PHASE 4 — Classification**: 7 Type으로 분류, Exclude 적용
5. **PHASE 5 — Metadata Enrichment**: 8 필드 metadata (Type/Definition/Lifecycle/Invariants/Related Events/Avoid/Code/Found in)
6. **PHASE 6 — Category Assembly**: 12 카테고리 표준 구조로 작성
7. **PHASE 7 — Quality Gates**: 자동 검증 (Aggregate ≥ 1, Event emit trigger, Invariants, FQN grep 등)
8. **PHASE 8 — Grilling & ADR Offer**: TBD 해소 + ADR 제안

## v0.8.x → v0.9.0 마이그레이션

기존 v0.8.x 사전은 자유 형식 `## Terms` 섹션 단일 구조였다. v0.9.0 재생성:
```
/hns:glossary --deep --bc {name}
```
기존 파일을 덮어쓰기 전 `{bc}/glossary.v0.8.bak.md`로 백업.

## Aliases
- "용어 사전 만들어줘", "유비쿼터스 언어 정리"
- "사전 고도화", "사전 보강"
- "build glossary", "domain language"
