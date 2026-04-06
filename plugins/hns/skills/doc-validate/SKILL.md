---
name: doc-validate
description: "Validate CLAUDE.md and docs/ against actual codebase"
---

# /hns:doc-validate

## Purpose
CLAUDE.md와 docs/가 실제 코드 구조와 일치하는지 검증한다.

## Required Inputs
- CLAUDE.md and docs/ must exist

## Expected Outputs
- Validation report (PASS/WARN/FAIL per check)

---

## Overview

생성된 CLAUDE.md와 docs/ 트리가 실제 코드 구조와 일치하는지 검증한다.
검증 방향은 **docs → code** (docs가 source of truth).
docs에 명시된 내용이 코드에 실제로 존재하는지 확인하고, 불일치를 보고한다.

## Validation Direction

```
docs (source of truth)  →  code (reality check)
CLAUDE.md 모듈 목록      →  실제 디렉터리 존재 여부
아키텍처 패키지 경로     →  실제 패키지/디렉터리 경로
정책 문서 규칙           →  코드에서 규칙 준수 여부
```

## Checks

### 1. CLAUDE.md 규칙 vs 코드 구조

- 모듈 구조 섹션에 나열된 모듈이 실제로 존재하는지 확인
- 빌드 파일 경로가 올바른지 확인 (예: `build.gradle.kts` 위치)
- 테스트 디렉터리 경로가 실제와 일치하는지 확인

### 2. 모듈 존재 확인

settings.gradle.kts 또는 워크스페이스 설정에서 감지된 모듈:
- 각 모듈 디렉터리가 실제로 존재하는지 확인
- 각 모듈의 `src/main`, `src/test` (또는 동등한) 구조 확인
- docs에 나열된 모듈과 실제 모듈 목록 비교

### 3. 패키지 경로 확인

docs/architecture/overview.md에 명시된 패키지 구조:
- 실제 소스 파일에서 해당 패키지/디렉터리 존재 여부 확인
- 레이어 구조 (예: domain, application, infrastructure) 실재 확인
- 클래스/인터페이스 네이밍 패턴 샘플 검증

### 4. 정책 vs 코드 일관성

docs/policies/ 하위 문서에 명시된 규칙:
- 금지된 패턴 (예: "직접 DB 접근 금지")이 코드에 위반 사례가 없는지 확인
- 필수 패턴 (예: "모든 엔티티는 BaseEntity 상속")이 실제로 적용되는지 샘플 확인
- API 포맷 규칙이 컨트롤러 코드에서 준수되는지 확인

## Output Format

검증 결과를 다음 형식으로 출력:

```
## Validation Report

### CLAUDE.md
  ✓ 모듈 구조 섹션 - 모든 모듈 디렉터리 존재 확인
  ✓ 테스트 디렉터리 경로 일치
  ⚠ API 포맷 섹션 - 실제 컨트롤러에서 일부 불일치 발견

### docs/architecture/overview.md
  ✓ domain 레이어 패키지 존재
  ✓ application 레이어 패키지 존재
  ✗ infrastructure 패키지 경로 불일치: docs에는 'infra', 실제는 'infrastructure'

### docs/policies/
  ✓ user-service/docs/policies/order-policy.md - 코드와 일치
  ⚠ user-service/docs/policies/payment-policy.md - 검증 불가 (코드 샘플 부족)

---
총 검증 항목: 12
✓ 통과: 9  ⚠ 경고: 2  ✗ 오류: 1
```

### 심각도 레벨

- **✓ 통과**: docs와 코드가 일치
- **⚠ 경고**: 완전히 확인할 수 없거나 부분적 불일치 (코드 샘플 부족 등)
- **✗ 오류**: 명확한 불일치 (디렉터리 미존재, 경로 오류 등)

## 오류 발견 시 처리

오류(✗)가 발견되면:
1. 사용자에게 상세 보고
2. 수정 옵션 제안:
   - **docs 수정**: docs의 잘못된 경로/내용을 실제 코드에 맞게 수정
   - **코드 수정**: 코드 구조를 docs 명세에 맞게 변경 (구조적 결정인 경우)
   - **무시**: 의도적 불일치라면 docs에 주석으로 이유 기록

## 현재 버전 제약

- **v1은 수동 실행만 지원**: `/doc-validate` 명령으로 직접 호출
- 향후 Claude Code hooks를 통한 자동 트리거 예정 (파일 저장 시, 커밋 전 등)
- 정책 검증은 패턴 매칭 기반 샘플 확인 (100% 코드 커버리지 보장 아님)

## Integration

- **Called by:** hns:init, hns:harness-gc
- **Standalone:** `/hns:doc-validate`로 직접 호출 가능
- **Calls:** 없음 (검증 전용 스킬)
