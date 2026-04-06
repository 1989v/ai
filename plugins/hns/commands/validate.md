---
description: "Validate docs or code against harness rules — dual-mode: docs consistency + code compliance"
---

# /hns:validate

## Purpose
문서 일관성 검증(docs 모드)과 코드 규칙 준수 검증(code 모드)을 통합 제공한다.

## Usage

```
/hns:validate              # 기본: docs + code 모두 실행
/hns:validate --docs       # docs 모드만 실행
/hns:validate --code       # code 모드만 실행
```

## Required Inputs
- CLAUDE.md and docs/ must exist
- 프로젝트 소스 코드

## Expected Outputs
- Validation report (PASS/WARN/FAIL per check)

---

## Mode 1: Docs Validation (`--docs`)

문서가 실제 코드 구조와 일치하는지 검증한다.
검증 방향: **docs → code** (docs가 source of truth).

### Check 1: CLAUDE.md 규칙 vs 코드 구조

- 모듈 구조 섹션에 나열된 모듈이 실제로 존재하는지 확인
- 빌드 파일 경로가 올바른지 확인 (예: `build.gradle.kts` 위치)
- 테스트 디렉터리 경로가 실제와 일치하는지 확인
- 새로 추가된 인프라(docker/backup/ 등)가 문서에 반영되었는지 확인

### Check 2: 모듈 존재 확인

settings.gradle.kts 또는 워크스페이스 설정에서 감지된 모듈:
- 각 모듈 디렉터리가 실제로 존재하는지 확인
- 각 모듈의 `src/main`, `src/test` (또는 동등한) 구조 확인
- docs에 나열된 모듈과 실제 모듈 목록 비교

### Check 3: 패키지 경로 확인

docs/architecture/에 명시된 패키지 구조:
- 실제 소스 파일에서 해당 패키지/디렉터리 존재 여부 확인
- 레이어 구조 (예: domain, application, infrastructure) 실재 확인
- 클래스/인터페이스 네이밍 패턴 샘플 검증

### Check 4: 문서 상호 참조 일관성

- docs/README.md 인덱스에 나열된 문서가 실제로 존재하는지
- README.md(루트)에서 참조하는 문서 경로가 유효한지
- CLAUDE.md에서 참조하는 문서 경로가 유효한지

### Check 5: 정책 vs 코드 일관성

docs/policies/ 하위 문서에 명시된 규칙:
- 금지된 패턴이 코드에 위반 사례가 없는지 확인
- 필수 패턴이 실제로 적용되는지 샘플 확인
- API 포맷 규칙이 컨트롤러 코드에서 준수되는지 확인

---

## Mode 2: Code Validation (`--code`)

코드가 하네스 규칙(CLAUDE.md, docs/architecture/, agent-os/standards/)에 맞게 작성되었는지 검증한다.
검증 방향: **rules → code** (규칙이 source of truth).

### Check 1: 아키텍처 원칙 준수

CLAUDE.md와 docs/architecture/에 명시된 아키텍처 규칙:
- **의존성 방향**: domain 모듈이 Spring/JPA에 의존하지 않는지 확인
  - domain 모듈의 build.gradle.kts에 spring-boot, JPA 의존성 없음 검증
  - domain 소스에서 `@Entity`, `@Repository`, `@Service` 등 Spring 어노테이션 사용 없음 검증
- **서비스 간 DB 직접 접근 금지**: 다른 서비스의 DB 설정이나 Entity를 import하지 않는지
- **레이어 구조**: 각 서비스가 domain/application/infrastructure/presentation 구조를 따르는지

### Check 2: 패키지 네이밍 컨벤션

CLAUDE.md에 명시된 `com.kgd.{service}` 패턴:
- 각 서비스의 base package가 `com.kgd.{service}`로 시작하는지
- domain/application/infrastructure/presentation 하위 구조가 컨벤션과 일치하는지
- model/, policy/, event/, exception/ 등 세부 패키지가 적절한 레이어에 위치하는지

### Check 3: 테스트 규칙 준수

CLAUDE.md에 명시된 테스트 규칙:
- 테스트 프레임워크: Kotest BehaviorSpec 사용 여부 (Mockito 사용 금지 확인)
- 테스트 더블: MockK 사용 여부
- Domain 테스트: Mock 미사용 순수 단위 테스트인지
- Application 테스트: Outbound Port만 MockK으로 Mock하는지
- 파일 이름: 구현체 + `Test` suffix 규칙

### Check 4: Kafka 토픽 컨벤션

CLAUDE.md에 명시된 `{domain}.{entity}.{event}` 형식:
- Producer에서 발행하는 토픽명이 컨벤션과 일치하는지
- Consumer Group ID가 `{service}-{purpose}` 형식인지

### Check 5: API 응답 포맷

모든 Controller가 `ApiResponse<T>`를 반환하는지:
- RestController의 반환 타입 샘플 확인
- 에러 응답도 ApiResponse 포맷을 따르는지

### Check 6: 빌드/모듈 규칙

- common 모듈: bootJar 없이 jar만 생성하는지
- 서비스 모듈: common에 implementation 의존하는지
- 버전 관리: gradle/libs.versions.toml에서 중앙 관리되는지
- Java toolchain: JavaLanguageVersion.of(25) 통일

---

## Output Format

```
## Validation Report — {date}

### Docs Validation
  ✓ CLAUDE.md 모듈 구조 — 모든 모듈 디렉터리 존재
  ✓ 문서 상호 참조 — 모든 링크 유효
  ⚠ platform-overview.md — 신규 인프라 미반영

### Code Validation
  ✓ 아키텍처 원칙 — domain 모듈 Spring 의존성 없음
  ✓ 패키지 네이밍 — com.kgd.{service} 패턴 준수
  ✗ 테스트 규칙 — order:domain에 MockK 사용 발견 (Mock 금지 위반)
  ✓ Kafka 토픽 — 컨벤션 일치
  ✓ API 응답 포맷 — ApiResponse<T> 준수

---
총 검증 항목: 11
✓ 통과: 9  ⚠ 경고: 1  ✗ 오류: 1
```

## 심각도 레벨

- **✓ 통과**: 규칙과 실제가 일치
- **⚠ 경고**: 부분적 불일치 또는 검증 불가 (샘플 부족)
- **✗ 오류**: 명확한 규칙 위반

## 오류 발견 시 처리

오류(✗)가 발견되면:
1. 사용자에게 상세 보고 (파일 경로, 라인 번호, 위반 내용)
2. 수정 옵션 제안:
   - **코드 수정**: 규칙에 맞게 코드 변경
   - **규칙 수정**: 의도적 예외라면 docs/CLAUDE.md에 예외 명시
   - **무시**: 일회성 예외로 기록

## 현재 버전 제약

- v1은 수동 실행만 지원
- 정책/코드 검증은 패턴 매칭 기반 샘플 확인 (100% 코드 커버리지 보장 아님)
- 향후 Claude Code hooks를 통한 자동 트리거 예정

## Integration

- **Called by:** hns:init (Phase 3), hns:harness-gc
- **Standalone:** `/hns:validate`, `/hns:validate --docs`, `/hns:validate --code`
- **Calls:** 없음 (검증 전용)
- **Supersedes:** hns:doc-validate (이 커맨드로 통합)
