---
name: private-repo
description: "Extract directories into private GitHub repos as git submodules"
---

# /private-repo

Use the `private-repo:private-repo` skill to handle this request.

Follow that skill exactly:
- identify eligible directories in the current repo
- confirm target directory, repo name, and GitHub account with the user
- create private GitHub repo via `gh` CLI
- extract directory with history preservation when possible
- replace directory with git submodule
- commit and report results
