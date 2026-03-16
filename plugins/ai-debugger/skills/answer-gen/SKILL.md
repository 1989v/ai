---
name: answer-gen
description: Use when generating a comprehensive debug answer for the user - synthesizes code analysis, IO log evidence, and docs references into actionable response
---

# Debug Answer Generator

## Overview

분석 결과를 종합하여 사용자에게 구조화된 답변을 생성한다.

## 답변 구조

```
## 원인 분석

{이슈의 근본 원인 설명}

## 관련 코드

- `{파일경로}:{라인}` — {해당 코드의 역할과 문제점}

## IO 로그 근거 (조회한 경우)

- `{IO키}` — {데이터가 보여주는 증거}

## 문서 참조

- `docs/policies/{파일}` — {관련 비즈니스 규칙}

## 해결 방안

1. {구체적 수정 방안}
2. {대안이 있으면 제시}

## 재발 방지

- {근본적 해결을 위한 제안}
```

## 원칙

- 추측이 아닌 코드/데이터 근거 기반
- 코드 위치를 정확히 명시 (파일:라인)
- 해결 방안은 구체적이고 실행 가능하게
- 불확실한 부분은 명시적으로 "확인 필요" 표시

## Integration

- **Called by:** ai-debugger:debug-agent (최종 단계)
