# Harness Audit — claude-code-plugins (2026-04-23)

## Summary
- 외부 레포(`claude-code-plugins`)는 **레포 전역 Rust 기반 `claude-plugin-validator` + `.githooks/pre-commit` 게이트**로 모든 플러그인의 매니페스트·SKILL·marketplace 교차검증을 강제 — 우리의 런타임 CLAUDE.md 규칙보다 객관적이고 CI-ready. 가장 주목할 만한 차이.
- 외부는 **`write-spec` / `shape-spec` / `create-tasks` / `drift-check` / `orchestrate-tasks` / `interview-capture`** 까지 lifecycle을 커맨드 단위로 쪼갠 **`sdd-lifecycle-plugin`** 과 **4-layer `doctor-docs-tree` health check**를 별도 플러그인화함. 우리 `hns`는 19개 커맨드를 단일 플러그인에 통합한 "monolith" — 기능 분리/다중 플러그인화 논의 가치 있음.
- 외부는 **Shape → Write → Tasks → Implement → Drift → Close의 "semantic lifecycle stage" 어휘**를 전 커맨드에서 일관되게 쓰고, 모든 커맨드 상단에 **Command Contract 블록(Input/Output/Stage/Preconditions)** 을 선언 — 우리의 `Required Inputs / Expected Outputs` 보다 엄격한 표준.
- 외부는 커맨드 frontmatter에 **`name:` 필드를 의도적으로 쓰는 플러그인**(`graylog-mcp`)과 **안 쓰는 플러그인**(`docs-tree-tools`, `context-onboarding-tools`)이 공존. 우리 CLAUDE.md의 "name 필드 금지" 규칙은 Claude Code의 실제 동작과는 선택사항이며, 외부는 "prefix 강제"보다는 "명시적 호출명 제어"로 쓴다 — 우리 규칙을 "권고(기본값)"로 약화하거나, 의도를 문서화 필요.
- 외부는 **`agents: ["./agents/...md"]` 와 `skills: ["./skills/.../SKILL.md"]` 를 plugin.json에 명시 등록**하는 패턴이 지배적이며, 일부(`prompt-craft`)는 `skills: "./skills/"` 디렉토리 문자열로 등록. 우리 `hns/plugin.json`은 `commands[]`만 있고 agents/skills/references는 자동 발견에 의존 — `agents`, `skills` 명시 등록 채택 검토 가치.

## Sources Compared
- **Ours**: `/Users/gideok-kwon/IdeaProjects/ai` (주 대상: `plugins/hns`, 매니페스트 `.claude-plugin/marketplace.json`)
- **External**: `/Users/gideok-kwon/IdeaProjects/claude-code-plugins` (매니페스트 `.claude-plugin/marketplace.json`)

## Structural Overview

### Ours (`ai/`)
```
ai/
├── .claude-plugin/marketplace.json     (7 plugins)
├── CLAUDE.md                           ← 플러그인 개발 규칙 집약
├── docs/
│   └── plugin-development-guide.md
└── plugins/
    ├── hns/                            ← 19 commands, 하네스 플러그인
    │   ├── .claude-plugin/plugin.json  (commands[] 9개만 등록, agents/skills 미등록)
    │   ├── commands/
    │   │   ├── init.md, start.md, validate.md, verify.md,
    │   │   ├── audit.md, wrapup.md, gc.md, doc-gen.md,
    │   │   └── validate-fe-design.md   (+ 미등록 추가 커맨드들?)
    │   ├── agents/
    │   ├── skills/
    │   ├── references/
    │   │   └── gc-protocol.md
    │   └── templates/
    ├── ai-debugger/, private-repo/, content-analyzer/,
    ├── study/, ideabank/, appkit/
```

### External (`claude-code-plugins/`)
```
claude-code-plugins/
├── .claude-plugin/marketplace.json     (24 plugins)
├── .githooks/pre-commit                ← 전역 pre-commit 훅
├── CLAUDE.md                           ← 짧은 룰만 (semver, validator, hooksPath)
├── README.md                           ← 1줄
├── tools/
│   ├── bin/claude-plugin-validator     ← Rust 컴파일 바이너리
│   └── claude-plugin-validator/        ← Rust 소스
│       ├── Cargo.toml
│       └── src/main.rs                 (1247줄, 10-step 검증)
└── <24개 플러그인, 대부분 독립 디렉토리>
    ├── docs-tree-tools/                (21 commands + 17 skills, docs-health 하네스)
    ├── sdd-lifecycle-plugin/           (10 commands, spec→task→drift)
    ├── context-onboarding-tools/       (1 command + 1 skill + references/)
    ├── plugin-validation-harness/      (1 command + scripts/replay_harness.py)
    ├── internal-devkit/                     (1 agent + 3 skills, "development harness")
    ├── graylog-mcp/                    (5 commands, name: 사용)
    ├── prompt-craft/                   (skills: "./skills/" 디렉토리 문자열)
    └── devops/, corex-tools/, mobile/, mrt-ad-*, mrt-design-system/,
        mrt-tna-mapper/, ai-champion/, change-log/, dooray-tools/,
        opensearch-mcp/, strategy-builder/, techspec-builder/,
        workflow-utils/, mrt-cancel-popup/, my-first-plugin/
```

---

## Patterns External Has, We Don't

### 1. Rust 바이너리 검증기 + `.githooks/pre-commit` 전역 게이트
- **Where**: `claude-code-plugins/tools/claude-plugin-validator/src/main.rs:1-1247`, `claude-code-plugins/.githooks/pre-commit:1-31`, `claude-code-plugins/CLAUDE.md:10-11`
- **What**: 10-step 검증기. `marketplace.json` 구조, `plugin.json` 필수 필드(name/description/version/author.name), semver X.Y.Z 정규식, `PLUGIN_ALLOWED_FIELDS` 화이트리스트 기반 unknown-field WARN, `commands[]`·`agents[]`에 나열된 경로의 실제 파일 존재 검증, `SKILL.md`의 `allowed-tools` frontmatter와 본문 백틱 툴 레퍼런스 교차검증, 디렉토리 내 plugin.json이 있지만 marketplace에 미등록된 디렉토리 탐지, marketplace description에 실제 skill 이름이 whole-word로 언급되는지 cross-check. JSON/색상 출력 둘 다 지원. exit-code: 0 PASS / 1 FAIL / 2 WARN.
- **Why adopt**: 우리 CLAUDE.md의 "5대 규칙(name 금지/registry 등록/version bump/description 250자)"은 모두 **사람이 의식적으로 지켜야 하는 런타임 규칙**이다. commit 시점에 기계가 강제하지 않으므로 누락 가능성이 구조적으로 존재. 특히 description 길이, skill 이름 cross-check, unknown-field, commands 경로 존재 여부는 이미 몇 차례 우리 레포에서도 문제가 됐다. Rust 바이너리는 의존성 0개로 macOS/Linux 둘 다 동작.
- **Risk**:
  - (a) Rust 툴체인 의존 — 빌드 담당이 없으면 검증기 stale 위험. 단 바이너리는 이미 체크인되어 있어 `cargo build`는 수정 시에만 필요.
  - (b) 우리 플러그인 수(7개) 규모에서 over-engineering 가능성 — 최소 셸 스크립트 버전으로 시작하는 대안 있음.
  - (c) 커맨드 `name:` 필드 금지, description 250자 같은 **우리 고유 규칙**은 외부 검증기에 없음 — 확장 구현 필요.
- **Verdict**: **채택 권장 (단계적)**. 1단계: Python/Bash 기반 경량 검증기 작성(marketplace↔plugin.json 경로 존재, semver, required fields) + `.githooks/pre-commit`. 2단계: 우리 고유 규칙(name 금지, description ≤250자) 추가. 3단계: Rust 포팅은 플러그인 수가 15개를 넘으면 고려.

### 2. `plugin.json`에 agents/skills 명시 등록
- **Where**: `claude-code-plugins/internal-devkit/.claude-plugin/plugin.json:10-15`, `claude-code-plugins/docs-tree-tools/.claude-plugin/plugin.json:35-53`, `claude-code-plugins/context-onboarding-tools/.claude-plugin/plugin.json:14-17`
- **What**: 외부는 `"agents": ["./agents/dev-guide.md"]`, `"skills": ["./skills/bootstrap/SKILL.md", ...]` 형태로 개별 파일을 **배열로 명시 등록**. 일부는 `"skills": "./skills/"` 디렉토리 문자열 형식도 사용(`prompt-craft`). 우리 `plugins/hns/.claude-plugin/plugin.json:8-18`은 `commands[]`만 있고 agents/skills는 디렉토리 자동 발견에 의존.
- **Why adopt**:
  - (a) **진실의 단일 소스(single source of truth)** — 무엇이 등록된 에이전트/스킬인지 매니페스트만 보면 즉시 파악 가능.
  - (b) 검증기가 `agents`/`skills` 경로 존재를 체크할 수 있음(`validate_file_refs`).
  - (c) 디렉토리에 방치된 deprecated 스킬이 "자동 발견"되어 유효 스킬인 양 로드되는 사고 방지.
- **Risk**: 매번 등록 갱신 필요 — 누락하면 스킬이 로드 안 됨. 단 이는 validator가 경고로 잡아줌.
- **Verdict**: **채택 권장**. `plugins/hns/.claude-plugin/plugin.json`에 `agents[]`, `skills[]` 명시 추가. 변경 범위 = `hns/plugin.json` 1파일 + 필요 시 marketplace description 업데이트.

### 3. Semantic Lifecycle Stage 어휘 표준화
- **Where**: `claude-code-plugins/sdd-lifecycle-plugin/commands/drift-check.md:9`("Semantic lifecycle role: `close` / `revisit`"), `claude-code-plugins/sdd-lifecycle-plugin/commands/shape-spec.md:9`("Semantic lifecycle stage: `shape`")
- **What**: 모든 SDD 커맨드가 상단 "Command Contract" 블록에서 자기가 속한 **lifecycle stage를 명시적 enum**으로 선언(`shape / write / task / implement / verify / close / revisit`). drift-check가 "close/revisit 검증", shape-spec이 "shape", 등.
- **Why adopt**: 우리 `hns`에는 `init → start → validate → verify → audit → wrapup → gc` 커맨드가 섞여 있지만, 어떤 게 어느 lifecycle 단계에 속하는지 커맨드 내부에 **명시된 곳이 없다**. 사용자와 AI 모두 "이 커맨드는 언제 쓰는가?" 판단을 description 자연어에 의존. stage enum이 있으면:
  - 커맨드 간 순서 제약을 기계 검증 가능(e.g., verify는 implement 뒤에만).
  - audit/gc 리포트에 "이 세션은 어디까지 왔는가?" 표시 가능.
- **Risk**: 우리 플로우가 외부의 Spec-Driven 모델과 완전히 일치하지 않음(우리는 `start`가 분류→라우팅을 하는 하이브리드). 억지로 맞추면 왜곡.
- **Verdict**: **채택 권장(우리만의 enum 정의)**. 예: `init | scan | shape | plan | implement | verify | audit | wrapup | gc | evolve`. 각 커맨드 frontmatter에 `stage:` 추가. 변경 범위 = `commands/*.md` 전체 frontmatter + 1개 reference doc.

### 4. Command Contract 블록 표준
- **Where**: `claude-code-plugins/sdd-lifecycle-plugin/commands/drift-check.md:6-13`, `claude-code-plugins/docs-tree-tools/commands/session-wrapup.md:13-20`
- **What**: 모든 커맨드가 헤더 직후 **`## Command Contract`** 섹션에 고정 하위 항목을 둠: Required Input / Expected Output / Prerequisite / Idempotency / Skills required / Evidence citation 규칙. 예: "Every finding must cite `{file}:{line}` evidence", "If `ret-*.md` already exists → skip with warning, no overwrite".
- **Why adopt**: 우리는 `## Required Inputs` / `## Expected Outputs` 정도만 쓰고 있지만, **Idempotency, Prerequisite, Evidence citation, Skills required** 는 거의 없음. 결과 문서가 덮어써지는지, 재실행 안전성이 어떤지 사용자가 알 수 없다. 특히 `/hns:wrapup`, `/hns:gc`, `/hns:audit`은 반복 실행 가능성이 높아 idempotency 규약이 꼭 필요.
- **Risk**: 스키마화 비용. 우리 커맨드 19개 전부를 한 번에 바꾸는 건 부담.
- **Verdict**: **채택 권장**. `references/command-contract-template.md` 생성 + 신규/수정 커맨드부터 점진 적용. 변경 범위 = reference 1개 + 리팩토링 대상 커맨드들.

### 5. 독립 Health-Check 플러그인 패턴 (`docs-tree-tools` doctor)
- **Where**: `claude-code-plugins/docs-tree-tools/commands/doctor-docs-tree.md:1-90`
- **What**: "doctor" 명명의 단일 커맨드가 4-layer weighted diagnostic(Index Integrity / Agent Guidance / Harness Principles / Evidence Coverage) + Prompt Surface Hygiene + Compaction Advisory + Git Drift Detection을 실행. strict/warn-only 플래그, pre-commit 자동 설치 제안, PASS/WARN/FAIL 레이어 출력.
- **Why adopt**: 우리 `/hns:gc`는 "dead code / doc drift / rule violation / stale harness" 체크를 가지고 있지만 **가중 계층화가 없고** strict/warn-only 분리가 없다. 특히 "pre-commit 자동 설치 제안" 흐름은 onboarding UX를 크게 개선.
- **Risk**: gc와 기능 중복 — `/hns:gc`를 확장할지, 신규 `/hns:doctor` 분리할지 결정 필요.
- **Verdict**: **보류 → 설계 후 결정**. 우선 `/hns:gc --layer` 모드로 레이어별 가중 스코어링을 확장하는 방향 우선 검토. 대형 리팩토링이므로 단독 ADR 필요.

### 6. Fixture-First Replay Harness(결정론 테스트 하네스)
- **Where**: `claude-code-plugins/plugin-validation-harness/scripts/replay_harness.py:1-250`, `claude-code-plugins/plugin-validation-harness/commands/validate-plugin-replay.md:1-32`
- **What**: YAML `manifest` → `adapter: fixture-copy`로 tmpdir sandbox에 fixture 복사 → `setup → apply → verify` phase 순차 실행 → 기계 판독 JSON + evidence 번들 출력. 샌드박스 경계 탈출 방지 검증까지 포함.
- **Why adopt**: 우리 `/hns:verify`는 실제 프로젝트 리포에서 lint/build/test를 돌리지만, **플러그인 자체의 재현 가능 테스트 하네스는 없다**. 특히 `init`·`doc-gen`·`start` 같은 파괴적 커맨드는 회귀 테스트가 필요.
- **Risk**: Python 의존, fixture 관리 부담. 플러그인 수가 적으면 ROI 낮음.
- **Verdict**: **미채택(당장은)** — 현재 플러그인 개수 기준 overkill. 단, `/hns:init` 등 파괴적 커맨드의 리팩토링이 잦아지면 재검토 후보로 기록.

### 7. `references/*-contract.md` 파일 네이밍 컨벤션
- **Where**: `claude-code-plugins/context-onboarding-tools/references/onboarding-contract.md:8-36`
- **What**: 스킬/커맨드가 강하게 의존하는 규약 문서를 **`-contract.md` 접미사**로 통일. "Ownership Boundary", "v1 Scope", "Runtime Modes", "Discovery Contract" 같은 고정 섹션 헤더.
- **Why adopt**: 우리 `plugins/hns/references/gc-protocol.md`는 접미사가 `-protocol`. 네이밍 혼선. contract vs protocol 의미 구분이 모호.
- **Risk**: 기존 참조 링크 깨짐. 전수 grep 필요.
- **Verdict**: **채택 권장(약)**. "규약" 성격이면 `-contract.md`, "절차" 성격이면 `-protocol.md`로 분리 문서화. 개별 파일명 변경은 점진 적용.

### 8. 레포 레벨 CLAUDE.md 단순화 (규칙만, 가이드는 분리)
- **Where**: `claude-code-plugins/CLAUDE.md:1-13` (13줄)
- **What**: 레포 루트 CLAUDE.md는 **5개 단문 rule만** 담고(semver/hooksPath/`use` keyword), 구체 가이드는 플러그인별 문서로 분산.
- **Why adopt**: 우리 루트 CLAUDE.md는 50줄에 플러그인 구조·명령 테이블까지 포함 — 플러그인 추가 시 매번 테이블 갱신 필요(이미 hns 19 vs plugin.json 9 불일치 발생 중).
- **Risk**: 분산 시 "어디서 찾지?" 질문 증가. 명확한 index 필요.
- **Verdict**: **채택 권장**. 루트 CLAUDE.md는 공통 규칙만, 플러그인 목록은 `marketplace.json`을 "ground truth"로 삼고 CLAUDE.md에선 링크만. 변경 범위 = 루트 CLAUDE.md 1파일.

### 9. 스킬 간 `use <plugin>:<skill>` FQN 참조 규약
- **Where**: `claude-code-plugins/CLAUDE.md:12`
- **What**: 스킬이 다른 스킬을 호출할 때 "use internal-devkit:setup"처럼 **fully qualified name 필수** 규칙.
- **Why adopt**: 우리는 스킬 간 참조가 암묵적 — 어떤 플러그인의 스킬인지 문서 내 불명.
- **Risk**: 없음. 문서 규칙만 추가.
- **Verdict**: **채택 권장(저비용)**. 플러그인 개발 가이드에 1줄 추가.

---

## Patterns We Have, External Doesn't

### A. 레포 루트 `docs/plugin-development-guide.md` (300+ lines)
- **Where**: `ai/docs/plugin-development-guide.md`
- **Why we have it**: 플러그인 개발 5대 규칙, commands vs skills 차이표, frontmatter 규약, marketplace 캐시 대처법까지 집약.
- **External's alternative**: 외부는 이런 가이드가 없고, CLAUDE.md 5줄 룰 + 각 플러그인 README에 암묵적으로 녹여둠.
- **Verdict**: **유지 권장**. 단, 이 가이드의 규칙 중 **기계 검증 가능한 항목(semver, description 길이, name 금지)은 validator로 자동화**하여 "문서 = 사양, validator = 강제"로 이중화.

### B. 한글 description + 한영 혼용 커맨드 이름
- **Where**: `ai/plugins/hns/commands/wrapup.md:2` (description에 한국어 trigger 명시)
- **Why we have it**: Claude가 한국어 요청을 자동 라우팅하도록 description에 "세션 정리, 회고, 작업 마무리, session wrapup, retrospective" 같은 다국어 키워드 포함.
- **External's alternative**: 외부도 일부 플러그인(`graylog-mcp`, `dooray-tools`)은 한글 description 사용. 하지만 trigger 키워드를 description에 나열하는 패턴은 우리가 더 체계적.
- **Verdict**: **유지 권장**. 외부 `internal-devkit/agents/dev-guide.md:6`도 "Triggers:" 섹션으로 동일 패턴 — 업계 표준에 부합.

### C. `/hns:audit` 자체 (외부 하네스 벤치마킹 커맨드)
- **Where**: `ai/plugins/hns/commands/audit.md`
- **Why we have it**: 지금 이 감사 리포트를 생성하는 메타 커맨드. `docs/benchmarks/YYYY-MM-DD-{source}.md` 산출.
- **External's alternative**: 없음. 외부는 자기 반성 메커니즘이 SDD의 `drift-check`로 구현되지만, 외부 레포/포스트와 비교하는 감사 툴은 부재.
- **Verdict**: **유지 + 강화**. 우리 고유 자산. 다만 지금 audit.md는 "URL/repo path/auto" 3-way 분기만 명시하고 **결정론적 비교 매트릭스 템플릿**이 references/에 없음 → `references/benchmark-matrix.md` 추가 권장.

### D. Self-Healing 피드백 루프 (`/hns:wrapup` → `/hns:evolve`)
- **Where**: `ai/plugins/hns/commands/wrapup.md:56-110` (실패 패턴 5분류 → evolve 자동 호출 → changelog)
- **Why we have it**: 회고에서 발견한 실패 패턴을 규칙/훅/스킬 수정으로 **자동 인코딩**하는 루프. 외부의 `drift-check`는 **감지**만 할 뿐 self-healing 까진 가지 않음.
- **External's alternative**: 외부 `session-wrapup`도 retrospective 생성까지는 동일하나, 규칙 자동 진화까지는 없음.
- **Verdict**: **유지 + 핵심 자산**. 다만 "Self-Healing Actions Taken" 테이블이 실제로 생성되는지 텔레메트리 필요. wrapup이 호출될 때 항상 evolve 제안이 뜨는지 감사.

### E. `/hns:validate` 의 dual-mode (docs + code)
- **Where**: `ai/plugins/hns/commands/validate.md`
- **Why we have it**: docs→code drift 검증과 code→standards drift 검증을 한 커맨드가 플래그로 분기.
- **External's alternative**: 외부는 분리 — `docs-tree-tools/commands/doctor-docs-tree.md`가 docs-health, `sdd-lifecycle-plugin/commands/drift-check.md`가 code-spec drift.
- **Verdict**: **유지 but 재검토**. Dual-mode는 사용자 학습 비용이 낮지만, 실제 구현 복잡도는 높아진다. 외부의 분리 패턴이 더 깔끔할 수도. ADR로 결정 기록 권장.

### F. `commands/` 경로 자동 발견 경고 (plugin-development-guide.md:67)
- **Where**: `ai/docs/plugin-development-guide.md:67`
- **Why we have it**: 문서: "`commands/` 디렉토리 안의 .md 파일은 plugin.json 등록 여부와 무관하게 자동 발견된다" — Claude Code 동작 실측 기반.
- **External's alternative**: 외부도 같은 동작 전제하에 `devops/plugin.json`처럼 commands[] 미등록 플러그인이 존재. 단 문서화는 없음.
- **Verdict**: **유지 + validator로 가드**. validator가 `commands/`에 있지만 `plugin.json`에 미등록된 파일을 WARN으로 보고하도록 확장.

---

## Common Patterns (Validated)
- **`.claude-plugin/marketplace.json` 중심 registry** — 양쪽 모두 채택 ✓
- **`plugin.json` 필수 필드**: name, description, version(semver), author.name ✓
- **`commands/{name}.md` 플랫 파일 + 상단 frontmatter** ✓
- **`skills/{name}/SKILL.md` 디렉토리 구조** ✓
- **`references/`, `templates/`, `agents/` 서브디렉토리 관례** ✓
- **세션 회고 / retrospective 커맨드 존재** (우리 `wrapup`, 외부 `session-wrapup`) ✓
- **Phase 기반 커맨드 서술(PHASE 0, PHASE 1, ...)** ✓ (외부 `shape-spec.md`, 우리 `start.md` 공통)
- **"Iron Law" / "Hard Rules" / "Constitutional Boundary" 개념** — 외부 `onboard-domain-repo.md:16` vs 우리 `verify.md:71` ✓
- **Evidence-based reporting(`file:line` 인용)** — 외부 `drift-check.md:9` vs 우리 `audit.md` ✓
- **한글 description에 trigger 키워드 나열** ✓
- **Plugin description 250자 내외 자동완성 친화** ✓

---

## Adoption Recommendations (우선순위 순)

1. **[HIGH] Pre-commit validator 도입 (경량 버전)**
   - 우선 Python 또는 Bash로 `tools/validate_plugins.sh` 작성: marketplace↔plugin.json 경로 존재, semver, required fields, description ≤250자, `commands/` 내 미등록 파일 WARN.
   - `.githooks/pre-commit` 추가 + `CLAUDE.md`에 `git config core.hooksPath .githooks` 1줄 추가.
   - 변경 범위: `tools/` 신규 2파일, `.githooks/pre-commit` 신규, `CLAUDE.md` 1줄.

2. **[HIGH] `plugin.json`에 agents/skills/references 명시 등록**
   - `plugins/hns/.claude-plugin/plugin.json`에 실제 스킬/에이전트 경로 배열 추가.
   - 부수적으로 "hns 19 vs plugin.json 9" 불일치 정리 — marketplace.json description의 숫자 갱신.
   - 변경 범위: `plugins/hns/plugin.json` + 루트 `CLAUDE.md` 테이블.

3. **[HIGH] Command Contract 템플릿 표준화**
   - `plugins/hns/references/command-contract-template.md` 신규 — Required Input / Expected Output / Stage / Prerequisite / Idempotency / Skills required / Evidence rule.
   - 신규 커맨드부터 적용, 기존 커맨드는 세션마다 1~2개씩 점진 마이그레이션.
   - 변경 범위: reference 1개 + (점진) 커맨드들.

4. **[MED] Semantic Lifecycle Stage enum 도입**
   - `references/lifecycle-stages.md`에 enum 정의: `init | scan | shape | plan | implement | verify | audit | wrapup | gc | evolve`.
   - 각 커맨드 frontmatter에 `stage:` 추가. validator가 enum 외 값을 WARN으로 체크.
   - 변경 범위: reference 1개 + 커맨드 frontmatter 전수.

5. **[MED] `commands/` 미등록 파일 발견 정리**
   - CLAUDE.md는 hns 19 commands 주장, plugin.json은 9개만 등록. 먼저 실제 파일 목록을 훑고 어느 쪽이 맞는지 결정.
   - 변경 범위: plugin.json commands[] 또는 CLAUDE.md 테이블 정합화.

6. **[MED] 루트 CLAUDE.md 슬림화 + Active Plugins 테이블 제거**
   - 플러그인 목록은 `marketplace.json`을 ground truth로. CLAUDE.md에서 자주 stale되는 숫자 테이블 제거.
   - 변경 범위: 루트 `CLAUDE.md` 1파일.

7. **[LOW] 스킬 FQN `use <plugin>:<skill>` 규약 문서화**
   - 플러그인 개발 가이드에 1줄 추가.
   - 변경 범위: `docs/plugin-development-guide.md` 1줄.

8. **[LOW] `references/` 파일 네이밍 `-contract` vs `-protocol` 분리 규칙**
   - 규약 문서(불변 규칙) = `-contract.md`, 절차 문서(실행 순서) = `-protocol.md`.
   - 변경 범위: 가이드 1줄 + 추후 리네이밍(고리스크 아님).

9. **[BACKLOG] Health-check 레이어드 스코어링(`/hns:gc` 확장)**
   - 외부 `doctor-docs-tree`의 4-layer weighted model을 우리 `gc`에 이식할지 ADR로 결정.

10. **[BACKLOG / 미채택]** Fixture-first replay harness (플러그인 규모 확장 전까지는 overkill).

---

## Next Steps
- 사용자가 위 우선순위 중 채택 항목을 선택
- 채택 항목은 `/hns:evolve`로 증분 반영 (또는 수동 PR)
- 채택 거절 항목은 `docs/benchmarks/2026-04-23-claude-code-plugins-decisions.md` 같은 decision log에 근거 기록(ADR) — 6개월 후 재감사 시 재검토 입력이 됨
- 특히 항목 1(validator)은 즉시 채택 시 나머지 모든 규칙의 기계 강제 기반이 되므로 first-mover로 권장

---

## 감사 중 발견한 부수 이슈

- `ai/CLAUDE.md:44`는 `hns` 19 commands라고 명시하지만 `ai/plugins/hns/.claude-plugin/plugin.json:8-18` commands[]는 9개만 등록. **실제 `commands/` 디렉토리를 전수하여 정합화 필요**.
- `ai/.claude-plugin/marketplace.json:25`의 hns description은 "5-dimension review"라 명시, 반면 `plugins/hns/.claude-plugin/plugin.json:3`은 "6-dimension review" — **숫자 불일치**. validator가 도입되면 바로 잡아낼 항목.
