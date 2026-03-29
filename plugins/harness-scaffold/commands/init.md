---
name: init
description: "Initialize AI harness for any project — auto-scan + interactive setup"
---

# /hnsf:init

Use the `harness-scaffold:session` skill context for this command.

## Purpose
Set up a complete AI harness environment for the current project.

## Required Inputs
- Access to project root directory

## Expected Outputs
- CLAUDE.md (project-customized)
- PLANS.md
- agent-os/ directory tree
- .claude/hooks/hnsf-automation.json
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
   - JUnit, Spock, Kotest → JVM
   - Jest, Vitest, Mocha → JS/TS
   - pytest, unittest → Python

4. **Existing AI Settings**: Check for
   - `.claude/` directory
   - `CLAUDE.md`, `AGENTS.md`
   - `docs/` structure

5. **Build/Test Commands**: Extract from build config

Present scan results to user.

## PHASE 2: Interactive Setup (3-5 questions)

Ask sequentially:

**Q1**: "프로젝트 프로파일이 맞나요?" + [scan results summary]
**Q2**: "아키텍처 패턴은?" (Clean Architecture / Layered / Monolith / Microservice / Other)
**Q3**: (If CLAUDE.md exists) "기존 CLAUDE.md와 병합할까요, 새로 만들까요?"
**Q4**: "모드 선택 — 품질 모드(기본, 비용 무관 최고 품질) / 효율 모드(토큰 절약)?"
**Q5**: "병렬 실행(git worktree) 지원이 필요한가요?"

## PHASE 3: Generate Files

Using templates from the harness-scaffold plugin, generate all files.
Replace `{{PLACEHOLDER}}` values with scan results and user answers.

**Always generate:**
- `CLAUDE.md` — from `templates/claude-md/default.md`
- `PLANS.md` — from `templates/plans-md.md`
- `agent-os/config.yml` — mode + layer settings
- `agent-os/product/mission.md` — from user input
- `agent-os/product/tech-stack.md` — from scan results
- `agent-os/standards/agent-behavior/` — all 6 files from templates
- `agent-os/standards/global/conventions.md` — from scan + user input
- `.claude/hooks/hnsf-automation.json` — from template
- `.claude/COMPACTION-GUIDE.md` — from template
- `docs/specs/` — empty directory

**Conditional:**
- `.claude/scripts/parallel-work.sh` — if Q5 = yes
- `agent-os/parallel-execution-rules.md` — if Q5 = yes

## PHASE 4: Idempotency Check

For each file to generate:
- If file doesn't exist → create
- If file exists and identical → skip with note
- If file exists and different → show diff → ask user: merge / skip / overwrite

## Completion

Output summary of generated files and suggest next steps:
```
AI harness initialized for [project-name]!

Generated:
- CLAUDE.md (project configuration)
- PLANS.md (execution plan rules)
- agent-os/ (standards, product, config)
- .claude/hooks/ (automation)
- docs/specs/ (SDD spec directory)

Next: Use /hnsf:shape-spec to start your first feature spec.
```
