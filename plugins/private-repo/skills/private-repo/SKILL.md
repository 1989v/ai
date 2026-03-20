---
name: private-repo
description: Extract directories into private GitHub repos as git submodules. Handles repo creation, history preservation, and submodule replacement. Responds to natural language like "make this private", "split into private repo", "separate as submodule".
argument-hint: [directory ...]
---

# Private Repo — Extract Directory as Private Git Submodule

Extracts one or more directories from the current repository into separate private GitHub repositories, replacing them with git submodules. Preserves git history when available.

## Trigger

- `/private-repo` — list eligible directories and choose
- `/private-repo my-service` — extract `my-service/` immediately
- `/private-repo dir1 dir2` — batch extract multiple directories
- Natural language: "make this private", "split into private repo", "separate as submodule", "move to private", "extract as private"

## Prerequisites

- `gh` CLI authenticated (`gh auth status`)
- Current directory is a git repository with a remote
- GitHub account has repo creation permission

## Execution Steps

### 1. Identify Target Directories

1. List top-level directories in the repo root
2. Exclude directories already registered as submodules (parse `.gitmodules`)
3. Exclude common non-candidate directories: `.git`, `.github`, `.claude`, `node_modules`, `build`, `dist`, `out`, `.gradle`, `.venv`, `venv`

- **Argument provided**: validate directory exists, then proceed
- **No argument**: display eligible directories with status and let user choose

```
| # | Directory      | Git History   | Status         |
|---|---------------|---------------|----------------|
| 1 | my-service/   | 12 commits    | Extractable    |
| 2 | my-idea/      | untracked     | Extractable    |
| 3 | lib-internal/ | 5 commits     | Extractable    |
```

Use AskUserQuestion to let the user select.

### 2. Confirm Details

Before proceeding, display and confirm:

- **Target directory**: name and file count
- **GitHub account**: detected via `gh api user --jq '.login'`
- **Repo name**: default `{current-repo-name}-{directory}`, customizable
- **Visibility**: private (default)
- **History**: will be preserved if commits exist, otherwise fresh init

Use AskUserQuestion for repo name:
- Option 1: default name `{repo-name}-{directory}` (Recommended)
- Option 2: custom name

### 3. Create Private Repository

```bash
gh repo create {owner}/{repo-name} --private \
  --description "{directory} — private submodule extracted from {current-repo}"
```

### 4. Extract and Push

**If git history exists** (directory has commits in `git log`):

```bash
# Extract directory history into a temporary branch
git subtree split -P {directory} -b split-{directory}

# Push to new repo from temp location
cd /tmp && mkdir {repo-name} && cd {repo-name}
git init && git pull {original-repo-path} split-{directory}
git remote add origin https://github.com/{owner}/{repo-name}.git
git branch -M main && git push -u origin main

# Cleanup
cd {original-repo-path}
git branch -D split-{directory}
rm -rf /tmp/{repo-name}
```

**If no git history** (untracked or gitignored):

```bash
cd /tmp && mkdir {repo-name} && cd {repo-name}
git init
cp -r {original-repo-path}/{directory}/* .
cp -r {original-repo-path}/{directory}/.* . 2>/dev/null
git add -A && git commit -m "initial: extract {directory}"
git remote add origin https://github.com/{owner}/{repo-name}.git
git branch -M main && git push -u origin main

cd {original-repo-path}
rm -rf /tmp/{repo-name}
```

### 5. Replace with Submodule

```bash
# Remove from git tracking and filesystem
git rm -r --cached {directory} 2>/dev/null
rm -rf {directory}

# Remove from .gitignore if present (use Edit tool)

# Add as submodule
git submodule add https://github.com/{owner}/{repo-name}.git {directory}
```

### 6. Commit and Report

```bash
git add .gitignore .gitmodules {directory}
git commit -m "chore: extract {directory} as private submodule → {owner}/{repo-name}"
```

Report to user:
- Private repo URL
- Submodule status (`git submodule status`)
- Clone note: `git clone --recurse-submodules` required for full checkout
- Access note: collaborators need repo access to clone private submodules

## Batch Processing

When multiple directories are given (`/private-repo dir1 dir2 dir3`):
- Run steps 2–6 sequentially for each directory
- Single summary at the end with all created repos

## Undo Instructions

If the user wants to reverse the extraction:

```bash
# Remove submodule
git submodule deinit -f {directory}
git rm -f {directory}
rm -rf .git/modules/{directory}

# Restore as regular directory
git clone https://github.com/{owner}/{repo-name}.git {directory}
rm -rf {directory}/.git
git add {directory}
git commit -m "chore: inline {directory} back from submodule"
```

## Error Handling

| Scenario | Action |
|----------|--------|
| `gh auth status` fails | Prompt `gh auth login` |
| Repo name already exists | Ask to use existing or pick new name |
| `subtree split` fails | Fall back to no-history extraction |
| `submodule add` fails (residual files) | Clean `.git/modules/{dir}` and retry |
| No directories eligible | Inform user all dirs are already submodules or excluded |
| Push fails (auth) | Run `gh auth setup-git` and retry |
