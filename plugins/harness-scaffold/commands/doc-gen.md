---
name: doc-gen
description: "Generate CLAUDE.md and docs/ tree for the current project"
requires:
  - agent-os/product/tech-stack.md
auto_reference: false
---

# /hns:doc-gen

## Purpose
프로젝트에 CLAUDE.md와 docs/ 트리를 생성한다.

## Required Inputs
- Access to project root directory

## Expected Outputs
- CLAUDE.md
- docs/ directory tree

---

Delegate to `hns:doc-gen-agent` with `hns:doc-gen` skill loaded.
