---
description: "git commit history 기반 개발자 포트폴리오를 생성·보완한다. 기본은 현재 repo + ~/.claude/portfolio/{user}.md. 자연어 트리거: 내 포트폴리오 만들어줘, portfolio 갱신, 커리어 정리."
argument-hint: "[--repos p1,p2] [--github user] [--output path] [--full] [--lang ko|en]"
---

# /portfolio:build

git commit history를 분석해 사용자의 개발 포트폴리오를 markdown으로 생성한다. 기존 포트폴리오가 있으면 **마지막 분석 이후 신규 커밋만** incremental로 반영한다.

상세 추출/머지 알고리즘은 `skills/build/SKILL.md`에서 로드한다.

## 트리거

- `/portfolio:build` — 현재 repo + 기본 출력 경로
- `/portfolio:build --full` — 전체 재분석
- `/portfolio:build --repos /path/a,/path/b` — 여러 로컬 repo 합산
- `/portfolio:build --github gideok-kwon` — GitHub 전체 스캔 (gh CLI 필요)
- `/portfolio:build --output ./portfolio.md` — 출력 경로 override
- 자연어: "내 포트폴리오 만들어줘", "포트폴리오 갱신", "커리어 정리", "지금까지 한 일 정리해줘"

## 옵션

| Flag | Default | 설명 |
|---|---|---|
| `--repos <p1,p2,...>` | (current cwd) | 콤마 구분 로컬 repo 경로 합산 |
| `--github <user>` | off | gh CLI로 사용자의 모든 repo 스캔 (시간 소요) |
| `--output <path>` | `~/.claude/portfolio/{git-user}.md` | 출력 파일 경로 |
| `--full` | off | 마커 무시하고 전체 재분석 |
| `--lang ko\|en` | ko | 출력 언어 |

## 동작 개요

1. **사용자 식별**: `git config user.email` → 본인 커밋만 필터
2. **모드 결정**: `--github` > `--repos` > current cwd
3. **출력 경로 결정**: `--output` > `~/.claude/portfolio/{user}.md`
4. **Incremental 판정**: 출력 파일에서 `<!-- portfolio-meta: ... -->` 블록 파싱
   - 없거나 `--full`이면 전체 재분석
   - 있으면 repo별 `last-sha` 이후 커밋만 수집
5. **데이터 추출**: 프로젝트 요약 / 주요 기여 / 기술 스택
6. **섹션 머지**: `<!-- BEGIN auto:* -->` 마커 사이만 갱신, 사용자 수기 편집 영역 보존
7. **메타 갱신**: 분석 시점 + repo별 최신 SHA 기록

## 외부 도구 요구

- 필수: `git`
- 선택: `gh` (GitHub-wide 스캔 시), `jq` (의존성 매니페스트 파싱 시)

## 사전 검증

실행 직전 다음을 확인:
- 대상 repo가 git 저장소인지 (`git rev-parse --git-dir`)
- `git config user.email` 값 존재 여부 (없으면 사용자에게 묻는다)
- 출력 디렉토리 존재 여부 (없으면 `mkdir -p`)

## 출력 요약 보고

분석 종료 후 다음을 표로 보고:

```
Portfolio updated: {output-path}

| Repo | New commits | Sections updated |
|---|---|---|
| msa | 23 | projects, contributions, stack |
| ai | 5 | contributions |

Mode: incremental | Languages tracked: Kotlin, TS, Python | Last analyzed: 2026-05-12
```

## 에러 처리

| 상황 | 처리 |
|---|---|
| current dir이 git repo 아님 | `--repos` 또는 `--github` 사용 안내 |
| git user.email 미설정 | 사용자에게 입력 받음 |
| 본인 커밋 0건 | "No commits found for {email}. Check --author or pass --repos" 안내 |
| `gh` 미설치 + `--github` 지정 | 설치 안내 후 중단 |
