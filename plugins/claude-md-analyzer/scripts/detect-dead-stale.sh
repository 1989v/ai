#!/usr/bin/env bash
# detect-dead-stale.sh — Tag rules with Dead/Stale flags based on static heuristics.
#
# Usage: detect-dead-stale.sh <rules.json> <cwd>
# Output: rules.json with extra fields per rule:
#   - stale_reason: "path-missing" | "line-out-of-range" | null
#   - dead_reason:  "path-bound-irrelevant" | "permanently-overridden" | null
#
# The `unreferenced` heuristic requires keyword extraction and grep — that part is
# orchestrated by the analyze command via the introspect adapter, not here.

set -euo pipefail

RULES_PATH="${1:-}"
CWD="${2:-$PWD}"

if [[ -z "$RULES_PATH" || ! -f "$RULES_PATH" ]]; then
  echo "usage: detect-dead-stale.sh <rules.json> <cwd>" >&2
  exit 64
fi

# Helper: is `child` a sub-path of `parent`?
is_subpath() {
  local parent="$1"
  local child="$2"
  # Normalize trailing slash
  parent="${parent%/}"
  child="${child%/}"
  [[ "$child" == "$parent"* ]]
}

# Walk rules array — minimal JSON-text rewrite via line-anchored sed.
# We assume the JSON was produced by our pipeline (one rule per line block).

# For each "source" line, derive flags and inject them after.
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

python3 - "$RULES_PATH" "$CWD" > "$TMP" <<'PY'
import json, os, sys

rules_path = sys.argv[1]
cwd = os.path.abspath(sys.argv[2])

with open(rules_path) as f:
    data = json.load(f)

def tag_rule(rule):
    stale = None
    dead = None

    # Pick the "primary" source — winner if present, else first source field
    src = rule.get("winner") or {}
    src_path = src.get("source", "")

    if ":" in src_path:
        path_part, line_part = src_path.rsplit(":", 1)
        line_part = line_part.split("-")[0]
        # Stale: file missing
        if path_part and not os.path.isfile(path_part):
            stale = "path-missing"
        else:
            try:
                ln = int(line_part)
                if path_part:
                    with open(path_part, "r", errors="ignore") as f:
                        total = sum(1 for _ in f)
                    if ln < 1 or ln > total:
                        stale = "line-out-of-range"
            except (ValueError, OSError):
                pass

        # Dead: path-bound-irrelevant
        # Rule source is under a sub-directory not in cwd's tree.
        # If the source is a service-level CLAUDE.md (e.g., /repo/order/CLAUDE.md)
        # and cwd is /repo/product/, mark as path-bound-irrelevant.
        if path_part and "/CLAUDE.md" in path_part:
            src_dir = os.path.dirname(path_part)
            # If src_dir is NOT an ancestor of cwd AND not the cwd itself
            # AND src_dir is itself a descendant of some common ancestor with cwd
            # → likely path-bound-irrelevant
            if src_dir and not (cwd == src_dir or cwd.startswith(src_dir.rstrip("/") + "/")):
                # exclude global/user layers which are outside the project tree
                layer = src.get("layer") or rule.get("layer", "")
                if layer in ("local", "project"):
                    # local CLAUDE.md outside of cwd's tree
                    dead = "path-bound-irrelevant"

    # Dead: permanently-overridden
    # Simplified: rule is Overridden AND winner is at a higher layer that
    # always wins regardless of cwd (project/local layer beats global/user).
    if rule.get("status") == "Overridden":
        winner_layer = (rule.get("winner") or {}).get("layer", "")
        loser_layer  = (rule.get("loser")  or {}).get("layer", "")
        # Global rule overridden by project/local at root level → permanently dead
        # unless user moves cwd outside the project tree (rare).
        if loser_layer == "global" and winner_layer in ("project", "local"):
            # Only mark as permanently-overridden if the same rule has no
            # exception clause (heuristic: shorter rules with absolute language).
            text = (rule.get("loser") or {}).get("text", "").lower()
            if any(kw in text for kw in ("반드시", "필수", "always", "never", "must", "금지")):
                dead = dead or "permanently-overridden"

    rule["stale_reason"] = stale
    rule["dead_reason"] = dead
    return rule

if isinstance(data, dict) and "rules" in data:
    data["rules"] = [tag_rule(r) for r in data["rules"]]
    # Bump summary
    summary = data.setdefault("summary", {})
    summary["stale"] = sum(1 for r in data["rules"] if r.get("stale_reason"))
    summary["dead"]  = sum(1 for r in data["rules"] if r.get("dead_reason"))
    print(json.dumps(data, ensure_ascii=False, indent=2))
elif isinstance(data, list):
    print(json.dumps([tag_rule(r) for r in data], ensure_ascii=False, indent=2))
else:
    print(json.dumps(data, ensure_ascii=False, indent=2))
PY

cat "$TMP"
