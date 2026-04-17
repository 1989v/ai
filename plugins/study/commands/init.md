---
description: "study/temp.md의 스터디 주제를 파싱하여 구조화된 학습 계획서를 생성한다. 스터디 초기화, 학습 계획 작성, 주제 정리 등의 자연어 요청에도 반응."
argument-hint: "[주제 번호]"
---

# Study — Init (학습 계획서 생성)

study/temp.md에 기록된 스터디 주제를 읽고, 구조화된 학습 계획서를 `study/docs/{N}-{slug}/plan.md`에 생성한다.

## 트리거

- `/study:init` — 학습 계획서가 아직 없는 주제 목록을 보여주고 선택
- `/study:init 1` — 1번 주제의 학습 계획서를 바로 생성
- `/study:init all` — 미생성 주제 전체 일괄 처리
- 자연어: "스터디 정리해줘", "학습 계획 만들어줘", "주제 초기화"

## 실행 단계

### 1. 현황 파악

1. `study/temp.md` 파일을 읽는다
2. `study/docs/` 하위의 **주제 폴더** 목록을 스캔 (Glob: `study/docs/*/plan.md`)
3. temp.md에서 아직 학습 계획서가 없는 주제를 식별

### 2. 사용자 프로필 로딩

메모리에서 사용자 정보 로드 → 난이도/깊이 조절에 활용.

### 3. 주제 선택

- **번호가 주어진 경우**: 해당 번호의 주제를 바로 처리
- **번호가 없는 경우**: 미생성 주제 목록을 표 형태로 출력

### 4. 학습 계획서 생성

**파일 경로**: `study/docs/{N}-{slug}/plan.md`

디렉토리가 없으면 먼저 생성 (`mkdir -p study/docs/{N}-{slug}`).

slug 규칙: 영문 kebab-case, 주제 핵심 키워드 (예: `1-aws-network`, `2-jvm-gc`).

**학습 계획서 템플릿**:

```markdown
---
id: {번호}
title: {한글 제목}
status: draft
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
tags: [태그1, 태그2, 태그3]
difficulty: {beginner | intermediate | advanced}
estimated-hours: {예상 학습 시간}
codebase-relevant: {true | false}
---

# {한글 제목}

## 1. 개요
## 2. 학습 목표
## 3. 선수 지식
## 4. 학습 로드맵
### Phase 1: 기본 개념
### Phase 2: 심화
### Phase 3: 실전 적용
### Phase 4: 면접 대비

## 5. 코드베이스 연관성
## 6. 참고 자료
## 7. 미결 사항
## 8. 원본 메모
```

**작성 원칙**:
- temp.md의 원본 내용을 `8. 원본 메모` 섹션에 그대로 보존
- 섹션 1~5는 원본 기반 구조화
- `difficulty`는 사용자 프로필 + 주제 내용 종합 판단
- `codebase-relevant`는 현재 msa 프로젝트 관련성 (Grep/Glob 빠른 체크)
- 과도한 추측 금지

### 5. temp.md 현황 표 업데이트

학습 계획서 생성 후 `study/temp.md`의 **학습 현황** 표에 행 추가/업데이트:

```markdown
| {N} | {한글 제목} | [{N}-{slug}/](docs/{N}-{slug}/) | draft |
```

### 6. 결과 보고

- 생성된 폴더 경로: `study/docs/{N}-{slug}/`
- 계획서 경로: `study/docs/{N}-{slug}/plan.md`
- 학습 목표 요약 (3줄 이내)
- 예상 난이도 + 학습 시간
- 다음 단계: `/study:bs {N}` 로 방향 브레인스토밍

### 7. 다수 주제 일괄 처리

`/study:init all` 호출 시 미생성 주제 전체 순차 생성.

## 파이프라인

```
init → bs → exec (프리뷰) → start (본격 심화)
```

- `init`: 계획서 초안
- `bs`: 계획서 다듬기
- `exec`: 주제 전체의 소주제 지도 + 가벼운 프리뷰
- `start`: 개별 소주제를 면접 꼬리질문 수준까지 심화

## 에러 처리

- `study/temp.md` 없음: 파일 생성 안내
- `study/docs/` 없음: 자동 생성
- 이미 `{N}-{slug}/plan.md` 존재: 덮어쓰기 여부 확인
- 존재하지 않는 번호: 사용 가능한 번호 목록 출력
