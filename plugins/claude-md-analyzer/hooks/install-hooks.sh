#!/usr/bin/env bash
# install-hooks.sh — Idempotently register cma-snapshot.sh into user's Claude Code settings.
#
# Usage:
#   install-hooks.sh [--scope=user|project] [--events=SessionStart,PreToolUse] [--dry-run]
#
# scope=user    → ~/.claude/settings.json        (default)
# scope=project → {cwd}/.claude/settings.json
#
# This script is opt-in. Users should invoke it explicitly (e.g. via README guidance);
# the plugin does NOT auto-install hooks.

set -euo pipefail

SCOPE="user"
EVENTS="SessionStart"
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --scope=*)  SCOPE="${arg#--scope=}" ;;
    --events=*) EVENTS="${arg#--events=}" ;;
    --dry-run)  DRY_RUN=1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_PATH="${SCRIPT_DIR}/cma-snapshot.sh"

if [[ ! -x "$HOOK_PATH" ]]; then
  echo "❌ hook script not found or not executable: $HOOK_PATH" >&2
  exit 1
fi

case "$SCOPE" in
  user)    TARGET="${HOME}/.claude/settings.json" ;;
  project) TARGET="$PWD/.claude/settings.json" ;;
  *)       echo "❌ invalid --scope: $SCOPE" >&2; exit 64 ;;
esac

mkdir -p "$(dirname "$TARGET")"
if [[ ! -f "$TARGET" ]]; then
  echo "{}" > "$TARGET"
fi

# Merge hook config via Python (jq dependency optional)
python3 - "$TARGET" "$HOOK_PATH" "$EVENTS" "$DRY_RUN" <<'PY'
import json, sys

target, hook_path, events, dry_run = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == "1"

with open(target) as f:
    try:
        cfg = json.load(f)
    except json.JSONDecodeError:
        cfg = {}

hooks = cfg.setdefault("hooks", {})
event_list = [e.strip() for e in events.split(",") if e.strip()]

# Claude Code settings.json hooks schema (simplified):
# "hooks": {
#   "<EventName>": [
#     {"command": "...", "matcher": "optional"},
#     ...
#   ]
# }
added = []
for ev in event_list:
    bucket = hooks.setdefault(ev, [])
    # Idempotency: skip if our hook is already present
    already = any(
        isinstance(h, dict) and h.get("command", "").startswith(hook_path)
        for h in bucket
    )
    if already:
        continue
    entry = {
        "command": f'{hook_path} --event={ev}',
        "matcher": "*"
    }
    bucket.append(entry)
    added.append(ev)

if dry_run:
    print("--- dry-run (no write) ---")
    print(json.dumps(cfg, indent=2, ensure_ascii=False))
    sys.exit(0)

if not added:
    print(f"✓ no changes — hook already registered for: {', '.join(event_list)}")
    sys.exit(0)

with open(target, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"✓ registered hook in {target}")
print(f"  events: {', '.join(added)}")
print(f"  command: {hook_path}")
PY

echo ""
echo "→ Test with: claude --start (or restart your Claude Code session)"
echo "→ Inspect snapshots: ls ~/.claude/projects/*/cma-snapshots/"
