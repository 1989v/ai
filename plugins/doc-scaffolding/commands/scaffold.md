---
name: scaffold
description: "Analyze the current project and scaffold CLAUDE.md plus a standardized docs tree"
---

# /scaffold

Use the `doc-scaffolding:scaffold` skill to handle this request.

Follow that skill exactly:
- analyze the project structure and current documentation state
- collect any missing project-specific requirements from the user
- generate `CLAUDE.md` and the `docs/` tree
- validate the generated documentation against the codebase
- optionally generate an HTML docs site if the user wants it
