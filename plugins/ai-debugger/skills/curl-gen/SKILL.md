---
name: curl-gen
description: Use when generating curl commands from natural language or API specs - parses user intent, finds matching API endpoints, collects parameters, and builds executable curl
---

# curl Command Generator

## Overview

사용자의 자연어 설명을 파싱하여 대상 API의 curl 명령을 생성한다.

## 프로세스

### 1. API 식별
사용자 설명에서 대상 API를 식별:
- 코드베이스의 Controller/Router 탐색
- OpenAPI spec 파일 존재 시 참조
- docs/에 API 문서가 있으면 참조

### 2. 파라미터 수집
- Path variable, Query parameter, Request body 식별
- 필수/선택 구분
- 사용자에게 누락된 필수 파라미터 질문

### 3. 인증 처리
- 환경변수에서 토큰 조회 (예: `$API_TOKEN`, `$AUTH_HEADER`)
- 없으면 사용자에게 입력 요청
- 로그에는 마스킹 처리 (`Authorization: Bearer ***`)

### 4. curl 생성 + 실행
```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "X-Trace-Id: debug-$(date +%s)" \
  -d '{"productId": 1, "quantity": 2}'
```

- X-Trace-Id 헤더 자동 추가 (IO 인터셉터 연동)
- 사용자 확인 후 실행
- 응답 출력

## Integration

- **Called by:** ai-debugger:debug-agent
- **Standalone:** `/curl-gen`으로 직접 호출
