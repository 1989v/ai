---
name: doc-gen
description: "Generate CLAUDE.md and a standardized docs tree for the current project"
---

# /doc-gen

Use the `doc-scaffolding:doc-gen` skill to handle this request.

Follow that skill exactly:
- inspect the project to detect language, framework, and module structure
- choose the appropriate templates
- generate `CLAUDE.md` and the `docs/` tree
- if required information is missing, ask only for the minimal details needed to produce accurate docs
