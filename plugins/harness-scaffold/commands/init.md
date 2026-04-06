---
name: init
description: "Initialize AI harness for any project — auto-scan + interactive setup + doc-gen + hooks + routing"
---

# /harness-scaffold:init

Use the `hns:session` skill context for this command.

## Purpose
Set up a complete AI harness environment for the current project.

## Required Inputs
- Access to project root directory

## Expected Outputs
- CLAUDE.md (project-customized)
- PLANS.md
- agent-os/ directory tree
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
4. Run `hns:doc-validate` for validation

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
- `agent-os/config.yml` — mode + layer settings
- `agent-os/product/mission.md` — from user input
- `agent-os/product/tech-stack.md` — from scan results
- `agent-os/standards/agent-behavior/` — all 6 files
- `agent-os/standards/global/conventions.md` — from scan + user input
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
- agent-os/ (standards, product, config)
- docs/ (architecture, adr, index, routing)
- .claude/hooks/ ({tier} tier)
- docs/specs/ (SDD spec directory)

Harness philosophy: docs/philosophy/
Context routing: docs/index.yml

Next: Use /harness-scaffold:shape-spec to start your first feature spec.
      Use /harness-scaffold:harness-audit to compare with external benchmarks.
```
