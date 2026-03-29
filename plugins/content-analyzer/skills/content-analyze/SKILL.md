---
name: content-analyze
description: Use when analyzing fetched content - extracts key concepts, identifies learning objectives, categorizes topics, and assesses difficulty level
---

# Content Analyze

## Overview

link-fetch 스킬이 수집한 콘텐츠를 분석하여 핵심 개념, 학습 목표, 주제 분류, 난이도를 도출한다. 이 분석 결과는 doc-generate 스킬의 입력이 된다.

## 분석 프로세스

### 1. 주제 분류

콘텐츠를 다음 카테고리로 분류:

| 카테고리 | 설명 | 예시 |
|----------|------|------|
| **Architecture** | 시스템/소프트웨어 설계 | MSA, DDD, Event-Driven |
| **Language/Framework** | 특정 언어/프레임워크 기술 | Kotlin Coroutines, Spring WebFlux |
| **DevOps/Infra** | 인프라, CI/CD, 클라우드 | K8s, Terraform, GitHub Actions |
| **AI/ML** | 인공지능, 머신러닝 | LLM, RAG, Fine-tuning |
| **Best Practice** | 개발 방법론, 패턴 | TDD, Clean Code, Code Review |
| **Career/Insight** | 커리어, 인사이트, 경험담 | 기술 리더십, 조직 문화 |
| **Other** | 위에 해당하지 않는 기타 | - |

복수 카테고리 가능 (주 카테고리 + 보조 카테고리).

### 2. 핵심 개념 추출

콘텐츠에서 다음을 추출:
- **핵심 키워드**: 콘텐츠의 주요 기술/개념 용어 (5~15개)
- **핵심 주장/인사이트**: 저자가 전달하려는 핵심 메시지 (3~7개)
- **실용적 테이크어웨이**: 실무에 바로 적용 가능한 포인트
- **코드 예제 요약**: 코드가 포함된 경우 각 코드 블록의 목적 정리

### 3. 난이도 평가

| 레벨 | 설명 |
|------|------|
| **Beginner** | 사전 지식 거의 불필요, 입문 수준 |
| **Intermediate** | 기본 지식 필요, 실무 적용 수준 |
| **Advanced** | 깊은 이해 필요, 전문가 수준 |

### 4. 선수 지식 도출

해당 콘텐츠를 이해하기 위해 필요한 선수 지식 목록:
- 필수 선수 지식 (이것 없이는 이해 불가)
- 권장 선수 지식 (있으면 이해가 깊어짐)

### 5. 관련 주제 연결

콘텐츠와 관련된 심화/확장 주제 도출:
- 이 콘텐츠를 배운 후 다음으로 학습할 주제
- 이 콘텐츠와 연관된 보완 주제

## 출력 포맷

```markdown
## 분석 결과

### 주제 분류
- **주 카테고리**: {category}
- **보조 카테고리**: {sub_categories}

### 난이도
- **레벨**: {Beginner | Intermediate | Advanced}
- **예상 학습 시간**: {estimated_hours}

### 핵심 키워드
{keyword_list}

### 핵심 인사이트
1. {insight_1}
2. {insight_2}
...

### 실용적 테이크어웨이
1. {takeaway_1}
2. {takeaway_2}
...

### 선수 지식
- **필수**: {required_prerequisites}
- **권장**: {recommended_prerequisites}

### 관련 심화 주제
- {related_topic_1}
- {related_topic_2}
```

## Integration

- **Called by:** content-analyzer:analyzer-agent
- **Standalone:** 직접 호출 불가 (link-fetch 결과 필요)
- **Calls:** 없음
