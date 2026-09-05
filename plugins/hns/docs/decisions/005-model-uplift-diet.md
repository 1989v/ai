# ADR-005: 모델 상향·플랫폼 2.1 대비 다이어트와 실제 훅 (v0.14.0)

**Date**: 2026-09-05 · **Status**: Accepted · **Source**: `docs/benchmarks/2026-09-05-model-uplift-platform-2-1.md`

## Context
Claude 5(Fable 5.1) 와 Claude Code 2.1.261 환경에서 hns 를 재점검했다. 세션 기록 99건에서 사용자가 `/hns:*` 를 직접 친 횟수 0, 에이전트 디스패치 0, `hns:start` 자동 진입 14회. 훅 템플릿 3종은 존재하지 않는 스키마(`type: reminder` `PrePrompt` `condition`)라 4월부터 무동작. 플러그인 `skills/` 는 한 단계만 탐색하므로 `core/` `sdd/` `review/` `commands/` 아래 숨은 스킬 22개는 한 번도 발견된 적이 없다(스크래치 플러그인으로 실측). 플랫폼은 그 사이 `.claude/rules/` 경로 스코프, 에이전트 `isolation: worktree`·`memory`, 스킬 프론트매터(`disable-model-invocation` `when_to_use` `context: fork`), `/skill-doctor`, `/doctor` 트림, auto memory 를 내장했다.

## Decision
1. **훅을 실제 스키마로 교체** — `templates/hooks/`: `session-start-recover.sh`(SessionStart) · `precompact-preserve.sh`(PreCompact) · `commit-gate.sh`(PreToolUse `git commit`, 컴파일) · `edit-lint.sh`(PostToolUse) + Stop `prompt` 훅(완료 주장 증거 게이트). 3단계는 `HNS_HOOK_TIER` 로 같은 스크립트를 다르게. 플러그인 레벨 자동 활성은 하지 않는다(전역 활성 플러그인이라 다른 레포에서도 발화).
2. **스킬 평탄화** — `commands/` 13 + 숨은 22 → `skills/<name>/SKILL.md` 23. 이름 = 디렉토리명. 부수효과 워크플로(init·setup-hooks·gc·doc-gen·audit·health-mode·evolve·diet)는 `disable-model-invocation: true`, 파이프라인 단계·행동 규칙은 `user-invocable: false`. 리뷰어 6종은 `spec-review/reviewers/` 보조 파일로.
3. **에이전트 10 → 5** — `implementer`(tester 병합, Bash 허용) · `verifier` · `spec-reviewer`(신규, 읽기 전용, 6회 병렬) · `gc-agent` · `harness-auditor`. 사용자에게 질문하는 shaper·doc-gen 은 메인 컨텍스트 스킬로(서브에이전트는 질문할 수 없다).
4. **플랫폼 중복 제거** — `docs/index.yml` 키워드 라우팅(색인은 doctor 용으로만 유지) · 계층 위임 문서 · `parallel-work.sh`/worktree 프로토콜 · `config.yml` quality/efficient 모드 · 컴팩션 75/90% 리마인더 · COMPACTION-GUIDE · doc-html · interview-capture(모호성 게이트와 중복) · orchestrate-tasks/verify-crosscheck(implement-tasks/validate 로 흡수).
5. **diet·evolve 재정의** — diet 는 세션 기록 호출 수·`/skill-doctor`·`/doctor` 를 증거로, CLAUDE.md 상한 200줄. evolve 는 교정 성격에 따라 memory / rules / hook / CLAUDE.md / skill 로 라우팅.
6. **init 은 컨벤션을 `.claude/rules/` 로** — 번들 파일에 `paths:` 를 붙여 그 경로를 읽을 때만 로드.

## Verification (2026-09-05)
- 스크립트 단위: 실패 입력 주입 → `permissionDecision: deny` / `additionalContext`, 정상 입력 → 출력 없음 exit 0. 5/5 통과.
- 런타임(`claude -p`, haiku): SessionStart 주입 내용을 모델이 그대로 인용 · `git commit` 이 deny 되고 HEAD 불변, 컴파일 통과 시 HEAD 이동 · 근거 없는 "테스트 통과" 주장은 Stop 게이트가 차단해 모델이 검증을 시도, 실패 보고·인사말은 통과.
- 탐색: `claude plugin validate --strict` 통과, 격리 로드 시 스킬 목록에 숨은 스킬 포함 노출(§ 결과는 changelog 참조).

## Consequences
**+** Enforcement 기둥이 처음으로 실제로 동작한다. 숨은 스킬이 발견된다. 파일 수와 규칙 수가 줄어 컨텍스트 비용이 준다. 리뷰 6회가 병렬이다.
**−** `/hns:orchestrate-tasks` `/hns:interview-capture` `/hns:verify-crosscheck` `/hns:doc-html` 는 사라졌다(각각 implement-tasks · shape-spec · validate --crosscheck · 없음). 기존 프로젝트의 `.claude/hooks/hnsf-*.json` 은 무동작 파일이므로 삭제 대상이다(msa: `.claude/hooks/hnsf-automation.json`).
**−** Stop 게이트는 매 턴 빠른 모델 호출 1회를 쓴다. enforce 수준에서만 켠다.

## Not adopted
플러그인 레벨 hooks.json · `claude plugin eval` 케이스(얼리액세스 미해제) · Workflow 도구 자동 전환 · docs-health CI 액션 핀 갱신 · glossary/validate-fe-design 본문 축소.
