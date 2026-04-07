---
description: "Unified entry point: analyzes user request → codebase query OR feature pipeline. Trigger on: 새 기능, 기능 추가, 피처 개발, feature 만들어, 서비스 구현, new feature, add feature, 코드 분석, 이거 어떻게 동작해, 구조 알려줘, explain this"
---

# /hns:start

모든 작업 요청의 통합 진입점.
요청을 분석하여 **코드베이스 질의**(탐색/분석/설명)로 처리할지, **피처 파이프라인**(shape→write→review→tasks→implement→validate)으로 전환할지 자동 판단한다.

## Usage

```
/hns:start                       # 기본: 요청 분석 후 적절한 경로로 라우팅
/hns:start --feat                # 피처 파이프라인 강제 실행
/hns:start --no-validate         # 피처 파이프라인 실행 시 검증 단계 스킵
/hns:start --skip-to implement   # 이미 spec이 있을 때 구현부터 시작
```

## Required Inputs
- User request (feature description, question, or analysis request)

## Expected Outputs
- **Query mode**: 코드베이스 분석 결과, 구조 설명, 동작 원리 등
- **Feature mode**: docs/specs/{date}-{name}/ 아래 전체 산출물 + 구현 코드

---

## PHASE 0: Request Analysis & Routing

사용자 요청을 분석하여 라우팅 경로를 결정한다.

### Step 1: Intent Classification

요청을 다음 카테고리로 분류:

| Category | Signal | Route |
|----------|--------|-------|
| **Query** | "어떻게 동작해?", "구조 알려줘", "왜 이렇게?", 특정 파일/클래스 언급, 디버깅 질문 | → Query Mode |
| **Feature** | "만들어줘", "추가해줘", "구현해줘", 명확한 신규 기능 요구 | → Feature Pipeline |
| **Ambiguous** | "~하면 좋겠다", "~는 어때?", 개선 제안, 모호한 요청 | → Step 2 |

### Step 2: Ambiguity Resolution (Ambiguous일 때만)

1. Context Loading (PHASE 0 Context Loading 수행)
2. 코드베이스 탐색으로 관련 코드/문서 파악
3. 사용자에게 판단 결과 제시:

```
요청 분석 결과:

- 관련 코드: {files/modules}
- 현재 상태: {summary}
- 판단: 이 요청은 [신규 피처 개발 / 기존 코드 수정 / 분석·설명]에 해당합니다.

[신규 피처라면] 피처 파이프라인으로 진행할까요? [Y/n]
[분석·설명이라면] 바로 답변을 드리겠습니다.
```

### Routing Decision

- **Query Mode** → 바로 코드베이스 탐색 + 분석 + 답변
- **Feature Pipeline** → PHASE 1~7 진행
- **`--feat` 플래그** → 분석 없이 바로 Feature Pipeline 진행

---

## Query Mode

코드베이스 질의 처리 흐름:

1. **Context Loading**: docs/index.yml, 관련 문서 로딩
2. **Code Exploration**: Grep/Glob/Read로 관련 코드 탐색
3. **Architecture Context**: docs/architecture/, docs/adr/ 참조
4. **Answer**: 코드 구조, 동작 원리, 의존 관계 등을 증거 기반으로 설명

Query 중 피처 개발이 필요하다고 판단되면 사용자에게 피처 파이프라인 전환을 제안한다.

---

## Feature Pipeline

### Pipeline Overview

```
PHASE 0: Context Loading
PHASE 1: Shape Spec        ← /hns:shape-spec
PHASE 2: Write Spec         ← /hns:write-spec
PHASE 3: Spec Review        ← /hns:spec-review (5-dimension)
PHASE 4: Create Tasks       ← /hns:create-tasks
PHASE 5: User Approval Gate
PHASE 6: Implement Tasks    ← /hns:implement-tasks
PHASE 7: Post-Implementation Validation (기본 ON)
```

### PHASE 0: Context Loading

1. Read docs/index.yml (if exists) for auto-reference
2. Read agent-os/product/mission.md
3. Read agent-os/product/tech-stack.md

### PHASE 1: Shape Spec

Delegate to `/hns:shape-spec` flow:
1. spec-initializer → create spec folder
2. spec-shaper → requirements.md
3. Build test strategy → test-quality.md
4. Seed open-questions.yml

### PHASE 2: Write Spec

Delegate to `/hns:write-spec` flow:
1. Load open-questions context
2. spec-writer → spec.md

### PHASE 2.5: Open Questions Update

Update open-questions.yml with any new unknowns from spec writing.

### PHASE 2.8: ADR 필요성 판단

스펙 내용을 분석하여 아키텍처 변경이 포함되어 있는지 확인:

**ADR 트리거 조건** (하나라도 해당되면 ADR 필수):
- 새로운 서비스 모듈 추가
- 새로운 외부 의존성 (DB, 메시징, 캐시 등) 도입
- 기존 서비스 간 통신 방식 변경
- 데이터 모델 구조 변경 (스키마 마이그레이션 포함)
- 보안/인증 방식 변경

해당되면:
1. 기존 ADR 목록 조회 (`docs/adr/`)
2. 충돌하는 ADR이 있는지 확인
3. 사용자에게 알림: "이 스펙은 아키텍처 변경을 포함합니다. ADR을 먼저 작성할까요?"
4. 사용자 승인 시 ADR 초안 생성 → 승인 후 PHASE 3 진행
5. ADR 없이 진행 선택 시 경고 로그 기록 후 계속

### PHASE 3: Spec Review (5-Dimension)

Delegate to `/hns:spec-review` flow:
1. Run 5 reviewers sequentially
2. If BLOCK → return to PHASE 2 with feedback (max 2 iterations)
3. If REVISE → auto-revise spec.md (max 2 iterations)
4. If all SHIP → proceed

### PHASE 4: Create Tasks

Delegate to `/hns:create-tasks` flow:
1. tasks-list-creator → tasks.md

### PHASE 5: User Approval Gate

Present pipeline results summary:
```
Pipeline complete for: {feature-name}

Artifacts:
- requirements.md ✓
- spec.md ✓ (reviewed, {verdict})
- tasks.md ✓ ({N} task groups)
- open-questions.yml ({M} open, {K} closed)
- ADR: {created/not-required/skipped}

Proceed with implementation? [Y/n]
```

Wait for user approval before proceeding.

### PHASE 6: Implement Tasks

Delegate to `/hns:implement-tasks` flow.

### PHASE 7: Post-Implementation Validation

> `--no-validate` 옵션으로 이 단계를 스킵할 수 있음.

구현 완료 후 자동으로 3단계 검증을 수행:

#### Step 1: Code Validation (`hns:validate --code`)
- 아키텍처 원칙 준수 (domain에 Spring 의존성 없음 등)
- 패키지 네이밍 컨벤션
- 테스트 규칙 준수
- API 응답 포맷

#### Step 2: Drift Check (`hns:drift-check`)
- 구현 코드가 스펙(spec.md)과 일치하는지
- 스펙에 없는 기능이 추가되지 않았는지
- 스펙에 있는 기능이 누락되지 않았는지

#### Step 3: Docs Sync (`hns:validate --docs`)
- 새로 추가된 모듈/인프라가 CLAUDE.md에 반영되었는지
- docs/README.md 인덱스가 업데이트되었는지
- README.md(루트)에 새 서비스가 반영되었는지

#### Validation Report

```
## Post-Implementation Validation — {date}

| Step | Result | Details |
|------|--------|---------|
| Code Validation | PASS/WARN/FAIL | [summary] |
| Drift Check | PASS/WARN/FAIL | [summary] |
| Docs Sync | PASS/WARN/FAIL | [summary] |

Overall: PASS / NEEDS_ATTENTION
```

- **PASS**: 모든 검증 통과 → 완료 안내
- **NEEDS_ATTENTION**: WARN/FAIL 항목이 있으면 수정 옵션 제안

## Aliases

이 커맨드는 다음 자연어에도 반응:
- "새 기능 만들어줘", "기능 추가해줘"
- "피처 개발", "서비스 구현해줘"
- "new feature", "add feature"
- "이거 어떻게 동작해?", "구조 알려줘"
- "코드 분석해줘", "explain this code"

## Integration

- **Supersedes:** hns:feat, hns:new-feature (이 커맨드로 통합)
- **Delegates to:** shape-spec, write-spec, spec-review, create-tasks, implement-tasks, validate, drift-check
