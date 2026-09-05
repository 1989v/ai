# Agent Behavior Standards

## Core Rules

### Explore First, Evidence Based
- 코드나 문서를 먼저 읽고, 추론하지 말 것
- 가정 대신 증거 기반 접근
- 불확실하면 질문

### Pre-Work Checklist (모든 코드 수정 전)
1. Read `docs/specs/{feature}/context/key-decisions.md` (if exists)
2. Read `docs/specs/{feature}/spec.md`
3. Read `docs/specs/{feature}/tasks.md` → confirm current task
4. Check docs/standards/ and docs/conventions/ → matching standard
5. If unclear → ask "Please confirm: [specific question]"

## Risk Classification & Confirmation

### Risk Levels

| Level | Task Type | Action |
|-------|-----------|--------|
| **L1** | 리팩토링, 포맷, 주석, 문서 | Auto-proceed + build check |
| **L2** | 신규 파일, 메서드 시그니처, 테스트 추가 | Auto-proceed + Ralph Loop |
| **L3** | 비즈니스 로직, 도메인 개념, 아키텍처 변경 | **WAIT for human approval** |

### Ralph Loop (L2/L3)

```
MAX_RETRIES = 3
LOOP:
  1. BUILD   → fail → FIX
  2. TEST    → pass → EXIT (success)
  3. ANALYZE → identify root cause
  4. FIX     → different approach
  5. ITERATION++ → if >= 3 → EXIT (escalate)
```

Failure Classification:
- **Execution Failure** (Mock 누락, 파싱 오류) → 루프 내 수정
- **Implementation Failure** (404, 500, spec 불일치) → 즉시 STOP

### L3 Approval Request Format
```
## Work Confirmation Request
**Task**: [what]  **Reason**: [why]  **Impact**: [files/features]
**Evidence**: [docs/code referenced]
Proceed?
```

## Session Management

### Session Start
1. Read CLAUDE.md
2. Read docs/product/mission.md (if exists)
3. Check recent spec status in docs/specs/
4. Load active task context

### Session End
- Ensure all changes committed
- Update status.md if applicable
- Note next steps in tasks.md

### Post-Compaction Recovery
- SessionStart 훅 주입 내용부터 읽는다. 없으면 Compaction Rules 의 직접 읽기 순서
- 부족하면 구체적으로 질문

## Compaction Rules

컴팩션은 자동이다. 시점을 통제하지 말고 **파일을 원본**으로 유지한다.
- task group 완료·결정·블로커마다 `docs/specs/{feature}/context/progress.md` (현재 위치·완료·다음 단계·블로커) 와 `key-decisions.md` 갱신 + 커밋
- `PreCompact` 훅이 요약에 보존할 항목을 지시하고, `SessionStart` 훅이 컴팩션 후 progress·결정·열린 질문·최근 커밋을 다시 주입한다 (`/hns:setup-hooks`)
- 훅이 없으면 같은 것을 직접 읽는다: CLAUDE.md → key-decisions.md → open-questions.yml → tasks.md 체크박스 → `git log`

## Doc Gardening

### Doc Impact Scan (구현 성공 후)

```bash
git diff --name-only HEAD
```

변경된 파일 키워드 → docs/standards/·docs/conventions/ 매칭 → 관련 문서 보고

### 동기화 대상
- spec.md ↔ 실제 구현
- tasks.md ↔ 완료 상태
- key-decisions.md ↔ 코드 내 결정

### 원칙
- 구현이 성공한 후에만 문서 동기화
- 문서는 코드의 결과물, 코드가 source of truth

## Self-Review Protocol

### L1/L2: Automated Review
- 프로젝트 린터 실행 → 위반 시 수정

### L3: Fresh Context Review
- 서브에이전트로 fresh context reviewer 호출
- git diff + spec + standards만 제공
- 구현 히스토리 제외 (편향 방지)

### Verdict
- **SHIP** → BUILD 진행
- **REVISE** → 재구현 (max 2회)
- **BLOCK** → 에스컬레이션
