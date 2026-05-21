#!/usr/bin/env bash
# hash-context.sh — Compute a stable SHA256 hash from layer inventory JSON.
#
# Usage: hash-context.sh <inventory.json>
#    or: echo '<inventory.json>' | hash-context.sh -
#
# Algorithm:
#   1. Parse paths from inventory JSON (sorted alphabetically for stability)
#   2. For each path, compute SHA256 of file content
#   3. Concatenate "<path>:<sha256>\n" lines in sorted order
#   4. SHA256 the concatenation, return hex digest

set -euo pipefail

INPUT="${1:-/dev/stdin}"
if [[ "$INPUT" == "-" ]]; then INPUT="/dev/stdin"; fi

# Extract paths from inventory JSON. Minimal parser — assumes one path field per line.
PATHS=$(grep -oE '"path":"[^"]+"' "$INPUT" 2>/dev/null \
  | sed 's/"path":"\(.*\)"/\1/' \
  | sed 's/\\\\/\\/g; s/\\"/"/g' \
  | sort -u)

if [[ -z "$PATHS" ]]; then
  # Empty inventory still yields stable hash for "empty"
  printf "empty" | shasum -a 256 | awk '{print $1}'
  exit 0
fi

# Build line-per-file digest then aggregate
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

while IFS= read -r p; do
  if [[ -f "$p" && -r "$p" ]]; then
    sha=$(shasum -a 256 "$p" | awk '{print $1}')
    echo "${p}:${sha}" >> "$TMP"
  else
    echo "${p}:missing" >> "$TMP"
  fi
done <<< "$PATHS"

shasum -a 256 "$TMP" | awk '{print $1}'
