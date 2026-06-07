---
description: "Initialize AI harness for any project — auto-scan + interactive setup + doc-gen + hooks + routing"
---

# /hns:init

Use the `hns:session` skill context for this command.

## Purpose
Set up a complete AI harness environment for the current project.

## Required Inputs
- Access to project root directory

## Expected Outputs
- CLAUDE.md (project-customized)
- PLANS.md
- docs/ directory tree
- docs/ directory tree (architecture, adr, index)
- docs/index.yml (context routing map)
- .claude/hooks/ (selected tier)
- .claude/COMPACTION-GUIDE.md
- docs/specs/ directory
- (Optional) .claude/scripts/parallel-work.sh

---

## PHASE 1: Auto Scan

Analyze the project root to build a profile:

1. **Language/Framework**: Check build files
   - `build.gradle.kts` / `build.gradle` → Java/Kotlin + Gradle
   - `pom.xml` → Java + Maven
   - `package.json` → Node.js (check for TS, framework)
   - `pyproject.toml` / `requirements.txt` → Python
   - `go.mod` → Go
   - `Cargo.toml` → Rust

2. **Module Structure**: Check for monorepo/multi-module
   - `settings.gradle.kts` includes → multi-module
   - `workspaces` in package.json → monorepo
   - Multiple `*/src/main` patterns → multi-service

3. **Test Framework**: Detect from dependencies

4. **Existing AI Settings**: Check for `.claude/`, `CLAUDE.md`, `AGENTS.md`, `docs/`

5. **Build/Test Commands**: Extract from build config

Present scan results to user.

## PHASE 1.5: Convention Library (optional)

1. PHASE 1 스캔 결과를 `templates/conventions/manifest.yml`의 각 번들 `detect` 규칙과 매칭하여 적용 가능한 번들을 식별한다.
2. 매칭된 번들이 있으면 사용자에게 제시 (없으면 이 단계 스킵):
   ```
   감지된 스택: {detected_stack}
   매칭 컨벤션 번들:
     - backend-kotlin-spring (9 files)
     - messaging-kafka (1 file)
   이 스택에 맞는 코딩 컨벤션 파일도 생성할까요? [Y/n] (번들 개별 선택 가능)
   ```
3. 승인된 번들의 파일을 `docs/conventions/` 하위로 복사하고, 플레이스홀더를 치환한다:
   - `{{base_package}}` → 스캔된 루트 패키지 (dot form, 예: `com.example.app`)
   - `{{base_package_path}}` → 위 값의 dots→slashes (예: `com/example/app`)
   - `{{design_system}}` → 사용자 입력 (없으면 `@org/design-system` 기본값 + TODO 주석)
   - `{{service}}` → 모듈/서비스명
4. `docs/conventions/conventions.md`(베이스라인)에 생성된 번들 파일 링크를 인덱스로 추가한다.
5. 거절 시 베이스라인 `conventions.md`만 생성하고 계속한다.

> `performance` 번들은 `detect: opt-in` 이므로 자동 매칭되지 않고, 사용자가 명시적으로 원할 때만 제안한다.

## PHASE 2: Interactive Setup (3-5 questions)

**Q1**: "프로젝트 프로파일이 맞나요?" + [scan results summary]
**Q2**: "아키텍처 패턴은?" (Clean Architecture / Layered / Monolith / Microservice / Other)
**Q3**: (If CLAUDE.md exists) "기존 CLAUDE.md와 병합할까요, 새로 만들까요?"
**Q4**: "모드 선택 — 품질 모드(기본) / 효율 모드(토큰 절약)?"
**Q5**: "병렬 실행(git worktree) 지원이 필요한가요?"

## PHASE 3: Doc Generation

Delegate to `hns:doc-gen` skill:
1. Select CLAUDE.md template based on language/framework
2. Generate CLAUDE.md with scan results + user answers
3. Generate docs/ tree (index.md, architecture/, adr/, plans/)
4. Run `hns:validate --docs` for validation

## PHASE 4: Hook Tier Selection

Ask user:
```
프로젝트에 적용할 훅 수준을 선택하세요:
  (A) Light  — 리마인더만 (신규 프로젝트, 탐색 단계)
  (B) Medium — 린트/컴파일 피드백 (개발 진행 중)
  (C) Strict — 실패 시 차단 (안정 운영 단계)
```

Copy selected template from `templates/hooks/hnsf-hooks-{tier}.json` to `.claude/hooks/`.

## PHASE 5: Context Routing Setup

1. Copy `templates/docs-index.yml` → `docs/index.yml`
2. Replace placeholders with scan results
3. Add project-specific entries based on detected structure

## PHASE 6: Generate Remaining Files

Using templates, generate:
- `PLANS.md` — from `templates/plans-md.md`
- `.claude/config.yml` — mode + layer settings
- `docs/product/mission.md` — from user input
- `docs/architecture/overview.md` — tech stack + layers + build/test commands (from scan)
- `docs/standards/agent-behavior.md` — agent behavior standards (6 sections)
- `docs/conventions/conventions.md` — baseline code conventions (from scan + user input)
- `.claude/COMPACTION-GUIDE.md` — from template
- `docs/specs/` — empty directory
- (Conditional) `.claude/scripts/parallel-work.sh`

## PHASE 7: Idempotency Check

For each file:
- If not exists → create
- If exists and identical → skip
- If exists and different → show diff → ask: merge / skip / overwrite

## Completion

```
AI harness initialized for [project-name]!

Generated:
- CLAUDE.md (project configuration)
- PLANS.md (execution plan rules)
- docs/ (product, architecture, standards, conventions, adr, index, routing)
- .claude/ (config.yml, hooks/ {tier} tier, COMPACTION-GUIDE.md)
- docs/specs/ (SDD spec directory)

Harness philosophy: docs/philosophy/
Context routing: docs/index.yml

Next: Use /hns:shape-spec to start your first feature spec.
      Use /hns:audit to compare with external benchmarks.
```
