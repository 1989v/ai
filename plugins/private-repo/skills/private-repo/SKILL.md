---
name: private-repo
description: Separate directories from a public repo into private or public GitHub repos using git submodules. Controls visibility (public/private) per directory while keeping the monorepo structure intact. Responds to natural language like "make this private", "split into private repo", "separate as submodule".
argument-hint: [directory ...]
---

# Private Repo — Split Directories with Public/Private Visibility via Git Submodules

Separates directories from the current repository into independent GitHub repositories using git submodules, with explicit **public/private visibility control** per directory.

**Core concept**: A public monorepo can contain a mix of public and private submodules. Other users who clone the public repo will see the full project structure, but private submodule directories appear as empty folders — the private code is only accessible to authorized users.

```
my-project/              (public repo)
├── core/                (inline — visible to everyone)
├── docs/                (inline — visible to everyone)
├── feature-a/           (submodule → public repo — visible to everyone)
├── feature-b/           (submodule → private repo — empty folder for others)
└── my-ideas/            (submodule → private repo — empty folder for others)
```

## Trigger

- `/private-repo` — list eligible directories and choose
- `/private-repo my-service` — extract `my-service/` immediately
- `/private-repo dir1 dir2` — batch extract multiple directories
- Natural language: "make this private", "split into private repo", "separate as submodule", "move to private", "extract as public submodule"

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
- **History**: will be preserved if commits exist, otherwise fresh init

**Visibility selection** — Use AskUserQuestion:
- **Private (Recommended)**: only you (and collaborators) can access this repo. Other users who clone the parent repo will see an empty folder.
- **Public**: anyone can see and clone this submodule repo.

Use AskUserQuestion for repo name:
- Option 1: default name `{repo-name}-{directory}` (Recommended)
- Option 2: custom name

### 3. Create Repository

```bash
# --private or --public based on user's visibility choice
gh repo create {owner}/{repo-name} --{visibility} \
  --description "{directory} — submodule extracted from {current-repo}"
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
- Repo URL and visibility (public/private)
- Submodule status (`git submodule status`)
- Clone note: `git clone --recurse-submodules` required for full checkout
- **If private**: other users who clone the parent repo will see this directory as an empty folder. Only users with access to the private repo can pull the submodule contents.
- **If public**: all users can clone this submodule normally.

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
