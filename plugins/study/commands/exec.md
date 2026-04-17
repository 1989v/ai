---
description: "ready 상태의 학습 계획서를 기반으로 주제 전체의 소주제 지도와 프리뷰(00-preview.md)를 생성한다. 스터디 프리뷰, 주제 개요, 소주제 목차 등의 자연어 요청에도 반응."
argument-hint: "[주제 번호]"
---

# Study — Exec (프리뷰 생성)

주제 **전체의 소주제 지도 + 가벼운 프리뷰**를 생성한다. 본격 심화는 `/study:start` 로 수행.

## 역할 재정의 (v0.2)

`exec` 는 "breadth" 담당. 주제 내 핵심 소주제(10-20개)의 **이름 + 1-2문단 개요 + 개념 관계도 + 치트시트**만 작성. 깊이는 없음.

**깊이는 `/study:start` 담당** — 소주제 단위로 개별 파일에 면접 꼬리질문 수준까지.

## 트리거

- `/study:exec` — ready 상태 계획서 목록 표시 후 선택
- `/study:exec 1` — 1번 주제 프리뷰 바로 생성
- 자연어: "스터디 프리뷰", "소주제 정리", "학습 개요"

## 산출물

- **파일**: `study/docs/{N}-{slug}/00-preview.md`
- **내용**:
  1. 학습자 프로필 (00-plan.md 에서 계승)
  2. 멘탈 모델 / 핵심 비유 (있으면)
  3. 소주제 목록 (10-20개) — 각 1-2문단 개요
  4. 개념 관계도 (ASCII diagram)
  5. 소주제 간 의존 관계
  6. Phase 1 치트시트 (용어 표, 빠른 판단 트리, 비교표)
  7. "본격 심화 가이드" — 어느 소주제부터 `/study:start` 로 파고들지 추천 순서

## 실행 단계

### 0. 준비

- `study/docs/{N}-{slug}/00-plan.md` 읽기
- frontmatter status 확인 (ready 또는 in-progress 여야 함)
- 존재하면 기존 `00-preview.md` 백업 후 재생성 또는 --resume 모드

### 1. 00-plan.md 분석

- Phase 1~4 의 소주제 목록 추출
- 학습자 수준/범위/깊이/면접 비중/출력 형태 파악

### 2. 00-preview.md 작성

**템플릿**:

```markdown
---
parent: {N}-{slug}
type: preview
created: {YYYY-MM-DD}
---

# {한글 제목} — Preview

> 학습자 수준: {level} · 전체 예상 시간: {h}h · 목표: {goal}

## 멘탈 모델

{1-2문단 비유 또는 핵심 관점}

## 소주제 지도

### Phase 1 기반 개념 (n개)

#### 1. {소주제 이름}
{1-2문단 개요} — 깊이 학습 필요 시 `/study:start {N} {slug}`

#### 2. ...

### Phase 2 심화 (m개)
...

### Phase 3 실전 적용
...

### Phase 4 면접 대비
...

## 개념 관계도

```text
[ASCII 다이어그램]
```

## 치트시트

### 용어 한 줄 정의
| 용어 | 정의 |

### 빠른 판단 트리
### 비교표 (주요 쌍)

## 다음 단계 — `/study:start` 추천 순서

1. `/study:start {N} {most-critical-subtopic}` — 가장 중요한 것 먼저
2. `/study:start {N} {second}` — 그다음
...
```

### 3. plan 상태 갱신

- `00-plan.md` frontmatter 의 status 를 `ready` → `in-progress` 로 변경 (아직 아니라면)
- `study/temp.md` 학습 현황 표에 "preview 완료" 반영

### 4. 결과 보고

- 생성된 00-preview.md 경로
- 식별된 소주제 N개
- 추천 심화 순서 상위 3개
- 다음 단계 안내: `/study:start {N} {subtopic}`

## 작성 원칙

- **Breadth 전용**: 한 소주제당 최대 1-2문단. 세부 메커니즘, 꼬리 질문, 장애 시나리오는 start 에 양보
- **관계도 필수**: 소주제 간 의존/상호작용이 면접에서 자주 물어봄
- **치트시트 포함**: Phase 1 수준의 빠른 복기용
- 코드 블록, 실습은 start 에 양보 (preview 에 가벼운 예시 1개 정도는 OK)

## 에러 처리

- `00-plan.md` 없음 or status 가 draft/refined: `/study:bs {N}` 로 ready 까지 다듬으라 안내
- 이미 `00-preview.md` 존재: 덮어쓰기 확인 (기존 파일은 `00-preview.md.bak` 으로 보존)

## 중단 및 재개

- 어느 소주제에서 중단 가능
- `--resume` 로 기존 00-preview.md 뒤에 이어쓰기
