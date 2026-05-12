---
name: build
description: "Use when /portfolio:build is invoked or when user asks to generate/refresh their developer portfolio from git history. Extracts per-repo project summary, top contributions, and tech-stack frequency. Incrementally merges into existing portfolio.md using auto-section markers."
user-invocable: false
---

# portfolio:build — extraction & merge protocol

`/portfolio:build` 실행 시 따르는 표준 절차. 토큰 효율을 위해 **shell + git plumbing 위주**로 데이터를 수집한 뒤, 자연어 요약 단계에서만 LLM을 사용한다.

---

## 1. 입력 정규화

### 1.1 사용자 식별
```bash
EMAIL=$(git -C "$REPO" config user.email)
NAME=$(git -C "$REPO" config user.name)
```
- 두 값 모두 비어 있으면 사용자에게 `AskUserQuestion`으로 직접 입력 요청
- 출력 파일명용 slug: email의 `@` 앞 + 영숫자만 (예: `example.user`)

### 1.2 대상 repo 목록 결정
| 모드 | 처리 |
|---|---|
| (기본) | `[$(pwd)]` |
| `--repos a,b,c` | 콤마 분리 후 각 경로 검증 (`git rev-parse --git-dir`) |
| `--github <user>` | `gh repo list <user> --limit 1000 --json nameWithOwner,url,description` → 임시 디렉토리에 `git clone --filter=blob:none --depth=500` shallow clone |

### 1.3 출력 경로
- `--output` 지정 시 그대로
- 미지정 시 `~/.claude/portfolio/{slug}.md`
- 부모 디렉토리 없으면 `mkdir -p`

---

## 2. Incremental 메타 파싱

기존 출력 파일이 존재하면 다음 블록을 찾는다:

```html
<!-- portfolio-meta:
analyzed-at: 2026-05-12
language: ko
repos:
  - path: /Users/x/IdeaProjects/msa
    name: msa
    last-sha: 9138168abc...
  - path: /Users/x/IdeaProjects/ai
    name: ai
    last-sha: 7ee3eee123...
-->
```

- 파싱 실패 / 블록 없음 / `--full` → `last-sha` 모두 `null` 취급 (전체 분석)
- 각 repo의 `last-sha`가 있으면 `git log <sha>..HEAD --author=$EMAIL` 으로 신규 커밋만 수집
- 새 repo는 last-sha=null이므로 첫 분석에는 전체 history

---

## 3. 데이터 추출 (repo별)

### 3.1 본인 커밋 수집
```bash
git -C "$REPO" log "${RANGE}" --author="$EMAIL" \
  --pretty=format:'%H%x09%ai%x09%s' --numstat
```
- `RANGE`: incremental이면 `${last_sha}..HEAD`, full이면 빈 문자열
- 출력 파싱: 각 커밋 = (sha, iso-date, subject) + 이어지는 numstat 라인(added\tdeleted\tpath)

### 3.2 프로젝트 요약 데이터
| 필드 | 소스 |
|---|---|
| `name` | repo 디렉토리명 또는 `gh` description |
| `description` | README.md 첫 단락 (최대 200자) — `head -n 30` 후 첫 비어있지 않은 문단 |
| `period` | 본인 첫 커밋 ~ 마지막 커밋 ISO 날짜 |
| `total_commits` | 본인 커밋 수 (incremental은 기존 + 신규 합산) |
| `primary_lang` | 본인이 touch한 파일 확장자 최빈값 |

LLM은 위 raw 데이터를 받아 What/Why/Stack 2-3 문장 요약만 생성한다. (반복 가능한 형태 유지)

### 3.3 주요 기여 (top contributions)
필터링 + 랭킹:
1. subject가 `^(feat|refactor|perf|fix|breaking)(\(.+\))?:` 매치
2. LOC delta = added + deleted, 상위 N=15
3. merge commit (`^Merge `) 제외
4. revert / chore / docs / style / test prefix 제외

각 항목 출력 형태:
```
- {date} {repo}: {subject 정제판} (+{added}/-{deleted}, {sha-short})
```
LLM은 subject에서 prefix를 떼고 한 줄 자연어로 정제. 외부 컨벤션 정보가 충분하면 "왜 중요한지" 1줄 코멘트 추가.

### 3.4 기술 스택 (빈도 카운트)
**파일 확장자 카운트**:
```bash
# 본인 커밋이 touch한 파일에서만 카운트
git log --author=$EMAIL --name-only --pretty=format: \
  | sort -u | sed -n 's/.*\.//p' | sort | uniq -c | sort -rn
```

**확장자 → 언어 매핑**:
```
ts,tsx → TypeScript
js,jsx,mjs → JavaScript
kt,kts → Kotlin
java → Java
py → Python
rs → Rust
go → Go
swift → Swift
rb → Ruby
php → PHP
md → Markdown (집계는 하되 stack 표에는 제외)
yml,yaml,toml,json → Config (제외)
```

**의존성 매니페스트 발견 시 추가 데이터**:
| 파일 | 추출 키 |
|---|---|
| `package.json` | dependencies + devDependencies 핵심만 (react, vue, next, express, vitest 등 화이트리스트) |
| `build.gradle*` | Spring, Kotlin, JPA, Kafka 등 자주 쓰는 라이브러리 |
| `pyproject.toml` / `requirements.txt` | fastapi, django, pydantic 등 |
| `Cargo.toml` | tokio, axum, serde 등 |
| `go.mod` | gin, echo, gorm 등 |

화이트리스트 외 의존성은 무시 (스팸 방지). 핵심 라이브러리가 detect되면 frameworks 섹션에 추가.

---

## 4. Merge 알고리즘

기존 파일을 섹션 마커로 잘라낸 뒤 `auto:*` 영역만 교체. 사용자 수기 편집 영역(intro, custom 섹션 등)은 보존.

### 4.1 섹션 마커 구조
```markdown
# {이름} — Developer Portfolio

<!-- portfolio-meta:
... (자동)
-->

> 사용자가 자유롭게 편집 가능한 인트로 영역

<!-- BEGIN auto:projects -->
## 프로젝트
...
<!-- END auto:projects -->

<!-- BEGIN auto:contributions -->
## 주요 기여
...
<!-- END auto:contributions -->

<!-- BEGIN auto:stack -->
## 기술 스택
...
<!-- END auto:stack -->

> 사용자 자유 영역 (Awards, Talks 등)
```

### 4.2 섹션별 머지 규칙

#### projects
- 기존 항목과 repo name 키로 join
- 신규 repo → append
- 기존 repo에 신규 커밋만 있을 때:
  - `period.end` 갱신
  - `total_commits` 갱신
  - 1줄 요약은 보존 (사용자가 수기 보강했을 수 있음). 단 단순 자동 생성(2-3문장)이면 신규 커밋 패턴 반영해 재생성
- 항목 정렬: `period.end` 내림차순

#### contributions
- 마지막 분석 이후 신규 highlight만 append (시간순)
- 항목 상한: 최근 50건만 유지 (오래된 건 뒤로 밀려서 잘림)

#### stack
- 빈도 카운트는 **누적**: 기존 카운트 + 신규 커밋분 추가
- 표 재정렬 후 통째로 재생성
- 한 줄 포맷: `{언어/프레임워크} — {count}회 ({비중%})`

### 4.3 자동 메타 블록 갱신
머지 완료 후 portfolio-meta 블록을 다음으로 교체:
```html
<!-- portfolio-meta:
analyzed-at: {YYYY-MM-DD}
language: {ko|en}
repos:
  - path: {abs path}
    name: {repo name}
    last-sha: {HEAD sha at analysis time}
-->
```

---

## 5. 출력 템플릿 (한국어 기본)

```markdown
# {Name} — Developer Portfolio

<!-- portfolio-meta:
...
-->

> {간단 한 줄 자기소개 — 사용자 편집 가능}

<!-- BEGIN auto:projects -->
## 프로젝트

### {Repo Name}
- **기간**: 2024-03 ~ 2026-05 ({총 N개월})
- **What**: {LLM 생성 1-2문장}
- **Why**: {LLM 생성 1문장}
- **Stack**: Kotlin, Spring Boot, Kafka, PostgreSQL
- **본인 커밋**: 234건

### {다른 Repo}
...
<!-- END auto:projects -->

<!-- BEGIN auto:contributions -->
## 주요 기여

- 2026-04-12 · msa — 주문 도메인 이벤트 소싱 도입 (+1240/-380, `abc1234`)
- 2026-03-08 · ai — hns doctor 헬스체크 + docs-health CI 워크플로 추가 (+520/-12, `9e3530c`)
- ...
<!-- END auto:contributions -->

<!-- BEGIN auto:stack -->
## 기술 스택

| 영역 | 항목 | 빈도 |
|---|---|---|
| 언어 | Kotlin | 420회 (38%) |
| 언어 | TypeScript | 280회 (25%) |
| 프레임워크 | Spring Boot | 180회 |
| 인프라 | Kafka | 45회 |
<!-- END auto:stack -->

> Awards, Talks 등 자유 추가 가능
```

영어 모드는 동일 구조에서 헤더만 영문화 (Projects / Highlights / Tech Stack).

---

## 6. 실행 흐름 (요약)

1. **arg 파싱** → mode/repos/output/full/lang
2. **사전 검증** → git repo 여부, user.email 존재
3. **기존 portfolio 읽기** → meta block 파싱
4. **repo별 루프**:
   - git log range 결정
   - 본인 커밋 raw 수집
   - 프로젝트 요약 / 기여 후보 / 확장자 카운트 추출
5. **LLM 요약 단계**:
   - 프로젝트별 What/Why 자연어 생성 (신규/갱신 대상만)
   - 기여 highlight 한 줄 정제 (신규만)
6. **머지** → auto 섹션 재구성
7. **메타 블록 갱신 + 파일 저장**
8. **사용자에게 요약 보고** (repo별 신규 커밋 수, 갱신된 섹션, 출력 경로)

---

## 7. 성능 가드

- `--github` 모드는 repo 수가 많을 수 있으므로 **하나씩 순차 처리** + 중간 진행 보고
- shallow clone (`--depth=500`) 사용
- LLM 호출은 신규 데이터 발생한 repo에만
- 본인 커밋 1000건 초과 시 가장 오래된 항목은 raw 텍스트 단계에서 truncate (요약만 유지)

---

## 8. 자연어 트리거 대응

다음 표현이 들어오면 `/portfolio:build` 본 절차로 진입:
- "내 포트폴리오 만들어줘"
- "포트폴리오 업데이트", "포트폴리오 갱신"
- "이번 분기 내가 한 일 정리해줘"
- "커리어 정리", "이력서 자료"
- "build my portfolio", "refresh portfolio"

옵션 없이 들어오면 기본값(current repo + 글로벌 출력 경로)으로 실행하되, 첫 1회는 `--full` 효과로 동작 (메타 블록 없으므로 자연스럽게 전체 분석).
