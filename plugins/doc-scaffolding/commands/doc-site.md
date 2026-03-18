---
name: doc-site
description: "Build a static HTML documentation site from the docs tree"
---

# /doc-site

Use the `doc-scaffolding:doc-site` skill to handle this request.

Follow that skill exactly:
- inspect the existing `docs/` tree
- generate the HTML documentation site using the plugin template
- keep output self-contained with no external runtime dependency unless the user explicitly asks otherwise
