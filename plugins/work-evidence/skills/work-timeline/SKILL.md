---
name: work-timeline
description: Create a privacy-reviewed offline work timeline from explicitly authorized Git, Jira, wiki and optional metric evidence, with date filters, item details and outcome metrics.
---

# Work Timeline

Create an evidence-led work narrative, not a commit leaderboard. Put the main impact/progression diagram before the dated evidence timeline. Include dated outcome metrics only where defensible. The interactive date range and status filter must update both item details and metrics/diagram together. Status semantics are explicit: “new” means first started in the selected range; “ongoing” means active during the range and begun before its start; “done” means a completed item overlaps the range. These are relative to the selected range, not inferred from ticket status alone. Use `status=done` only for confirmed completion; `date` is start, `end_date` is confirmed completion. Open items extend through the report end. Missing start dates must be resolved or omitted.

## Intake and authorization
Before collection, ask together for company/personal context, topic or question, period and timezone, audience, and the user's own account roles. Private organization/repository/account IDs, author identities and wiki page/space IDs go only in a user-controlled local scope/config, never in conversation or model context. Use aliases, roles, counts and date ranges in the conversation. Propose concrete read-only sources: Git repositories/organizations, Jira projects, optional company wiki spaces/pages (Confluence, Notion, internal wiki, decision documents, runbooks and revision history), and optional logs/metrics. Name source/page/date boundaries, permission limits, units and baseline. Obtain explicit confirmation of this scope before collecting anything, including optional wiki spaces/pages and revision/date limits. Grants are per source and per wiki space/page: never infer permission for child spaces/pages, neighboring repositories or linked documents. Earlier confirmed scope may be reused only for the same unfinished task. Connector availability is not authorization. Never infer access or inaccessible facts; do not seek credentials or shared API tokens. Do not publish or send messages.

## Local privacy boundary
Collect only through authorized read-only sources. Company content and personal data must not enter model intermediates, raw dumps, prompts, generated files, or artifacts. Perform selection, aggregation and redaction locally first; use a local connector/tool or user-provided sanitized records that can honor this boundary. If a connector returns raw content into model context, do not use it for this workflow. Ask for a locally prepared sanitized export instead. Never silently relax this boundary to finish.

Project, person, ticket, commit, wiki, customer and account identifiers become stable safe aliases. Preserve source kind, alias locator, observation time, safe fact and provenance; keep any alias-to-private-source map outside the artifact and model context, under the user's control. Review ambiguous/sensitive wording and quantities with the user before rendering. Omit unapproved values; do not guess missing measurements. Do not copy raw prose, payloads, stack traces or private links. Public references are optional and must be truly public, explicitly allowlisted by hostname and reviewed in full. Sensitive paths, query strings, fragments and embedded credentials are forbidden. Private references use aliases only.

Read [references/input.md](references/input.md) before building the sanitized input. The renderer rejects unknown fields, requires collection and content review flags, builds a fixed projection, escapes text, and scans both input and complete output for selected secret/PII patterns. This is defense in depth: pattern filtering cannot identify every name, company secret, indirect identifier, encoded secret or misleading claim. Human review and local minimization remain mandatory. Never claim the scan proves anonymization.

## Diagram-first delivery
Apply explain-diagram's design directly: choose the main diagram before prose; use a brief title, one audience-appropriate sentence, labeled relationships and an explicit caption. Business readers see impact, choices and risk; technical readers see mechanism, dependencies or state; general readers see plain-language progression. Do not reuse one generic diagram across modes. Supplement with short text that answers the stated question. Metrics require unit, measurement definition, baseline and evidence; activity counts are not business outcomes and correlation is not causation.

Generate offline files only: no remote scripts, fonts, images, analytics, fetches or assets. Use the CLI below. Validate every artifact with `--check` and inspect the sanitized source and generated markup for leakage including comments, URLs, metadata and filenames. Render visually only if suitable tools exist and current computer-use approval explicitly covers that action; otherwise report that visual verification was not performed. Do not change global settings. Final response links local files and states scope, missing evidence and verification limits succinctly.

Resolve `<SKILL_DIR>` to the directory containing this loaded `SKILL.md`. In Claude Code, use `${CLAUDE_SKILL_DIR}`; in Codex, use the absolute installed skill directory from its catalog. Do not assume a home directory or working directory. Python 3.9+ and an available IANA timezone database are required. No third-party Python packages or sibling skill installation are needed.

```sh
python3 "<SKILL_DIR>/scripts/render.py" --input /absolute/sanitized.json --output /absolute/work-timeline.html
python3 "<SKILL_DIR>/scripts/render.py" --check /absolute/work-timeline.html
```
