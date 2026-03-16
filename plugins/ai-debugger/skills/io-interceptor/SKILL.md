---
name: io-interceptor
description: Use when setting up IO capture in a target service - injects unified AOP interceptor with profile-based activation and @IOTraceable annotation
---

# IO Interceptor Setup

## Overview

대상 서비스에 통합 AOP 기반 IO 인터셉터를 주입한다. 서비스의 코드 컨벤션을 준수하며,
`@Profile("debug-trace")`로 활성화하여 평상시 성능 영향 없음.

## 아키텍처: 통합 AOP

5개 개별 인터셉터 대신 **1개 AOP Aspect**로 모든 IO 캡처:

| 컴포넌트 | 역할 |
|---------|------|
| `TraceIdFilter` | X-Trace-Id → MDC 설정만 (경량) |
| `IOSnapshotAspect` | 모든 IO 캡처 + 적재 (통합 AOP) |
| `IOTraceLogAppender` | 애플리케이션 로그 캡처 (WARN 이상) |
| `RedisIOLogStore` | Redis 저장/조회 |
| `@IOTraceable` | 커스텀 어노테이션 (명시적 opt-in) |

## 타겟 식별 3단계

```
execution(* org.springframework.data.repository.Repository+.*(..))  ← 1. Spring Data (자동)
|| @within(IOTraceable)                                              ← 2. 어노테이션 (명시적)
|| execution(* *..*Adapter.*(..))                                    ← 3. *Adapter suffix (폴백)
```

대상 프로젝트에서 할 일:
- Spring Data Repository → **추가 작업 없음** (자동 캡처)
- WebClient 래퍼, Kafka Producer 등 → `@IOTraceable(IOType.EXTERNAL_API)` 부착
- *Adapter suffix 클래스 → **추가 작업 없음** (컨벤션 폴백)

## 활성화 전략

- **Spring**: `@Profile("debug-trace")` — 프로필 미활성 시 빈 자체 미등록, 오버헤드 0
- **비Spring**: 헤더 기반 `X-Debug-Trace: true` (향후)

## 주입 프로세스

### 1. 프로젝트 분석
- 언어/프레임워크 감지
- Redis 의존성 존재 여부 확인
- adapter/repository 패키지 구조 파악

### 2. 의존성 추가
- Redis 클라이언트 (없으면 추가)
- Spring AOP (없으면 추가)

### 3. 코드 주입
`templates/interceptors/kotlin-spring/` 의 템플릿을 대상 프로젝트에 주입:
- 패키지명을 프로젝트 컨벤션에 맞게 변경
- infrastructure/config/ 패키지에 배치
- application-debug-trace.yml 추가
- Spring Data가 아닌 IO 클래스에 `@IOTraceable` 부착 안내

### 4. 검증
- 컴파일 확인 (`./gradlew compileKotlin`)
- debug-trace 프로필 없이 기존 테스트 통과 확인

## 순서 보장

- sequence: 호출 진입 시 AtomicLong 채번 (AOP proceed 전)
- 데이터 쓰기: proceed() 반환 시점에 1회만 (blocking/suspend 모두 동일)

## Integration

- **Called by:** ai-debugger:debug-agent (미설치 감지 시)
- **Standalone:** `/io-setup`으로 직접 호출
