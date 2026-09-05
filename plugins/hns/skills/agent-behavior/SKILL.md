---
name: agent-behavior
description: Use when starting any coding task in an hns-managed project — risk classification, build/test loop, self-review, session recovery, and compaction rules that every hns skill assumes.
user-invocable: false
---

# Agent Behavior

## 0. 원칙
- 증거 먼저: 추론 전에 코드·문서를 읽는다. 충돌 시 CLAUDE.md > memory > 추정.
- "고쳤다" 는 값이 달라진 것으로 판정한다. "테스트 통과" 는 실행 명령과 결과 줄이 있을 때만 말한다.
- 사용자에게 확인이 필요한 것은 한 번에 하나씩 묻는다.

## 1. 작업 전 (스펙이 있는 경우)
`docs/specs/{feature}/context/key-decisions.md` → `spec.md` → `tasks.md`(현재 그룹) → `context/open-questions.yml`(`pre-impl` + `open` 이면 구현 금지).

## 2. 리스크 분류
| Level | 종류 | 행동 |
|---|---|---|
| L1 | 리팩토링·포맷·주석·문서 | 진행 + 빌드 확인 |
| L2 | 신규 파일·시그니처·테스트 추가 | 진행 + 검증 루프 |
| L3 | 비즈니스 로직·도메인 개념·아키텍처·스키마 | **사용자 승인 후** 진행 |

L3 승인 요청 형식: `Task / Reason / Impact(files) / Evidence(docs·code) / Proceed?`

## 3. 검증 루프 (L2·L3)
`BUILD → TEST → ANALYZE(원인) → FIX(다른 접근)` 최대 3회. 3회 실패 → 중단하고 시도한 것과 다음 가설을 보고.
- 실행 실패(mock·파싱·환경) → 루프 안에서 수정
- 구현 실패(404·500·스펙 불일치) → 즉시 중단, 스펙/결정 확인

## 4. 구현 후 리뷰
- L1·L2: 프로젝트 린터.
- L3: `git diff` + spec + standards 만 주고 **fresh-context 서브에이전트**에 리뷰시킨다(구현 히스토리 제외). 판정 SHIP / REVISE(최대 2회) / BLOCK.
- 변경 파일 키워드로 `docs/standards/` `docs/conventions/` 를 훑어 갱신할 문서를 보고한다.

## 5. 세션과 컨텍스트
- 로딩은 플랫폼이 한다: 루트 `CLAUDE.md` 는 항상, 하위 디렉토리 `CLAUDE.md` 와 `.claude/rules/*.md`(`paths:`) 는 그 경로의 파일을 읽을 때, 스킬은 호출될 때. hns 가 따로 라우팅하지 않는다.
- 세션 시작·컴팩션 후에는 `SessionStart` 훅(`/hns:setup-hooks`)이 최신 `progress.md` · key-decisions · 열린 pre-impl 수 · 최근 커밋을 주입한다. 훅이 없으면 같은 것을 직접 읽는다.
- 레포 밖 지식베이스가 설정돼 있으면(`HNS_KB_PATH`) `hns:kb` 규칙대로 필요할 때만 최대 3페이지를 읽고 `updated` 와 함께 인용한다. 쓰기는 `obsidian-organize` 로.
- 이어가기 전에 이전 작업의 빌드/테스트를 한 번 돌린다. 완료된 그룹을 다시 구현하지 않는다.
- 컴팩션은 자동이다. 시점을 통제하려 하지 말고 **파일을 원본**으로 유지한다: task group 완료·결정·블로커가 생길 때마다 `context/progress.md`(현재 위치·완료·다음 단계·블로커)와 `key-decisions.md` 를 갱신하고 커밋한다. `PreCompact` 훅이 요약에 보존할 항목을 지시한다.

## 6. 결정 기록
```md
### [YYYY-MM-DD] 제목
- Decision / Reason / Evidence(docs·code) / Impact(files)
```
→ `docs/specs/{feature}/context/key-decisions.md`

## 7. 서브에이전트
- 메인에서: 왕복이 잦은 작업, 앞 단계 컨텍스트를 공유해야 하는 작업, 파일 하나 읽고 고치기, grep 한 번이면 되는 것.
- 서브에이전트: 출력이 큰 탐색·테스트·로그(`Explore`), 도구를 제한해야 하는 작업(리뷰어·검증자), 독립 결과를 요약만 받으면 되는 것, 병렬 가능한 것.
- fork: 대화 맥락 전체가 필요한 곁가지.
- 격리가 필요하면 Agent 호출에 `isolation: worktree` 를 쓴다. 스크립트로 워크트리를 만들지 않는다.

## 8. 외부 스킬
hns 파이프라인이 활성일 때 브레인스토밍·플랜·구현·검증은 hns 단계가 맡는다. 겹치는 외부 스킬(superpowers 등)은 사용자가 요청할 때만. 디버깅·코드리뷰 같은 보조 스킬은 자유.

## NEVER
- key-decisions.md 를 읽지 않고 코딩 시작
- 같은 접근을 반복하는 검증 루프
- 통과시키려고 테스트 약화·삭제
- 승인 없는 L3 변경
- 3회 실패 후 계속 시도
- 도구 한 번이면 되는 일에 서브에이전트
