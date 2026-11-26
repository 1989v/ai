# Sanitized input contract

Use JSON with exactly the following fields; renderer rejects unknown fields at every object boundary. Text is escaped, never interpreted as HTML. Strings are limited to 2400 characters. Lists and input size are bounded. Use neutral output filenames. The review booleans record an actual user review; do not set them automatically or treat them as a privacy guarantee.

```json
{
  "schema_version": 1,
  "mode": "timeline",
  "title": "Delivery Progress",
  "summary": "Reviewed changes support the stated result.",
  "audience": "technical",
  "context": "personal",
  "question": "What changed and what evidence supports it?",
  "period": {"start":"2026-01-01","end":"2026-01-31","timezone":"Asia/Seoul"},
  "approval": {"collection_confirmed":true,"wording_reviewed":true,"quantities_reviewed":true},
  "scope": {"sources":["Source A"],"roles":["Maintainer"]},
  "items": [{
    "id":"E1","kind":"commit","title":"Reviewed change","date":"2026-01-12",
    "end_date":"2026-01-12","status":"done","summary":"A locally reviewed change was completed.",
    "owner_role":"Maintainer",
    "evidence":{"source_alias":"Source A","locator":"change-1","observed_at":"2026-02-01","detail":"Local source inspection confirms this scoped change."},
    "outcome":"The approved verification completed.",
    "metric":{"label":"Processing time","before":30,"after":20,"unit":"ms","baseline":"Same approved fixture before the change","measurement":"Median of the approved local runs; no production attribution"}
  }],
  "diagram":{
    "nodes":[{"id":"N1","label":"Reviewed change","evidence_ids":["E1"]},{"id":"N2","label":"Verified result","evidence_ids":["E1"]}],
    "edges":[{"from":"N1","to":"N2","label":"verified with approved fixture"}],
    "caption":"The scoped check supports the recorded result."
  }
}
```

The example is illustrative, not evidence; never reuse its measurements or claims as real findings. Omit `metric` or `outcome` if unsupported. Metric fields are all required when present. A metric must identify comparable baseline and measurement conditions; its item date is the measurement date. Do not imply date filtering recomputes a baseline or an aggregate. Activity counts belong in evidence, not in business outcome claims.

`date` means start date, `end_date` means confirmed completion, and open items extend to report end. For completed items `status` must be `done` with `end_date`; other status values are `new` and `ongoing` but filter classification is recalculated relative to the chosen range. Items begun before report start are allowed when they overlap. Times must be converted locally to the selected IANA timezone before taking their calendar date. All date-range boundaries are inclusive.

Evidence kinds are `ticket`, `commit`, `wiki`, `metric`; IDs are neutral `E1`, `E2`, etc. Every item records a safe source alias from scope, a neutral locator (`ref-1`, `change-1`, `ticket-1`, `page-1`, `sample-1`, `revision-1`), observation date and specific safe detail. Locators must never be actual private issue keys, hashes, wiki IDs or raw URLs. Keep traceability in a user-controlled local private map; never place that map in artifacts or model context. Every role must be declared in scope. Node IDs are `N1` etc.; optional `evidence_ids` associates nodes with evidence visibility. Unassociated nodes and labeled relationships remain report-wide context, explicitly described in the artifact. Do not present such global context as a date-filtered claim.

Public links are omitted by default. Only when the user confirms a reference is genuinely public and approves its exact URL, add `public_reference_hosts:["public.example.org"]` at the top level and `public_url` inside evidence. Only clean HTTPS host/path URLs without credentials, port, query, fragment, escapes or local/private domain suffixes are supported. Hostname validation cannot establish public availability or absence of sensitive path data; independently check that without disclosing private content. Do not add a link merely because its hostname is GitHub or a wiki provider.

For handoff set `mode:"handoff"` and include:

```json
"handoff": {
  "context":"What the next role needs to know, using reviewed aliases.",
  "known_state":["Observed and verified state; missing facts remain unknown."],
  "decisions":[{"text":"Recorded decision and tradeoff.","evidence_ids":["E1"]}],
  "unresolved":[{"text":"Unresolved question or risk.","owner_role":"Maintainer","evidence_ids":["E1"]}],
  "next_verification":[{"text":"Concrete next check and expected observable result.","owner_role":"Maintainer","evidence_ids":["E1"]}]
}
```

Decisions may include `owner_role`; unresolved work and verification require it. Empty evidence lists explicitly mean no supporting evidence recorded, not an inferred fact. Print companion includes all reviewed evidence without active filters. The interactive handoff retains decisions and next actions while indicating how many supporting items remain under the current evidence filter.

# Actionable collection paths

Keep private organizations, repositories, accounts, author identities, projects and wiki IDs in user-controlled local config only; confirmation in conversation names safe aliases, roles and bounded counts/ranges. Grants do not inherit across spaces, child pages or links.

No connector integration is bundled. Prefer an available read-only connector only if it performs local minimization before any model-visible return. Otherwise have the user export selected sources locally into a local minimizer or supply already-sanitized JSON. Never print a raw export into the conversation.

- **Git commits:** the bundled `scripts/collect_git.py` reads a user-prepared local scope file, requires its explicit approval flag, selects one exact author identity and inclusive local date range, and emits dates plus neutral aliases only. No messages, diffs, authors, paths, hashes or remote URLs enter its output. It returns *metadata evidence*, not outcome claims. Run it locally: `python3 "<SKILL_DIR>/scripts/collect_git.py" --scope /private/location/git-scope.json --output /safe/location/git-items.json`. Review and merge those items into the full input. See script help for scope fields. A local mapping back to specific commits is intentionally not produced; use source/date/local Git review to resolve evidence, and retain any private map separately under user control.
- **Git PRs:** authorize exact repositories, own login/role, created/updated/merged date criteria and pagination limits. A local reader selects PR metadata and review/merge events and minimizes them before return; private PR numbers, titles, URLs and authors become aliases/approved wording. Confirm whether attribution is author, reviewer or merger. Do not infer deployment or outcome from merge.
- **Jira:** authorize project, own account and role (assignee/reporter/reviewer), fields and date semantics. Apply bounded JQL locally with explicit start and exclusive next-day end in selected timezone; inspect changelog only when approved. Transform issues locally into safe status-transition facts, aliases and approved summaries. An issue assigned to the user is not proof the user implemented it.
- **Wiki:** authorize exact Confluence spaces/pages, Notion pages/databases, or internal-wiki paths plus revision/date limits. Locally inspect selected revisions, decision documents and runbooks; omit collaborator names, private URLs and operational details. Distinguish recorded decision, current document and historic revision. If revision history is unavailable, state that a historical decision cannot establish the current state; cite the reviewed alias and available observation date without inventing a revision. A page update is not proof of deployment or policy adoption.
- **Logs/metrics:** authorize source, environment, aggregate query, interval, timezone, unit, sample/window and comparable baseline. Aggregate locally; exclude raw messages, IDs, IPs, traces, customer dimensions and small identifiable cohorts. Preserve a safe query/measurement description and observation time. Describe missing data rather than inventing a result.

If any required reader cannot honor authorization, pagination, minimization or permissions, stop collection for that source, state the evidence gap and continue with approved sanitized exports. Read-only means no edits, comments, transitions, messages, deploys or publication.

# File-write guarantees

CLI writes stage fully validated content in private temporary files beside each output, then publish complete files without replacing existing paths. Ordinary failures remove new outputs and staged files. Multiple outputs are not crash-atomic across directories; an abrupt process/machine failure may leave a complete subset or private temporary files. Inspect locally and remove abandoned stages before retrying; never claim filesystem-wide transactionality.
