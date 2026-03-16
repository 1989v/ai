---
name: data-analyze
description: Use when code analysis alone cannot explain an issue - analyzes IO log data patterns to find anomalies in request flows, response times, error patterns
---

# IO Data Analyzer

## Overview

수집된 IO 데이터에서 패턴을 분석하여 코드만으로 설명되지 않는 이슈의 원인을 찾는다.

## 분석 패턴

### 1. 에러 패턴
- 특정 IO 구간에서 반복적 에러 발생
- 에러 메시지 내용 분석

### 2. 지연 패턴
- invokedAt ~ completedAt 간격으로 병목 구간 식별
- sequence 순서와 시간 간격으로 비동기 대기 구간 파악

### 3. 데이터 불일치
- 요청 파라미터와 응답 데이터 간 불일치
- DB 쿼리 결과와 API 응답 간 변환 오류

### 4. 호출 패턴 이상
- 예상보다 많은 DB 호출 (N+1 문제)
- 불필요한 외부 API 중복 호출
- 누락된 캐시 히트 (Redis GET이 항상 miss)

## Integration

- **Called by:** ai-debugger:debug-agent (code-explore 후 추가 분석 필요 시)
- **Requires:** log-query로 데이터 먼저 조회
