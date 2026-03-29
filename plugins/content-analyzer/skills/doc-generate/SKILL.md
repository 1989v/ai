---
name: doc-generate
description: Use when generating the final learning plan or analysis document from analyzed content - produces structured markdown documents for study purposes
---

# Document Generate

## Overview

content-analyze 스킬의 분석 결과를 바탕으로 학습 플래닝 문서 또는 내용 정리/분석 문서를 생성한다. 사용자가 선택한 포맷에 따라 출력물이 달라진다.

## 문서 포맷

### Format 1: 학습 플래닝 문서 (plan)

콘텐츠를 학습하기 위한 체계적인 계획서를 생성한다.

```markdown
# {제목} - 학습 플래닝

## 개요
- **원본**: [{title}]({url})
- **작성자**: {author}
- **분류**: {category}
- **난이도**: {level}
- **예상 학습 시간**: {estimated_hours}

## 학습 목표
이 콘텐츠를 학습한 후 달성할 수 있는 구체적 목표:
1. {objective_1}
2. {objective_2}
...

## 선수 학습
### 필수 (먼저 학습 필요)
- [ ] {prerequisite_1} — {brief_description}
- [ ] {prerequisite_2} — {brief_description}

### 권장 (학습 효과 향상)
- [ ] {recommended_1} — {brief_description}

## 학습 단계

### Phase 1: 기초 이해 ({estimated_time})
- [ ] 핵심 개념 파악: {concepts}
- [ ] 용어 정리: {terms}
- **학습 방법**: {method}
- **확인 질문**: {check_questions}

### Phase 2: 심화 학습 ({estimated_time})
- [ ] {deep_topic_1}
- [ ] {deep_topic_2}
- **실습 과제**: {practice}
- **확인 질문**: {check_questions}

### Phase 3: 적용 & 실습 ({estimated_time})
- [ ] {application_1}
- [ ] {application_2}
- **실습 프로젝트**: {project_idea}

## 핵심 정리
### 키워드
{keyword_table}

### 인사이트
{insights}

## 심화 학습 로드맵
이 콘텐츠 이후 추천 학습 경로:
1. {next_topic_1} — {reason}
2. {next_topic_2} — {reason}

## 참고 자료
- {reference_1}
- {reference_2}
```

### Format 2: 내용 정리/분석 문서 (summary)

콘텐츠의 핵심을 구조화하여 레퍼런스 문서로 정리한다.

```markdown
# {제목} - 내용 분석

## 메타 정보
| 항목 | 내용 |
|------|------|
| 원본 | [{title}]({url}) |
| 작성자 | {author} |
| 분류 | {category} |
| 난이도 | {level} |
| 분석일 | {date} |

## TL;DR
{3줄 이내 핵심 요약}

## 핵심 내용

### 1. {topic_1}
{structured_content}

### 2. {topic_2}
{structured_content}

...

## 주요 인사이트
1. **{insight_title_1}**: {description}
2. **{insight_title_2}**: {description}

## 실무 적용 포인트
- {practical_point_1}
- {practical_point_2}

## 코드 레퍼런스
(코드가 포함된 콘텐츠인 경우)

### {code_example_title}
```{language}
{code}
```
**목적**: {purpose}
**핵심 포인트**: {key_point}

## 비판적 분석
- **강점**: {strengths}
- **한계/주의점**: {limitations}
- **대안적 관점**: {alternative_views}

## 관련 주제
- {related_1}
- {related_2}
```

## 포맷 자동 선택

사용자가 포맷을 지정하지 않은 경우 콘텐츠 유형에 따라 자동 선택:

| 콘텐츠 유형 | 기본 포맷 | 이유 |
|-------------|-----------|------|
| 기술 튜토리얼, 강의 | plan | 단계적 학습이 효과적 |
| 경험담, 인사이트 | summary | 핵심 정리가 더 유용 |
| Git 프로젝트 | summary | 구조/설계 분석이 핵심 |
| 기술 블로그 (심화) | plan | 학습 계획이 필요 |
| 기술 블로그 (팁/트릭) | summary | 빠른 레퍼런스가 목적 |

사용자에게 추천 포맷을 제안하되, 최종 선택은 사용자에게 맡긴다.

## 파일 저장

생성된 문서는 현재 작업 디렉터리에 저장:

```
{cwd}/
└── content-analysis/
    └── {YYYY-MM-DD}-{sanitized-title}.md
```

- 디렉터리가 없으면 생성
- 파일명은 날짜 + 제목을 kebab-case로 변환
- 동일 파일명 존재 시 사용자에게 덮어쓰기 여부 확인

## Integration

- **Called by:** content-analyzer:analyzer-agent
- **Standalone:** 직접 호출 불가 (content-analyze 결과 필요)
- **Calls:** 없음 (최종 생성 스킬)
