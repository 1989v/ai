#!/usr/bin/env bash
# cma-snapshot.sh — Hook script that captures layered context snapshot.
#
# Designed to be wired into Claude Code's SessionStart and (optionally) PreToolUse hooks.
# On each invocation it captures the current inventory + hash and appends a timestamped
# snapshot to ~/.claude/projects/{slug}/cma-snapshots/.
#
# Usage (from settings.json hook config):
#   {"command": "${CLAUDE_PLUGIN_ROOT}/hooks/cma-snapshot.sh", "event": "SessionStart"}
#
# Args:
#   --event=<name>   (optional) event label to embed in snapshot (default: "unknown")
#   --cwd=<path>     (optional) override working directory (default: $PWD)
#
# Output: writes JSON snapshot to disk; prints snapshot path to stdout.
# Failures are non-fatal (always exit 0) to avoid breaking Claude Code sessions.

set -uo pipefail

EVENT="unknown"
CWD="$PWD"
for arg in "$@"; do
  case "$arg" in
    --event=*) EVENT="${arg#--event=}" ;;
    --cwd=*)   CWD="${arg#--cwd=}" ;;
  esac
done

# Resolve script's own directory to find sibling scripts/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
COLLECT="${PLUGIN_ROOT}/scripts/collect-layers.sh"
HASH="${PLUGIN_ROOT}/scripts/hash-context.sh"

if [[ ! -x "$COLLECT" || ! -x "$HASH" ]]; then
  exit 0  # plugin not properly installed — silent skip
fi

# Slug derivation matches collect-layers.sh
SLUG="$(echo "$CWD" | sed 's|/|-|g')"
SNAP_DIR="${HOME}/.claude/projects/${SLUG}/cma-snapshots"
mkdir -p "$SNAP_DIR" 2>/dev/null || exit 0

TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
INV_FILE="${SNAP_DIR}/${TIMESTAMP}-${EVENT}.json"

# Capture inventory
INVENTORY=$("$COLLECT" "$CWD" 2>/dev/null) || exit 0

# Compute hash
HASH_HEX=$(echo "$INVENTORY" | "$HASH" - 2>/dev/null) || HASH_HEX="unknown"

# Wrap in snapshot envelope
cat > "$INV_FILE" <<EOF
{
  "event": "${EVENT}",
  "timestamp": "${TIMESTAMP}",
  "cwd": "${CWD}",
  "context_hash": "${HASH_HEX}",
  "inventory": ${INVENTORY}
}
EOF

# Retention: keep last 50 snapshots per project (FIFO trim)
SNAPS=$(ls -1t "$SNAP_DIR"/*.json 2>/dev/null)
COUNT=$(echo "$SNAPS" | wc -l | tr -d ' ')
if (( COUNT > 50 )); then
  echo "$SNAPS" | tail -n +51 | xargs rm -f 2>/dev/null || true
fi

echo "$INV_FILE"
exit 0
