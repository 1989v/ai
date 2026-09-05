---
name: start
description: Use as the entry point for any work request in an hns-managed project — classifies the request as a codebase query or a feature, and runs the spec pipeline (shape → spec → review → tasks → implement → validate) for features.
when_to_use: 새 기능, 기능 추가, 피처 개발, feature 만들어, 서비스 구현, new feature, add feature, 코드 분석, 이거 어떻게 동작해, 구조 알려줘, explain this
argument-hint: "[request] [--feat] [--quick|--deep] [--no-interview] [--skip-to implement] [--no-validate] [--wrapup]"
---

# /hns:start

요청을 **질의**(탐색·설명)로 처리할지 **피처 파이프라인**으로 갈지 판단한다. 행동 규칙은 `hns:agent-behavior`.

```
/hns:start [요청]            # 분석 후 라우팅
--feat                        # 파이프라인 강제
--quick | --deep              # Shape 인터뷰 깊이 (기본 standard)
--no-interview                # 요청이 이미 구체적일 때 모호성 게이트 생략
--skip-to implement           # spec·tasks 가 이미 있을 때
--no-validate                 # 구현 후 검증 생략
--wrapup                      # 구현 후 회고 실행 (기본 꺼짐)
```

## PHASE 0: 컨텍스트
- 플랫폼이 CLAUDE.md·하위 CLAUDE.md·`.claude/rules/` 를 로드한다. 추가로 있으면 읽는다: `docs/product/mission.md`, `docs/product/glossary.md`(멀티 BC 면 `docs/context-map.md` → 해당 BC 사전).
- 사전이 없으면 "`/hns:glossary` 권장" 한 줄만 남기고 진행한다.
- `HNS_KB_PATH` 가 설정돼 있으면 `hns:kb` 로 요청의 도메인 명사를 조회한다(최대 3페이지, 읽기 전용). Query 모드 답변과 브라운필드 판단의 근거로 `[[page]] (볼트, updated)` 를 인용한다.

## 라우팅
| 분류 | 신호 | 경로 |
|---|---|---|
| Query | "어떻게 동작해?", "왜 이렇게?", 특정 파일·클래스, 디버깅 질문 | 탐색 → 증거(file:line) 기반 답변 |
| Feature | "만들어줘", "추가해줘", 명확한 신규 기능 | 파이프라인 |
| Ambiguous | "~하면 좋겠다", 개선 제안 | 관련 코드 탐색 → 판단 제시 → `AskUserQuestion` 으로 파이프라인 여부 확인 |

Query 도중 기능 개발이 필요해지면 파이프라인 전환을 제안한다.

## 피처 파이프라인

### 1. Shape — `hns:shape-spec`
스펙 폴더 생성 → 모호성 게이트 인터뷰(`references/ambiguity-gating-protocol.md`, 한 번에 한 질문) → `planning/requirements.md` · `planning/test-quality.md` · `context/open-questions.yml`. 요청에 파일 경로·클래스명·AC 가 이미 있으면 게이트를 건너뛴다.

### 2. Spec — `hns:write-spec`
`spec.md`. 새 미지수는 `open-questions.yml` 에 추가.

### 2.5 ADR 판단
새 서비스 모듈·새 외부 의존(DB·메시징·캐시)·서비스 간 통신 방식 변경·스키마 변경·인증 방식 변경 중 하나라도 있으면: `docs/adr/` 의 충돌 ADR 확인 → 사용자에게 "ADR 을 먼저 쓸까요?" → 승인 시 초안 작성 후 진행, 거절 시 기록만 남기고 진행.

### 3. Review — `hns:spec-review`
6개 차원을 `hns:spec-reviewer` 에이전트로 **병렬** 리뷰. BLOCK → 2단계로 복귀(최대 2회). REVISE → spec 수정 후 재리뷰(최대 2회). 전부 SHIP → 진행.

### 4. Tasks — `hns:create-tasks`
`tasks.md`.

### 5. 승인 게이트
```
Pipeline complete for: {feature}
- requirements.md ✓  - spec.md ✓ ({verdict})  - tasks.md ✓ ({N} groups)
- open-questions.yml ({M} open / {K} closed)  - ADR: {created|not-required|skipped}
구현을 시작할까요? [Y/n]
```
승인 시 실행 방식(`hns:implement-tasks` 참조)을 함께 정한다: 기본 Task-Group. task group 이 6개 이상이거나 step 간 간섭을 줄여야 하면 Step 모드, 독립 그룹이 여럿이면 병렬(워크트리 격리).

### 6. Implement — `hns:implement-tasks`

### 7. Validate (기본 ON, `--no-validate` 로 생략)
`hns:validate --code` → `hns:drift-check` → `hns:validate --docs`. 결과 표:
```
| Code Validation | Drift Check | Docs Sync |  → Overall: PASS | NEEDS_ATTENTION
```
NEEDS_ATTENTION 이면 수정 옵션을 제안한다. `--wrapup` 이면 `hns:wrapup`.
