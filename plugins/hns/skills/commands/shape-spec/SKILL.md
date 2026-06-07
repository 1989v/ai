---
user-invocable: false
---

# /hns:shape-spec

## Purpose
Gather clear, testable requirements before writing a formal spec.md.

## Required Inputs
- Feature description (user prompt or roadmap reference)

## Expected Outputs
- `docs/specs/YYYY-MM-DD-{name}/` folder structure
- `planning/requirements.md`
- `planning/test-quality.md`
- `context/open-questions.yml`

---

## PHASE 1: Initialize

Delegate to `spec-initializer` agent:
- Create dated spec folder under `docs/specs/`
- Save raw idea to `planning/initialization.md`

## PHASE 2: Load Documentation Context

### 2.1 Domain Glossary (always)
IF `docs/product/glossary.md` exists:
- Load full content — this is the **ubiquitous language** all subsequent phases must use
- Note all `Avoid:` synonyms — if the feature description uses any, flag for grilling in PHASE 3
ELSE:
- Note "no glossary.md — recommend running /hns:glossary after this spec"
- Do NOT block; continue with degraded coherence

IF `docs/context-map.md` exists (multi-BC project):
- Identify which BC this feature belongs to → load that BC's glossary.md instead

### 2.2 Index-based Loading
IF `docs/index.yml` exists:
- Extract keywords from feature description
- Match against index entries
- Load top 3 related specs (README level)
- Load top 2 references (full content)
- Load matching standards

ELSE: Note "no docs/index.yml — using docs/standards/ fallback"

## PHASE 3: Research Requirements

Delegate to `spec-shaper` agent with:
- Feature initialization from Phase 1
- Documentation context from Phase 2 (incl. glossary.md if present)
- `docs/product/` context (mission, tech-stack)
- `docs/standards/` for compliance

Agent will:
1. Generate 4-8 clarifying questions — **use glossary.md vocabulary**; if user introduces a term that conflicts with `Avoid:` synonyms, ask first
2. Process user answers + mandatory visual check
3. Follow up if needed (max 1-3 questions)
4. Save to `planning/requirements.md`

If during Q&A a new domain term is coined or an existing term is sharpened:
- Recommend `/hns:glossary --conflict {term}` to inline-update before continuing
- Do NOT silently invent new vocabulary

## PHASE 4: Build Abstract Test Strategy

Create `planning/test-quality.md` (stack-neutral):
- Assign scenarios to test layers (unit, integration, component, e2e)
- Identify critical paths vs nice-to-have coverage
- Reference project test framework from tech-stack.md

## PHASE 5: Seed Open Questions

Create `context/open-questions.yml`:
- Classify unresolved items from Q&A as: pre-impl, impl-discovery, test-discovery, closure, waiver-revisit
- If no unresolved items, create empty registry

## Completion

Inform user:
```
Spec shaped: docs/specs/[dated-folder]/

Created:
- planning/requirements.md
- planning/test-quality.md
- context/open-questions.yml

Next: /hns:write-spec to create the specification
```
