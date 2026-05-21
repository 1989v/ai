#!/usr/bin/env bash
# collect-layers.sh — Enumerate Claude Code layered context files for given cwd.
#
# Usage: collect-layers.sh <cwd>
# Output: JSON array of { path, layer, bytes, modified, token_estimate }
#
# Token estimate uses heuristic: bytes/4 (rough English/Korean mix).

set -euo pipefail

CWD="${1:-$PWD}"
HOME_DIR="${HOME:-$(eval echo ~)}"

# Derive project slug like Claude Code does
# /Users/foo/IdeaProjects/msa  -> -Users-foo-IdeaProjects-msa
slug() {
  echo "${1}" | sed 's|/|-|g'
}

SLUG="$(slug "$CWD")"
PROJECT_DIR="${HOME_DIR}/.claude/projects/${SLUG}"

# Token estimate: bytes / 4
token_est() {
  local b="$1"
  echo $(( b / 4 ))
}

# Emit one JSON object for a file path with given layer label
emit() {
  local path="$1"
  local layer="$2"
  if [[ -f "$path" && -r "$path" ]]; then
    local bytes modified token
    bytes=$(stat -f %z "$path" 2>/dev/null || stat -c %s "$path" 2>/dev/null || echo 0)
    modified=$(stat -f "%Sm" -t "%Y-%m-%dT%H:%M:%SZ" "$path" 2>/dev/null || stat -c "%y" "$path" 2>/dev/null || echo "unknown")
    token=$(token_est "$bytes")
    # Escape path for JSON
    local esc_path esc_mod
    esc_path=$(printf '%s' "$path" | sed 's|\\|\\\\|g; s|"|\\"|g')
    esc_mod=$(printf '%s' "$modified" | sed 's|\\|\\\\|g; s|"|\\"|g')
    printf '  {"path":"%s","layer":"%s","bytes":%d,"modified":"%s","token_estimate":%d}' \
      "$esc_path" "$layer" "$bytes" "$esc_mod" "$token"
    return 0
  fi
  return 1
}

# Collect candidate paths
declare -a OUT=()

add_emission() {
  local out
  if out=$(emit "$1" "$2"); then
    OUT+=("$out")
  fi
}

# --- Global layer (user-level Claude Code config) ---
add_emission "${HOME_DIR}/.claude/CLAUDE.md" "global"
add_emission "${HOME_DIR}/.claude/settings.json" "global"

if [[ -d "${HOME_DIR}/.claude/memory" ]]; then
  while IFS= read -r -d '' f; do
    add_emission "$f" "global"
  done < <(find "${HOME_DIR}/.claude/memory" -maxdepth 1 -name "*.md" -print0 2>/dev/null)
fi

# --- User layer (Claude Code per-project memory store) ---
if [[ -d "$PROJECT_DIR" ]]; then
  add_emission "${PROJECT_DIR}/CLAUDE.md" "user"
  add_emission "${PROJECT_DIR}/settings.json" "user"
  add_emission "${PROJECT_DIR}/MEMORY.md" "user"
  if [[ -d "${PROJECT_DIR}/memory" ]]; then
    while IFS= read -r -d '' f; do
      add_emission "$f" "user"
    done < <(find "${PROJECT_DIR}/memory" -maxdepth 1 -name "*.md" -print0 2>/dev/null)
  fi
fi

# --- Project layer (repo root files) ---
add_emission "${CWD}/CLAUDE.md" "project"
add_emission "${CWD}/.claude/CLAUDE.md" "project"
add_emission "${CWD}/.claude/settings.json" "project"
add_emission "${CWD}/.claude/settings.local.json" "local"

# --- Parent chain up to home (in case nested working dir) ---
parent="$CWD"
while [[ "$parent" != "$HOME_DIR" && "$parent" != "/" ]]; do
  parent="$(dirname "$parent")"
  if [[ "$parent" == "$CWD" ]]; then break; fi
  add_emission "${parent}/CLAUDE.md" "ancestor"
  if [[ "$parent" == "$HOME_DIR" ]]; then break; fi
done

# --- Sub-service CLAUDE.md (up to 2 depth) ---
while IFS= read -r -d '' f; do
  add_emission "$f" "local"
done < <(find "$CWD" -mindepth 2 -maxdepth 3 -name "CLAUDE.md" -not -path "*/node_modules/*" -not -path "*/.git/*" -print0 2>/dev/null)

# Render JSON array
echo "["
for i in "${!OUT[@]}"; do
  if (( i < ${#OUT[@]} - 1 )); then
    echo "${OUT[$i]},"
  else
    echo "${OUT[$i]}"
  fi
done
echo "]"
