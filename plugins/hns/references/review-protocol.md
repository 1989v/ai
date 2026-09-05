# Seed Discovery Protocol (Review)

Universal review protocol used by every `hns:spec-reviewer` run (architecture, domain, implementation, security, test-strategy, usecase).

## Stage 1: Seed Analysis
- Read target spec file
- Classify document type (spec, requirements, tasks, etc.)
- Extract internal references (file paths, class names, module references)

## Stage 2: First-Ring Companions
- Glob same-directory siblings:
  - `tasks*`, `status*`, `design*`, `context/*`
- Follow relative Markdown links found in spec

## Stage 3: Standards Discovery
- Read `docs/standards/`, `docs/conventions/`, and `.claude/rules/` entries relevant to the review dimension (by filename and headings)
- Service-local `CLAUDE.md` next to the code under review counts as a standard
- If `HNS_KB_PATH` is configured, run `${CLAUDE_PLUGIN_ROOT}/skills/kb/kb-search.sh <keywords>` and treat matching concept pages as standards; cite `[[page]] (vault, updated)`. Repo docs win on conflict — report the conflict

## Stage 4: Code Evidence
- Grep/Glob for referenced classes, modules, APIs in codebase
- Verify existence of referenced components
- Check for conflicts with existing implementations

## Verdict Rules

### SHIP
All checks passed, no issues found.
→ Proceed to next workflow step.

### REVISE
Non-blocking issues found.
- List each issue with Check # and evidence
- Recommend specific fixes
- Max 2 revision rounds, then escalate to BLOCK

### BLOCK
Critical issues that must be addressed.
- Stop immediately
- Escalate to human for decision
- Do not proceed until resolved

## Output Location
`docs/specs/{feature}/context/engineer-review-{type}.md`

## Evidence Requirements
- Every finding MUST cite at least one `{file}:{line}` reference
- Findings without evidence citations are INVALID
- For REVISE: spec anchor + file path evidence required
- For BLOCK: mandatory dual evidence (spec decision + code/doc violation)
