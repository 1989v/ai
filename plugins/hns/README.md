# hns (Harness) v0.14

Claude Code 2.1 위에서 도는 하네스 엔지니어링 플러그인. 세 기둥 — **Context**(CLAUDE.md·rules·스킬), **Enforcement**(실제 훅·검증 게이트·리뷰), **Evolution**(evolve·diet·gc·audit) — 을 플랫폼 기능 위에 얇게 얹는다.

## 진입점

```
/hns:start [요청]        # 질의면 답하고, 기능이면 파이프라인: shape → spec → review(병렬 6차원) → tasks → implement → validate
```

| 스킬 | 언제 |
|---|---|
| `/hns:start` | 모든 작업의 시작 |
| `/hns:verify` | 구현 후 표준→린트→빌드→테스트, 증거 기록 |
| `/hns:validate [--docs\|--code\|--crosscheck]` | 문서↔코드, 규칙↔코드, 문서·스펙·태스크·코드 교차 |
| `/hns:doctor` | 5 레이어 헬스체크 점수 (`scripts/doctor.py`) |
| `/hns:glossary` | 도메인 사전 (8 소스 · 7 타입 · 품질 게이트) |
| `/hns:wrapup` | 회고 → 반복 실패를 evolve 로 |
| `/hns:evolve` · `/hns:diet` · `/hns:gc` · `/hns:audit` | 규칙 추가 · 사용 증거 기반 감량 · 청소 · 외부 벤치마크 |
| `/hns:init` · `/hns:setup-hooks` · `/hns:doc-gen` · `/hns:health-mode` · `/hns:validate-fe-design` | 초기화 · 훅 설치 · 문서 생성 · CI 모드 · FE 디자인 린트 |

파이프라인 단계(`shape-spec` `write-spec` `spec-review` `create-tasks` `implement-tasks` `drift-check`)와 행동 규칙(`agent-behavior` `spec-evolution`), 외부 지식베이스 읽기(`kb`)는 모델만 호출하는 숨은 스킬이다.

**지식베이스**: `HNS_KB_PATH` 에 Obsidian LLM-wiki 볼트를 가리키면 `start`·`shape-spec`·`spec-review`·`evolve`·`audit` 가 필요할 때만 최대 3페이지를 읽어 `[[page]] (볼트, updated)` 로 인용한다. 읽기 전용이며 쓰기는 `obsidian-organize` 에 넘긴다.

## 훅 (실제 스키마)

`/hns:setup-hooks` 가 프로젝트에 설치한다. 수준은 `HNS_HOOK_TIER`.

| 이벤트 | 동작 | tier |
|---|---|---|
| `SessionStart` | 최신 progress.md · 결정 · 열린 pre-impl · 최근 커밋 주입 | 전부 |
| `PreCompact` | 요약이 보존할 항목 지시 | 전부 |
| `PreToolUse` `git commit` | 컴파일 실패 → feedback 알림 / enforce 차단 | feedback+ |
| `PostToolUse` Write\|Edit | 바뀐 파일 린트 → 알림 | feedback+ |
| `Stop` (prompt) | 근거 없는 "완료·통과" 주장 → 종료 차단 | enforce |

성공은 조용히, 실패만 시끄럽게. 설치 시 실패 입력을 주입해 빨간불을 확인한다(`templates/hooks/README.md`).

## 구조

```
skills/<name>/SKILL.md      23개, 한 단계 (플러그인 skills/ 는 한 단계만 탐색한다)
  spec-review/reviewers/    6 차원 체크리스트 + skillsets
  glossary/procedure.md     8-phase 절차
agents/                     implementer · verifier · spec-reviewer · gc-agent · harness-auditor
references/                 hooks-reference · ambiguity-gating · review-protocol · step-execution · diet-criteria · language-reference · glossary-extraction-rules · fe-design-validation · gc-protocol · prompting-tone · harness-philosophy · command-execution-contract
templates/                  hooks/ (스크립트+settings 스니펫) · claude-md/ · docs-tree/ · conventions/ (→ .claude/rules) · specs/ · steps/ · ci/docs-health.yml
scripts/                    doctor.py · doc_map.py · doc_scan.py
docs/                       philosophy · decisions(ADR) · benchmarks · changelog · specs(역사)
```

플랫폼이 하는 것은 하지 않는다: 컨텍스트 라우팅(CLAUDE.md·`.claude/rules/` `paths:`·스킬), 워크트리(`isolation: worktree`), 컴팩션, auto memory, `/skill-doctor`·`/doctor` 트림.

## 설치

```bash
claude plugin install hns@ai-common          # 또는 claude --plugin-dir /path/to/ai/plugins/hns
/hns:init                                     # 새 프로젝트
/hns:setup-hooks enforce                      # 훅
```
검증: `claude plugin validate plugins/hns --strict`.

## 문서
- 철학 `docs/philosophy/` · 결정 `docs/decisions/` (ADR-005: 모델 상향 다이어트) · 벤치마크 `docs/benchmarks/` · 변경 `docs/changelog/harness-changelog.md`
