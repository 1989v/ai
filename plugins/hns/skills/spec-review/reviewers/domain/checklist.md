# Domain Review

## Seed Discovery Protocol
Apply `references/review-protocol.md` stages 1–4 (Seed Discovery).

## Reference
`references/language-reference.md` — glossary 포맷·규칙의 단일 출처.

## Checklist
- [ ] Bounded context boundaries clearly defined? No leakage across contexts?
- [ ] **Glossary present?** `docs/product/glossary.md` exists, or (multi-BC) `docs/context-map.md` points to per-BC glossary
- [ ] **Spec vocabulary matches glossary?** Every domain noun in spec.md is defined in glossary (or is a newly-introduced term flagged for `/hns:glossary`)
- [ ] **No `Avoid:` synonyms used in spec?** Deprecated synonyms in glossary's `Avoid` lines are not used in spec.md
- [ ] Ubiquitous language consistent between spec and existing codebase?
- [ ] Aggregate invariants explicitly stated and enforceable?
- [ ] Domain events properly scoped to owning aggregate?
- [ ] No cross-aggregate direct references? (API only)
- [ ] Value Objects vs Entities correctly classified?

For each check item, apply the matching procedure in `skillsets/` if one exists.

### Glossary Conflict Verdict Rules
- Missing glossary entirely → **REVISE** (recommend running `/hns:glossary` after spec ships)
- Spec uses `Avoid:` synonym → **BLOCK** (must resolve before proceeding)
- Spec coins new domain term without glossary entry → **REVISE** (run `/hns:glossary --conflict {term}`)
- Spec uses term with different meaning than glossary → **BLOCK** (real ubiquitous-language violation)

## Verdict
- **SHIP**: All checks passed
- **REVISE**: Non-blocking issues (max 2 rounds)
- **BLOCK**: Critical domain model violation → escalate

## Output
`docs/specs/{feature}/context/engineer-review-domain.md`

## NEVER
- Start review without Seed Discovery Protocol
- Return verdict without evidence (cite file:line)
- Mix reviewer types
