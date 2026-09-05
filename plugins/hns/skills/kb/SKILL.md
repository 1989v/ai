---
name: kb
description: Use when an hns step needs knowledge that lives outside the repo — decisions, pitfalls, and living status pages in the user's Obsidian LLM-wiki vault configured as HNS_KB_PATH. Read-only, just-in-time, at most three pages per lookup.
user-invocable: false
---

# kb — 외부 지식베이스 읽기

레포 `docs/` 는 코드의 진실이고, 볼트는 프로젝트를 가로지르는 개념·함정·이력 링크다. 볼트는 **읽기만** 한다. 쓰기는 `obsidian-organize` 스킬(볼트 판정·스키마·로그·커밋의 단일 원본)에 넘긴다.

## 설정
`HNS_KB_PATH` (환경변수 > `.claude/hns-hooks.env`). 값은 `wiki/index.md` 를 가진 볼트 루트. 없으면 이 스킬은 조용히 아무것도 하지 않는다. 볼트는 프로젝트 단위로 하나만 가리킨다(개인 레포 → 개인 볼트, 회사 레포 → 회사 볼트).

## 언제
| 단계 | 조회 키워드 | 쓰임 |
|---|---|---|
| `start` PHASE 0 · Query 모드 | 요청의 도메인 명사 2~3개 | 답변·라우팅 근거 |
| `shape-spec` 브라운필드 | 컴포넌트명·기존 시스템명 | 위키가 답하는 것은 묻지 않는다. 질문에 인용 |
| `spec-review` (architecture·implementation) | 스펙의 기술 결정 키워드 | 개념 페이지를 표준으로 취급 |
| `evolve` | 실패 패턴 키워드 | 이미 개념이 있으면 새 규칙 대신 링크 |
| `audit` | harness · prompt · 에이전트 | 내부 벤치마크 소스 |

## 어떻게
```bash
"${CLAUDE_PLUGIN_ROOT}/skills/kb/kb-search.sh" --status            # 볼트 이름 · 페이지 수 · 마지막 ingest
"${CLAUDE_PLUGIN_ROOT}/skills/kb/kb-search.sh" 검색 임베딩 하이브리드   # score  page  updated  summary
"${CLAUDE_PLUGIN_ROOT}/skills/kb/kb-search.sh" --page hybrid-search-local-embedding   # 파일 경로 + updated
```
1. 키워드로 검색해 상위 결과를 본다. **최대 3페이지**만 Read 한다. `index.md` 전체나 볼트 전체를 읽지 않는다.
2. 인용 형식: `[[page]] (볼트명, updated YYYY-MM-DD)`. 페이지의 `(추정)`·기준 시점 표기를 그대로 옮긴다. 레포 문서와 모순되면 레포가 이기고, 모순을 한 줄로 보고한다.
3. 결과가 없으면 없다고만 하고 진행한다.

## NEVER
- 볼트에 쓰기·수정·삭제 (→ `obsidian-organize`)
- 페이지를 통째로 컨텍스트에 붙이기 — 필요한 절만 인용
- `updated` 없이 인용 (낡은 사실이 사실처럼 굳는다)
- 회사 볼트 내용을 개인 레포 문서에 옮기기 (반대도)
