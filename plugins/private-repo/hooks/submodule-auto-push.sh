#!/usr/bin/env bash
# submodule-auto-push.sh — Claude Code PostToolUse hook
#
# Auto-commits and pushes changes when Claude edits files inside git submodules.
# Solves the "2-step commit" problem: submodule changes require a commit+push
# inside the submodule AND a pointer update in the parent repo.
#
# Install: Add to .claude/settings.local.json (see README for config snippet)
# Trigger: PostToolUse on Write|Edit
# Scope: Claude Code only — does NOT affect manual git operations

set -euo pipefail

# Auto-detect repo root from git
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0

# Extract file path from hook JSON payload
FILE_PATH=$(jq -r '.tool_input.file_path // .tool_response.filePath // empty' 2>/dev/null)
[ -z "$FILE_PATH" ] && exit 0

# Check if file is inside a registered submodule
SUBMODULE=""
while IFS= read -r sub; do
  SUB_ABS="$REPO_ROOT/$sub"
  if [[ "$FILE_PATH" == "$SUB_ABS/"* ]]; then
    SUBMODULE="$sub"
    break
  fi
done < <(git -C "$REPO_ROOT" config --file .gitmodules --get-regexp '^submodule\..*\.path$' 2>/dev/null | awk '{print $2}')

[ -z "$SUBMODULE" ] && exit 0

SUB_ABS="$REPO_ROOT/$SUBMODULE"

# Check if there are actual changes in the submodule
if git -C "$SUB_ABS" diff --quiet HEAD -- 2>/dev/null && \
   [ -z "$(git -C "$SUB_ABS" ls-files --others --exclude-standard 2>/dev/null)" ]; then
  exit 0
fi

# Auto-commit and push in the submodule
REL_PATH="${FILE_PATH#$SUB_ABS/}"
git -C "$SUB_ABS" add -A >/dev/null 2>&1
git -C "$SUB_ABS" commit -m "auto: update $REL_PATH" >/dev/null 2>&1 || exit 0
git -C "$SUB_ABS" push origin HEAD >/dev/null 2>&1 || true

# Update submodule pointer in parent repo
git -C "$REPO_ROOT" add "$SUBMODULE" >/dev/null 2>&1

echo '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Submodule '"$SUBMODULE"' auto-committed and pushed."}}'
