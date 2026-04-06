#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# parallel-work.sh - Git worktree management for parallel task execution
# =============================================================================

# Auto-detect project root and name
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: Not inside a git repository" >&2
  exit 1
}
PROJECT_NAME="$(basename "$PROJECT_ROOT")"

DEFAULT_BASE_BRANCH="main"

# -----------------------------------------------------------------------------
# Usage
# -----------------------------------------------------------------------------
usage() {
  cat <<USAGE
Usage: $(basename "$0") <command> [options]

Commands:
  create <task-name> [base-branch]  Create worktree with feature/<task-name> branch
                                     Default base: $DEFAULT_BASE_BRANCH
  list                               Show all active worktrees
  status                             Display git status for each worktree
  remove <task-name>                 Remove worktree and optionally delete branch
  cleanup                            Prune stale worktree references

Examples:
  $(basename "$0") create payment-api
  $(basename "$0") create payment-api develop
  $(basename "$0") status
  $(basename "$0") remove payment-api
USAGE
}

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
worktree_path() {
  local task_name="$1"
  echo "${PROJECT_ROOT}/../${PROJECT_NAME}-${task_name}"
}

branch_name() {
  local task_name="$1"
  echo "feature/${task_name}"
}

# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------

cmd_create() {
  local task_name="${1:?Error: task-name is required}"
  local base_branch="${2:-$DEFAULT_BASE_BRANCH}"
  local wt_path
  wt_path="$(worktree_path "$task_name")"
  local br
  br="$(branch_name "$task_name")"

  # Safety: check if worktree already exists
  if [ -d "$wt_path" ]; then
    echo "Error: Worktree already exists at $wt_path" >&2
    exit 1
  fi

  # Safety: check if branch already exists
  if git show-ref --verify --quiet "refs/heads/$br"; then
    echo "Warning: Branch '$br' already exists. Using existing branch."
    git worktree add "$wt_path" "$br"
  else
    # Ensure base branch is up to date
    echo "Fetching latest '$base_branch'..."
    git fetch origin "$base_branch" 2>/dev/null || true

    echo "Creating worktree at $wt_path with branch $br (from $base_branch)..."
    git worktree add -b "$br" "$wt_path" "origin/$base_branch" 2>/dev/null || \
      git worktree add -b "$br" "$wt_path" "$base_branch"
  fi

  echo ""
  echo "Worktree created successfully:"
  echo "  Path:   $wt_path"
  echo "  Branch: $br"
  echo ""
  echo "To start working:"
  echo "  cd $wt_path"
}

cmd_list() {
  echo "Active worktrees for '$PROJECT_NAME':"
  echo "---"
  git worktree list
}

cmd_status() {
  echo "Status for all worktrees:"
  echo "==="

  git worktree list --porcelain | grep "^worktree " | sed 's/^worktree //' | while read -r wt; do
    echo ""
    echo "--- $wt ---"

    # Show current branch
    local current_branch
    current_branch="$(git -C "$wt" branch --show-current 2>/dev/null || echo "(detached)")"
    echo "Branch: $current_branch"

    # Show status summary
    local changes
    changes="$(git -C "$wt" status --short 2>/dev/null)"
    if [ -z "$changes" ]; then
      echo "Status: Clean"
    else
      echo "Status:"
      echo "$changes" | sed 's/^/  /'
    fi
  done
}

cmd_remove() {
  local task_name="${1:?Error: task-name is required}"
  local wt_path
  wt_path="$(worktree_path "$task_name")"
  local br
  br="$(branch_name "$task_name")"

  if [ ! -d "$wt_path" ]; then
    echo "Error: Worktree not found at $wt_path" >&2
    exit 1
  fi

  # Safety: check for uncommitted changes
  local changes
  changes="$(git -C "$wt_path" status --short 2>/dev/null)"
  if [ -n "$changes" ]; then
    echo "Warning: Uncommitted changes in $wt_path:"
    echo "$changes" | sed 's/^/  /'
    echo ""
    read -r -p "Continue removing worktree? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
      echo "Aborted."
      exit 0
    fi
  fi

  echo "Removing worktree at $wt_path..."
  git worktree remove "$wt_path" --force

  # Ask about branch deletion
  if git show-ref --verify --quiet "refs/heads/$br"; then
    read -r -p "Delete branch '$br'? (y/N): " delete_branch
    if [[ "$delete_branch" =~ ^[Yy]$ ]]; then
      git branch -D "$br"
      echo "Branch '$br' deleted."
    else
      echo "Branch '$br' kept."
    fi
  fi

  echo "Worktree removed."
}

cmd_cleanup() {
  echo "Pruning stale worktree references..."
  git worktree prune -v
  echo "Done."
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
case "${1:-}" in
  create)   shift; cmd_create "$@" ;;
  list)     cmd_list ;;
  status)   cmd_status ;;
  remove)   shift; cmd_remove "$@" ;;
  cleanup)  cmd_cleanup ;;
  -h|--help|help|"")
    usage
    ;;
  *)
    echo "Error: Unknown command '$1'" >&2
    usage
    exit 1
    ;;
esac
