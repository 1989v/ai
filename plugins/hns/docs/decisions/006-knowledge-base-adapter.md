# ADR-006: 외부 지식베이스 읽기 어댑터 (`hns:kb`)

**Date**: 2026-09-05 · **Status**: Accepted · **Version**: 0.15.0

## Context
사용자의 Obsidian LLM-wiki 볼트(`1989v`, 58페이지)에 msa 의 결정·함정·현황 페이지가 쌓여 있고, 쓰기 경로는 `obsidian-organize` 스킬(볼트 판정·스키마·로그·커밋)이 이미 담당한다. hns 는 볼트의 존재를 몰랐다. 레포 `docs/` 만 보면 "왜" 와 "지난번에 뭐가 깨졌나" 가 빠진다.

## Decision
1. **읽기만** — `hns:kb`(숨은 스킬) + `skills/kb/kb-search.sh`. `wiki/index.md` 를 키워드로 grep 해 상위 결과를 내고, 호출자는 **최대 3페이지**만 Read 한다. 볼트 전체·index 전체를 컨텍스트에 싣지 않는다(JIT).
2. **쓰기는 핸드오프** — `wrapup` 이 새로 확정·발견한 것을 `obsidian-organize` 에 넘긴다. hns 는 볼트에 쓰지 않는다. 볼트 판정(회사 → 개인 볼트 금지)은 그 스킬의 몫이다.
3. **프로젝트당 볼트 하나** — `HNS_KB_PATH`(환경변수 > `.claude/hns-hooks.env`). 개인 레포는 개인 볼트, 회사 레포는 회사 볼트. 홈은 `~` 로 적어 공개 레포에 사용자명이 남지 않게 한다.
4. **인용 규약** — `[[page]] (볼트명, updated YYYY-MM-DD)`. `(추정)`·기준 시점 표기를 옮긴다. 레포 문서와 모순되면 레포가 이기고 모순을 보고한다.
5. **참조 지점 5곳** — `start` PHASE 0/Query, `shape-spec` 브라운필드("위키가 답하는 것은 묻지 않는다"), `spec-review` Stage 3 표준, `evolve`(기존 개념이면 링크), `audit`(소스 `kb`). SessionStart 훅은 볼트 이름·페이지 수·마지막 ingest 한 줄만 알린다.

## Consequences
**+** 이전 세션이 볼트에 남긴 결정이 다음 세션의 shape·review 근거가 된다. 규칙 중복(레포 docs vs 볼트) 대신 링크.
**−** iCloud 경로라 evict 되면 조회가 빈다(스크립트가 `.icloud` 플레이스홀더를 감지해 stderr 로 알린다). 볼트 사실은 낡을 수 있어 `updated` 인용을 강제한다.

## Not adopted
임베딩 검색(58페이지에 grep 이 충분) · index.md 전체를 SessionStart 에 주입(매 세션 3~4K 토큰) · `validate --crosscheck` 의 레포↔living 페이지 모순 렌즈(후속).
