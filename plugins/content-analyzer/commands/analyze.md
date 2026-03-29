---
name: analyze
description: "Analyze content from a URL (YouTube, LinkedIn, web post, Git repo) and generate a learning plan or analysis document"
---

# /analyze

Use the `content-analyzer:link-fetch` skill to fetch content, then `content-analyzer:content-analyze` to analyze it, and finally `content-analyzer:doc-generate` to produce the output document.

Alternatively, use the `content-analyzer:analyzer-agent` agent to orchestrate the full workflow automatically.

Usage:
- `/analyze <URL>` — analyze the given URL and generate a learning/analysis document
- `/analyze <URL> --format plan` — generate a learning plan
- `/analyze <URL> --format summary` — generate a content summary/analysis
