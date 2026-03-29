---
name: link-fetch
description: Use when fetching and extracting content from URLs - detects URL type (YouTube, LinkedIn, web post, Git repo) and retrieves structured content
---

# Link Fetch

## Overview

URL을 받아 타입을 판별하고, 해당 소스에서 콘텐츠를 추출한다. 다양한 URL 유형에 대해 최적의 방법으로 콘텐츠를 수집한다.

## URL 타입 판별

URL 패턴으로 타입을 자동 감지:

| 패턴 | 타입 |
|------|------|
| `youtube.com/watch`, `youtu.be/` | YouTube |
| `linkedin.com/posts/`, `linkedin.com/pulse/` | LinkedIn |
| `github.com/`, `gitlab.com/`, `bitbucket.org/` | Git Repository |
| 그 외 | Web Post (블로그, 기술 문서 등) |

## 타입별 수집 전략

### YouTube

1. WebFetch로 YouTube 페이지 접근
2. 영상 제목, 설명, 채널명 추출
3. 자막/트랜스크립트가 있으면 수집 (핵심 콘텐츠)
4. 자막 없으면 설명과 메타데이터 기반으로 분석

### LinkedIn Post

1. WebFetch로 LinkedIn 페이지 접근
2. 게시물 본문 텍스트 추출
3. 작성자 정보, 해시태그 추출
4. 첨부 링크나 이미지 설명 포함

### Git Repository

1. WebFetch로 README.md 페이지 접근
2. 프로젝트 설명, 주요 기능 추출
3. 디렉터리 구조 파악 (가능한 경우)
4. 주요 파일 (README, docs/, CONTRIBUTING.md 등) 수집
5. GitHub의 경우 topics, about 섹션도 수집

### Web Post (블로그, 기술 문서)

1. WebFetch로 페이지 접근
2. 본문 콘텐츠 추출 (메뉴, 광고 등 노이즈 제거)
3. 제목, 작성자, 작성일 추출
4. 코드 블록이 있으면 별도 보존
5. 이미지 alt 텍스트 포함

## 출력 포맷

```markdown
## 수집 결과

- **URL**: {original_url}
- **타입**: {YouTube | LinkedIn | Git | Web}
- **제목**: {title}
- **작성자/채널**: {author}
- **날짜**: {date}

### 콘텐츠

{extracted_content}

### 메타데이터

- 태그/토픽: {tags}
- 관련 링크: {related_links}
```

## 에러 처리

- 접근 불가 (403, 404): 사용자에게 알리고 대안 제안 (직접 콘텐츠 붙여넣기)
- 로그인 필요: 사용자에게 알리고 공개 접근 가능한 부분만 수집
- 콘텐츠 부족: 수집된 메타데이터라도 반환하고, 사용자에게 추가 컨텍스트 요청

## Integration

- **Called by:** content-analyzer:analyzer-agent
- **Standalone:** `/analyze` 커맨드의 첫 번째 단계로 호출
- **Calls:** 없음
