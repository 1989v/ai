# Benchmark: 모델 상향(Claude 5 / Fable 5.1) + Claude Code 2.1.261 대비 hns 재점검 (2026-09-05)

**Sources**
- Claude Code 2.1.261 공식 문서 — hooks / skills / sub-agents / memory / plugins-reference / changelog (2026-09-05 fetch)
- Anthropic — *Effective harnesses for long-running agents*, *Effective context engineering for AI agents*
- OpenAI — *Harness engineering* (msa `docs/benchmarks/2026-04-08-openai-harness-engineering.md` 경유)
- ai-boost/awesome-harness-engineering 분류 체계
- **실사용 증거**: `~/.claude/projects/-Users-gideok-kwon-IdeaProjects-msa/*.jsonl` 99개 세션(보존 30일분), msa 레포 산출물, ai 레포 커밋 이력
- 플러그인 탐색 실측: 스크래치 플러그인 `probe` (아래 §3)

---

## 0. 결론 요약

| 판정 | 내용 |
|---|---|
| 훅 | **3단계 훅 템플릿은 실제 스키마가 아니다.** `type: reminder` · `PrePrompt` · `condition` · `pattern` · `onSuccess/onFailure` 는 Claude Code 에 존재하지 않는다. msa 에 복사된 `.claude/hooks/hnsf-automation.json` 도 어디에도 연결되지 않은 채 4월부터 무동작. Enforcement 기둥이 비어 있었다. |
| 스킬 탐색 | **숨은 스킬 22개가 한 번도 발견되지 않았다.** 플러그인 `skills/` 는 `skills/<name>/SKILL.md` 한 단계만 본다(실측). `core/` · `sdd/` · `review/` · `commands/` 아래 파일은 Skill 도구 목록에 오르지 않았고, `name:` 프론트매터도 호출명에 반영되지 않는다. |
| 실사용 | 99 세션에서 사용자가 `/hns:*` 를 직접 친 횟수 **0**. `hns:start` 가 CLAUDE.md 라우팅으로 14회 자동 진입한 것이 전부. hns 에이전트 10종은 subagent_type 으로 **0회** 디스패치. |
| 플랫폼 대체 | `.claude/rules/*.md` + `paths:` 가 index.yml 키워드 라우팅과 계층 위임을, `isolation: worktree` 가 parallel-work.sh 를, `/doctor` 트림 + `/skill-doctor` 가 diet Phase 1 을, auto memory 가 evolve 의 "가벼운 교정" 경로를 각각 대체한다. |
| 유지 가치 | 모호성 게이트 인터뷰, 6차원 스펙 리뷰, 사전(glossary), doctor.py, docs-health CI, 실패→규칙 진화 사이클은 모델과 무관한 **판단 구조**라 유지. 단 실행 형태를 플랫폼 기능 위로 옮긴다. |

---

## 1. 실사용 증거

### 1.1 Skill 도구 호출 (99 세션, tool_use 입력 기준)

| 스킬 | 호출 | 비고 |
|---|---|---|
| `obsidian-organize` | 20 | |
| **`hns:start`** | **14** | 전부 CLAUDE.md "Skill Routing Priority" 에 의한 자동 진입 |
| `game-cleanroom` | 6 | |
| `superpowers:brainstorming` | 4 | |
| `superpowers:systematic-debugging` | 3 | |
| 그 외 hns 24종 (`glossary`·`wrapup`·`gc`·`doctor`·`verify`·…) | **0** | |

사용자가 프롬프트에 `/hns:` 를 직접 타이핑한 세션: **0 / 99**.

### 1.2 Agent 도구 `subagent_type`

| 타입 | 횟수 |
|---|---|
| `general-purpose` | 87 |
| `Explore` | 11 |
| `hns:implementer` · `tester` · `verifier` · `spec-shaper` · `spec-writer` · `tasks-list-creator` · `spec-initializer` · `doc-gen-agent` · `gc-agent` · `harness-auditor` | **0** |

### 1.3 msa 레포에 남은 hns 산출물

| 산출물 | 상태 |
|---|---|
| `docs/specs/*/` (hns 폴더 구조) | 28개 디렉토리 중 `planning/` 16 · `context/` 6. **6월 이후 스펙은 전부 평면 `.md` 28개** — 파이프라인 구조를 더 쓰지 않는다 |
| `docs/retrospectives/` | 1건 (2026-05-22) |
| `harness-gc-report.md` · `docs/changelog/harness-changelog.md` · `docs/product/glossary.md` · `docs/index.yml` · `docs/architecture/overview.md` | 없음 — 여러 스킬이 빌드 명령을 읽으러 가는 `architecture/overview.md` 가 존재하지 않는다 |
| `.claude/hooks/hnsf-automation.json` | 가짜 스키마, settings 어디에서도 참조 안 됨 |
| 사용자가 손으로 만든 **진짜** 훅 | `adr-check.sh`(PreToolUse Write\|Edit) · `cdp-chrome-guard.sh`(PreToolUse Bash) · `submodule-auto-push.sh` · `game-mobile-check.sh`(PostToolUse) + http 관찰자 4종 + 전역 SessionStart/SessionEnd/Stop 훅 |

### 1.4 hns 개발 이력

| 월 | 커밋 |
|---|---|
| 2026-04 | 95 |
| 2026-05 | 5 |
| 2026-06 | 18 (16일 마지막) |
| 2026-07 ~ 09 | 0 |

그 사이 사용자의 실제 하네스 진화는 msa `CLAUDE.md` · `docs/standards/agent-behavior.md` · 전역 `~/.claude/CLAUDE.md` · auto memory(feedback 30여 건)에서 일어났다. `/hns:evolve` 를 거치지 않았다.

---

## 2. 훅 — 가짜 스키마 대 실제 스키마

| hns 템플릿이 쓴 것 | 실제 Claude Code 2.1.261 |
|---|---|
| 이벤트 `PrePrompt` | 없음. 실제 32종: `SessionStart` `UserPromptSubmit` `PreToolUse` `PostToolUse` `PostToolUseFailure` `Stop` `SubagentStop` `PreCompact` `PostCompact` `TaskCompleted` `InstructionsLoaded` `WorktreeCreate` … |
| `type: reminder` + `message` | 없음. 핸들러 5종: `command` `http` `mcp_tool` `prompt` `agent` |
| `condition: context.usage > 0.75` | 없음. 컨텍스트 사용률은 훅 입력에 없다 |
| `pattern: "**/spec.md"` | 없음. `matcher` 는 도구명 정규식, 경로 필터는 스크립트가 `tool_input.file_path` 로 판단하거나 `if: "Bash(git commit *)"` 권한 규칙 |
| `onSuccess: silent` / `onFailure: block` | 없음. 차단은 **exit 2** 또는 `hookSpecificOutput.permissionDecision: "deny"`, 피드백은 `additionalContext` |

즉 "성공은 조용히, 실패만 시끄럽게" 원칙은 맞았지만 구현체가 없었다. 실제로 그 원칙을 구현할 수 있는 수단:

| 목적 | 실제 수단 |
|---|---|
| 컴팩션 후 복구 | `SessionStart` matcher `compact\|resume` → `additionalContext` 로 progress/key-decisions 주입 (superpowers 가 같은 방식) |
| 컴팩션 전 상태 보존 | `PreCompact` → `additionalContext` 에 보존 지시. 진행 노트는 파일이 원본 |
| 컴파일 실패 시 커밋 차단 | `PreToolUse` matcher `Bash` + `if: Bash(git commit *)` → 컴파일 → 실패 시 `permissionDecision: deny` |
| 편집 후 린트 피드백 | `PostToolUse` matcher `Write\|Edit` → 린트 → `additionalContext` (PostToolUse 는 차단 불가) |
| "테스트 통과" 주장에 증거 요구 | `Stop` `type: prompt` → `last_assistant_message` 에 검증 출력이 없으면 `{"ok": false, "reason"}` 로 종료 차단 (`stop_hook_active` 로 루프 방지) |

---

## 3. 스킬 탐색 실측

스크래치 플러그인 `probe` 에 4개 스킬을 두고 `claude -p --plugin-dir` 로 목록을 물었다.

```
skills/flat-a/SKILL.md            (name: flat-a)        → probe:flat-a      노출
skills/group/nested-b/SKILL.md    (name: nested-b)      → (없음)            미노출
skills/dir-c/SKILL.md             (name: renamed-c)     → probe:dir-c       디렉토리명이 호출명
skills/hidden-d/SKILL.md          (user-invocable:false)→ probe:hidden-d    모델에는 노출
```

hns 의 `skills/core/*` `skills/sdd/*` `skills/review/*` `skills/commands/*` 는 전부 2단계 이하 → `hns:start` 가 "Load `hns:review-architecture` skill" 이라고 적어도 그런 스킬은 존재한 적이 없다. 파이프라인은 사실상 `start.md` 본문과 파일 Read 로만 굴러갔다.

---

## 4. 플랫폼 2.1.261 이 내장한 것 vs hns

| hns 기능 | 플랫폼 내장 | 판정 |
|---|---|---|
| Context Routing L2 (`docs/index.yml` 키워드 매칭, 자동 3개) | `.claude/rules/*.md` + `paths:` 글롭, 스킬 `paths:` 프론트매터, 하위 `CLAUDE.md` 는 그 디렉토리 파일을 읽을 때 자동 로드 | **대체**. index.yml 은 doctor 용 문서 색인으로만 남긴다 |
| Level 0.5 계층 위임 (`hierarchical-delegation.md`) | 위와 동일 (nested CLAUDE.md on-demand) | **대체** |
| `parallel-work.sh` + `worktree-protocol.md` | 에이전트 `isolation: worktree`, `EnterWorktree` 도구, `WorktreeCreate/Remove` 훅 | **대체** |
| diet Phase 1 (CLAUDE.md 60줄 압축) | `/doctor` 가 CLAUDE.md 트림 제안(v2.1.206+), 권장 상한 200줄 | **대체**. 기준 60→200 |
| diet Phase 2 (미사용 규칙) | `/skill-doctor` 가 미사용 스킬 + 컨텍스트 비용 표시(v2.1.260) | **보강**. 트랜스크립트 사용 횟수를 diet 의 1차 증거로 |
| evolve (실패→규칙) | auto memory `feedback` 타입이 교정을 자동 축적 | **분기**. 소프트 교정=memory, 경로 한정 규칙=rules, 기계적 강제=hook, 항상 참=CLAUDE.md |
| `commands/` 13 + 숨은 스킬 | 커맨드는 스킬로 통합, `commands/` 는 deprecated. `disable-model-invocation` / `user-invocable` / `when_to_use` / `context: fork` / `allowed-tools` / `effort` / `hooks` | **이관** |
| implementer(테스트 금지·Bash 금지) / tester 분리 | Fable 5.1 은 TDD 를 한 에이전트가 수행. Bash 금지는 Ralph Loop(BUILD→TEST) 와 모순 | **병합** |
| spec-shaper·doc-gen-agent (서브에이전트가 사용자에게 질문) | 서브에이전트는 사용자와 대화할 수 없다 | **설계 결함 → 메인 컨텍스트 스킬로** |
| 6 리뷰어 순차 실행 | Agent 도구 병렬 디스패치 + 읽기 전용 에이전트 | **병렬화** |
| Step 모드 상태머신 | Workflow 도구(사용자 옵트인 시) | 유지, Workflow 를 드라이버 선택지로 명시 |
| `config.yml` quality/efficient 모드 | 근거 없는 분기, 아무도 읽지 않음 | **제거** |
| 컴팩션 75%/90% 리마인더 | 1M 컨텍스트 + 자동 컴팩션, 루트 CLAUDE.md 는 컴팩션 후 재주입 | **제거**. 대신 PreCompact/SessionStart 훅 |
| 평가 | `claude plugin eval`(얼리액세스), `claude plugin validate`, 사용자 자체 `skill-quality-eval` | validate 를 배포 게이트로, eval 은 얼리액세스 해제 시 |

---

## 5. 2026 트렌드와의 대조

| 트렌드 | hns 현재 | 채택 |
|---|---|---|
| **Agent = Model + Harness**, 하네스 5층(도구 오케스트레이션·검증 루프·컨텍스트/메모리·가드레일·관측) | 검증 루프·컨텍스트는 있고 **가드레일(훅)이 비어 있음**, 관측 없음 | 훅 실장, `InstructionsLoaded` 로 로딩 관측 가능함을 문서화 |
| Anthropic 장기 실행 하네스 — initializer/coding 분리, `feature_list.json` 은 **`passes` 필드만 바꾼다**, 세션 시작 루틴(pwd·git log·progress·테스트 먼저), 브라우저 e2e, 세션 끝은 클린 상태 | first/continuation window 구분과 progress.md 는 있음. "상태 필드만 변경" 계약과 시작 루틴이 훅으로 강제되지 않음 | implement-tasks 에 시작 루틴 명시, tasks.md 체크박스는 검증 통과 후에만(기존) |
| 컨텍스트 엔지니어링 — 시스템 프롬프트 고도(altitude), JIT 검색, 구조화 노트, 서브에이전트 격리, **"똑똑한 모델일수록 덜 규정적으로"** | 규정적 체크리스트(400줄·600줄·8가지 상태) 다수 | 체크리스트 리마인더 제거, 판단 기준만 남김 |
| 평가를 게이트로 (Demystifying evals, plugin eval ablation) | 없음 | validate 게이트 + 사용 증거 기반 diet. eval 은 얼리액세스 해제 후 |
| 권한/샌드박스는 설정이, 행동은 CLAUDE.md 가 | 문서에 명시되지 않음 | evolve 분류표에 반영 |

---

## 6. 채택 (→ ADR-005)

- **A1 실제 훅 4종 + Stop 게이트** — `templates/hooks/` 를 실제 스키마로 교체. 3단계는 `HNS_HOOK_TIER=reminder|feedback|enforce` 로 같은 스크립트를 다르게 동작시킨다. 각 스크립트는 입력 주입으로 빨간불/초록불을 확인한 뒤에만 배포.
- **A2 스킬 평탄화** — `commands/` 13 + 숨은 22 → `skills/<name>/SKILL.md` 23개. 이름 = 디렉토리명. 부수효과 워크플로는 `disable-model-invocation: true`.
- **A3 에이전트 10 → 5** — `implementer`(tester 병합, Bash 허용) · `verifier` · `spec-reviewer`(신규, 읽기 전용, 6회 병렬) · `gc-agent` · `harness-auditor`. 사용자에게 질문해야 하는 shaper/doc-gen 은 메인 컨텍스트 스킬로.
- **A4 네이티브 대체** — index.yml 라우팅 · 계층 위임 · parallel-work.sh · config.yml 모드 · 컴팩션 리마인더 · COMPACTION-GUIDE 제거. init 은 컨벤션 번들을 `.claude/rules/` 경로 스코프 규칙으로 설치.
- **A5 diet/evolve 재정의** — diet 는 트랜스크립트 사용 횟수 + `/skill-doctor` + `/doctor` 트림을 증거로, CLAUDE.md 상한 200줄. evolve 는 교정의 성격에 따라 memory / rules / hook / CLAUDE.md 로 라우팅.
- **A6 톤** — Claude 5 기준으로 강조 표현·리마인더 체크리스트 제거.

## 미채택

| 항목 | 사유 |
|---|---|
| 플러그인 레벨 `hooks/hooks.json` 자동 활성 | hns 는 사용자 전역에서 켜져 있어 회사 레포에서도 발화한다. 프로젝트별 `setup-hooks` 설치로 한정 |
| `claude plugin eval` 케이스 동봉 | 얼리액세스 미해제(`plugin eval is currently in early access`). 해제 시 `hns:start` 라우팅 케이스부터 |
| Workflow 도구로 Step 모드 자동 전환 | 사용자 옵트인이 필요한 도구. 선택지로만 명시 |
| docs-health CI 의 `claude-code-base-action@v0.0.63` 핀 갱신 | 동작 중인 CI. 별도 작업으로 |
| glossary · validate-fe-design 본문 축소 | 모델 상향과 무관한 도메인 절차. 이번 범위 밖 |
