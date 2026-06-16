# Ambiguity Gating Protocol

Socratic requirements clarification with a mathematical ambiguity gate.
Used by the Shape Spec phase (`hns:start` PHASE 1 / `spec-shaper`) to refuse
progression to spec-writing until requirements clarity crosses a threshold.

Benchmarked from oh-my-claudecode `deep-interview` (Ouroboros-inspired).
Adapted to hns conventions: hns paths, calibrated tone (`prompting-tone-guide.md`),
ontology feeds `hns:glossary` instead of a parallel entity model.

## When this runs

- `hns:start` Feature Pipeline PHASE 1, before write-spec.
- Skipped when: request is already concrete (file paths / class names / acceptance
  criteria present), `--no-interview` passed, or depth resolves to `quick` with
  initial ambiguity already ≤ threshold.

## Depth modes

| Mode | Flag | Behavior |
|------|------|----------|
| quick | `--quick` | Topology gate + 1–3 questions; proceed if ambiguity ≤ threshold |
| standard | (default) | Full loop, soft cap 10 rounds |
| deep | `--deep` | Full loop + all challenge modes, hard cap 20 rounds |

## Phase 0: Resolve threshold

Read `hns.shape.ambiguityThreshold` in precedence order (project overrides user):
1. `./.claude/settings.json`
2. `[$CLAUDE_CONFIG_DIR|~/.claude]/settings.json`
3. default `0.2`

Record the resolved value and its source. Carry both into the shaping artifact metadata.
Emit one line before the first question:

```
Shape gate threshold: {percent} (source: {project|user|default})
```

## Phase 1: Detect context (greenfield vs brownfield)

1. Run `Explore` agent: does cwd have source / package files / git history relevant to the idea?
2. Source exists AND idea references modifying/extending it → **brownfield**; else **greenfield**.
3. Brownfield: run `Explore` to map relevant areas → store as `codebase_context`. Also
   glob prior `docs/specs/*/planning/requirements.md` for durable facts already settled.

Gather codebase facts before asking the user. Never ask what the code already reveals —
when a question is triggered by repo evidence, cite the file/symbol/pattern in the question.

Load hierarchical sub-context per `hierarchical-delegation.md` (service-local CLAUDE.md / glossary).

## Round 0: Topology enumeration gate

Run once, before any scoring. Locks the *shape* of scope so depth-first questioning on the
most-described component can't hide ambiguity in its siblings.

1. Enumerate candidate top-level components (1–6) — workstreams/surfaces/integrations/deliverables
   that can succeed or fail independently. Group siblings if more than 6. Implementation tasks and
   fields are not components unless the user framed them as independent outcomes.
2. Ask one confirmation question (this is the only pre-scoring question):

```
Round 0 | Topology confirmation

I read this as {N} top-level component(s):
1. {name}: {one-sentence description}
2. ...

Right? Add / remove / merge / split / defer any?
```

3. Lock the confirmed component list into `shaping-state.yml` with per-component clarity slots.
   Single confirmed component → pass through with one component carried forward.

## Phase 2: Interview loop

Repeat until `ambiguity ≤ threshold` or early exit.

### 2a. Pick the target
- Choose the active component + dimension with the **lowest** clarity score.
- When >1 active components are similarly weak, rotate across them (don't re-drill the last one).
- One sentence, stated before the question: name the weakest dimension, its score, and why it's
  the current bottleneck.

### 2b. Ask ONE question
Use `AskUserQuestion` with contextual options + free-text. Expose assumptions, don't gather feature lists.

```
Round {n} | Component: {name} | Targeting: {dimension} | Why: {one sentence} | Ambiguity: {score}%

{question}
```

Question styles by dimension:

| Dimension | Style | Example |
|-----------|-------|---------|
| Goal | "What exactly happens when…?" | "When you say 'manage tasks', what's the first action a user takes?" |
| Constraint | "What are the boundaries?" | "Offline-capable, or is connectivity assumed?" |
| Criteria | "How do we know it works?" | "Shown the finished product, what makes you say 'that's it'?" |
| Context (brownfield) | "How does this fit?" | "Found JWT auth in `src/auth/` (passport+JWT). Extend it or diverge?" |
| Scope-fuzzy (ontology) | "What IS the core thing?" | "You've said workflow, inbox, and planner — which is the core entity, which are views?" |

### 2c. Score ambiguity
After each answer, score each dimension 0.0–1.0 with a one-line justification + remaining gap.
Honor locked topology: score every active component independently; never drop a confirmed sibling
because one is already clear.

- **Goal Clarity** — primary objective stated in one sentence without qualifiers; key entities (nouns) and relations (verbs) unambiguous.
- **Constraint Clarity** — boundaries, limits, non-goals clear.
- **Success Criteria** — a test could verify success; acceptance criteria concrete.
- **Context Clarity** (brownfield only) — existing system understood well enough to modify safely.

Weighted ambiguity:

```
Greenfield:  ambiguity = 1 − (goal·0.40 + constraints·0.30 + criteria·0.30)
Brownfield:  ambiguity = 1 − (goal·0.35 + constraints·0.25 + criteria·0.25 + context·0.15)
```

Overall dimension scores = coverage-weighted weakest across active components (one clear component
must not mask a vague sibling).

### 2d. Track ontology (feeds hns:glossary)
Extract entities (name / type / fields / relationships) each round. Round 1: all new, no stability.
Rounds 2+: compare to the previous round —
- stable = same name both rounds
- changed = different name, same type, >50% field overlap (renamed → counts toward stability)
- new / removed = unmatched
- `stability_ratio = (stable + changed) / total`

Converged when the same entities appear two consecutive rounds with no change. On completion, the
ontology is handed to `hns:glossary` as candidate ubiquitous-language terms — do not maintain a
second glossary here.

### 2e. Report progress

```
Round {n} complete.

| Dimension | Score | Weight | Weighted | Gap |
|-----------|-------|--------|----------|-----|
| Goal | … | … | … | … |
| Constraints | … | … | … | … |
| Success Criteria | … | … | … | … |
| Context (brownfield) | … | … | … | … |
| Ambiguity | | | {score}% | |

Topology: targeted {name} | active {n} | deferred {n}
Ontology: {count} entities | stability {ratio} | new {n} changed {n} stable {n}
Next: {component}/{dimension} — {why}
```

### 2f. Stop conditions

- **Round 3+**: allow early exit on "enough / let's go / build it" — warn with remaining gaps.
- **Round 10** (standard cap): soft warning, offer to continue or proceed.
- **Round 20** (deep hard cap): proceed with current clarity, note the risk.
- **Stall** (ambiguity within ±0.05 for 3 rounds): switch to Ontologist mode to reframe.
- **All dimensions ≥ 0.9**: skip to completion.
- **"stop / cancel / abort"**: halt, persist state for resume.

## Phase 3: Challenge modes

Perspective shifts injected into question generation, each used once, tracked in state:

| Mode | Activates | Injection |
|------|-----------|-----------|
| Contrarian | Round 4+ | "What if the opposite were true? Is this constraint real or habitual?" |
| Simplifier | Round 6+ | "What's the simplest version still valuable? Which constraints are assumed vs necessary?" |
| Ontologist | Round 8+ (if ambiguity > 0.3) or on stall | "What IS this, really? Of the tracked entities, which is core and which are supporting?" |

## Phase 4: Persist outcome

Write to `docs/specs/{date}-{name}/planning/requirements.md` (see `templates/specs/shaping-template.md`):
topology, per-dimension clarity breakdown, goal, constraints, non-goals, acceptance criteria,
assumptions exposed/resolved, ontology table + convergence, and the collapsed transcript.

Persist resume state in `planning/shaping-state.yml`: rounds, current ambiguity, threshold + source,
topology, challenge modes used, ontology snapshots. Re-running shape on an existing spec resumes from
the last completed round.

Seed any unresolved items into `open-questions.yml` (category `pre-impl`).

## Resume

Re-run shape on an existing `planning/shaping-state.yml` → continue from the last completed round.
State missing `topology` (legacy) → run Round 0 once, then continue the existing transcript.

## Hand-off

On gate pass (or approved early exit), Shape Spec is complete → `hns:start` proceeds to PHASE 2
(write-spec). The approval-gated execution decision stays at PHASE 5 — this protocol gates *clarity*,
not *consent*.
