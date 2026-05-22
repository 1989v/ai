#!/usr/bin/env bash
#
# fork-and-invoke.sh — copy source-skill, inject overlay, invoke via `claude --plugin-dir`
#
# Usage:
#   fork-and-invoke.sh \
#     --skill-id hns-glossary \
#     --snapshot-dir /path/to/snapshots/2026-05-22-baseline \
#     --case-id case-001 \
#     --source-skill-dir /path/to/original/skill \
#     --schema /path/to/output.schema.json \
#     --input /path/to/input.yml \
#     [--model haiku] \
#     [--max-budget-usd 0.50] \
#     [--retry 2]
#
# Behavior:
#   1. Copy source-skill-dir → {snapshot-dir}/source-skill/
#   2. Read overlay template, substitute variables, append to forked SKILL.md
#   3. Materialize a minimal plugin layout at a tmp dir
#   4. Invoke: claude -p --plugin-dir <tmp> --json-schema <schema> --append-system-prompt <overlay> "<input>"
#   5. Extract response.structured_output → write to actual.json (or expected.json for baseline)
#   6. Retry on schema failure up to --retry times
#   7. Print path of output JSON on success, exit non-zero on terminal failure

set -euo pipefail

# ───── arg parse ─────
SKILL_ID=""; SNAPSHOT_DIR=""; CASE_ID=""
SOURCE_SKILL_DIR=""; SCHEMA=""; INPUT=""
MODEL="opus"
MAX_BUDGET_USD="1.00"
RETRY="2"
OUTPUT_KIND="actual"  # actual | expected (baseline)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill-id) SKILL_ID="$2"; shift 2 ;;
    --snapshot-dir) SNAPSHOT_DIR="$2"; shift 2 ;;
    --case-id) CASE_ID="$2"; shift 2 ;;
    --source-skill-dir) SOURCE_SKILL_DIR="$2"; shift 2 ;;
    --schema) SCHEMA="$2"; shift 2 ;;
    --input) INPUT="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --max-budget-usd) MAX_BUDGET_USD="$2"; shift 2 ;;
    --retry) RETRY="$2"; shift 2 ;;
    --output-kind) OUTPUT_KIND="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

for v in SKILL_ID SNAPSHOT_DIR CASE_ID SOURCE_SKILL_DIR SCHEMA INPUT; do
  if [[ -z "${!v}" ]]; then
    echo "missing required: --${v,,}" >&2
    exit 64
  fi
done

command -v claude >/dev/null || { echo "claude CLI not found" >&2; exit 69; }
command -v jq >/dev/null || { echo "jq not found" >&2; exit 69; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OVERLAY_TEMPLATE="$PLUGIN_ROOT/references/overlay-template.md"

[[ -f "$OVERLAY_TEMPLATE" ]] || { echo "overlay template missing: $OVERLAY_TEMPLATE" >&2; exit 70; }
[[ -d "$SOURCE_SKILL_DIR" ]] || { echo "source-skill-dir not found: $SOURCE_SKILL_DIR" >&2; exit 66; }
[[ -f "$SCHEMA" ]] || { echo "schema not found: $SCHEMA" >&2; exit 66; }
[[ -f "$INPUT" ]] || { echo "input not found: $INPUT" >&2; exit 66; }

SNAPSHOT_ID="$(basename "$SNAPSHOT_DIR")"
SOURCE_DST="$SNAPSHOT_DIR/source-skill"
FORK_DST="$SNAPSHOT_DIR/forked-skill"
CASE_DIR="$SNAPSHOT_DIR/cases/$CASE_ID"

mkdir -p "$SOURCE_DST" "$FORK_DST" "$CASE_DIR"

# ───── 1) copy source-skill ─────
rsync -a --delete "$SOURCE_SKILL_DIR/" "$SOURCE_DST/"

# ───── 2) build forked SKILL.md ─────
SOURCE_SKILL_MD=""
for cand in "$SOURCE_DST/SKILL.md" "$SOURCE_DST"/*/SKILL.md; do
  [[ -f "$cand" ]] && { SOURCE_SKILL_MD="$cand"; break; }
done
[[ -n "$SOURCE_SKILL_MD" ]] || { echo "no SKILL.md found under $SOURCE_DST" >&2; exit 66; }

# Determine forked skill subdir name (mirror source structure)
SOURCE_REL="${SOURCE_SKILL_MD#$SOURCE_DST/}"
FORK_SKILL_MD="$FORK_DST/$SOURCE_REL"
mkdir -p "$(dirname "$FORK_SKILL_MD")"

# Copy entire source-skill content into fork (preserve refs/scripts etc.)
rsync -a --delete "$SOURCE_DST/" "$FORK_DST/"

# Build overlay body from template:
#   1) extract between <!-- OVERLAY_BEGIN --> / <!-- OVERLAY_END --> sentinels
#   2) substitute {{SKILL_ID}}, {{SNAPSHOT_ID}}, {{CASE_ID}}
#   3) substitute {{OUTPUT_SCHEMA_JSON}} line by line, reading schema from a temp file
SCHEMA_TMP="$(mktemp -t skill-eval-schema-XXXXXX)"
OVERLAY_TMP="$(mktemp -t skill-eval-overlay-XXXXXX)"
trap 'rm -f "$SCHEMA_TMP" "$OVERLAY_TMP"; rm -rf "${TMP_PLUGIN:-}"' EXIT
jq . "$SCHEMA" > "$SCHEMA_TMP"

sed -n '/<!-- OVERLAY_BEGIN -->/,/<!-- OVERLAY_END -->/p' "$OVERLAY_TEMPLATE" \
  | grep -v '<!-- OVERLAY_\(BEGIN\|END\) -->' \
  | sed -e "s|{{SKILL_ID}}|$SKILL_ID|g" \
        -e "s|{{SNAPSHOT_ID}}|$SNAPSHOT_ID|g" \
        -e "s|{{CASE_ID}}|$CASE_ID|g" \
  > "$OVERLAY_TMP"

{
  cat "$FORK_SKILL_MD"
  printf '\n\n'
  while IFS= read -r line; do
    if [[ "$line" == *"{{OUTPUT_SCHEMA_JSON}}"* ]]; then
      cat "$SCHEMA_TMP"
    else
      printf '%s\n' "$line"
    fi
  done < "$OVERLAY_TMP"
} > "$FORK_SKILL_MD.tmp"
mv "$FORK_SKILL_MD.tmp" "$FORK_SKILL_MD"
SCHEMA_PRETTY="$(cat "$SCHEMA_TMP")"

# ───── 3) materialize a minimal plugin layout in tmp ─────
FORK_PLUGIN_NAME="skill-eval-fork-$(echo "$SKILL_ID" | tr '/:' '-')"
TMP_PLUGIN="$(mktemp -d -t skill-eval-XXXXXX)"
mkdir -p "$TMP_PLUGIN/.claude-plugin" "$TMP_PLUGIN/skills"

cat > "$TMP_PLUGIN/.claude-plugin/plugin.json" <<EOF
{
  "name": "$FORK_PLUGIN_NAME",
  "version": "0.0.0",
  "description": "Ephemeral fork plugin for skill-quality-eval. Auto-cleaned after invoke.",
  "author": { "name": "skill-quality-eval" }
}
EOF

# Copy fork skill content under skills/ subdir
# Source structure: fork-dst/SKILL.md OR fork-dst/{name}/SKILL.md
FORK_SKILL_NAME="$(basename "$(dirname "$FORK_SKILL_MD")")"
if [[ "$FORK_SKILL_NAME" = "forked-skill" ]]; then
  # Flat layout — SKILL.md at fork-dst root
  FORK_SKILL_NAME="$(echo "$SKILL_ID" | tr '/:' '-')"
fi
mkdir -p "$TMP_PLUGIN/skills/$FORK_SKILL_NAME"
rsync -a "$FORK_DST/" "$TMP_PLUGIN/skills/$FORK_SKILL_NAME/"
# If SKILL.md is at the fork-dst root, move it under the named dir
if [[ -f "$TMP_PLUGIN/skills/$FORK_SKILL_NAME/$FORK_SKILL_NAME/SKILL.md" ]]; then
  : # already nested
elif [[ -f "$TMP_PLUGIN/skills/$FORK_SKILL_NAME/SKILL.md" ]]; then
  : # already at expected level
fi

# cleanup handled by the consolidated trap above (covers SCHEMA_TMP, OVERLAY_TMP, TMP_PLUGIN)

# ───── 4) build invoke prompt ─────
INPUT_BODY="$(cat "$INPUT")"
PROMPT="Invoke the ${FORK_PLUGIN_NAME}:${FORK_SKILL_NAME} skill with the following input. Output the schema-conforming JSON only, nothing else.

INPUT:
${INPUT_BODY}"

# ───── 5) invoke with retries ─────
OUTPUT_FILE="$CASE_DIR/${OUTPUT_KIND}.json"
RAW_LOG="$CASE_DIR/.invoke-raw.json"

attempt=0
while (( attempt <= RETRY )); do
  attempt=$((attempt + 1))
  echo "[skill-quality-eval] attempt $attempt/$((RETRY + 1)) — invoking $FORK_PLUGIN_NAME:$FORK_SKILL_NAME" >&2

  if claude -p \
       --plugin-dir "$TMP_PLUGIN" \
       --model "$MODEL" \
       --output-format json \
       --json-schema "$SCHEMA_PRETTY" \
       --max-budget-usd "$MAX_BUDGET_USD" \
       --no-session-persistence \
       "$PROMPT" > "$RAW_LOG" 2>/dev/null
  then
    # Extract structured_output
    if jq -e '.structured_output' "$RAW_LOG" >/dev/null 2>&1; then
      jq '.structured_output' "$RAW_LOG" > "$OUTPUT_FILE"
      echo "[skill-quality-eval] success → $OUTPUT_FILE" >&2
      echo "$OUTPUT_FILE"
      exit 0
    fi

    # Fallback: parse .result as JSON (extractor stage)
    if jq -e '.result' "$RAW_LOG" >/dev/null 2>&1; then
      result_str="$(jq -r '.result' "$RAW_LOG")"
      # Try direct parse, then strip code fences
      if echo "$result_str" | jq -e . >/dev/null 2>&1; then
        echo "$result_str" | jq . > "$OUTPUT_FILE"
        echo "[skill-quality-eval] success (via .result parse) → $OUTPUT_FILE" >&2
        echo "$OUTPUT_FILE"
        exit 0
      fi
      stripped="$(echo "$result_str" | sed -n 's/^```\(json\)\{0,1\}$//; /./,$p' | sed -e 's/```$//')"
      if echo "$stripped" | jq -e . >/dev/null 2>&1; then
        echo "$stripped" | jq . > "$OUTPUT_FILE"
        echo "[skill-quality-eval] success (via fenced extract) → $OUTPUT_FILE" >&2
        echo "$OUTPUT_FILE"
        exit 0
      fi
    fi
  fi

  echo "[skill-quality-eval] attempt $attempt failed; raw log preserved at $RAW_LOG" >&2
done

echo "[skill-quality-eval] terminal failure after $((RETRY + 1)) attempts; case marked format-fail" >&2
echo "format-fail" > "$CASE_DIR/.format-fail"
exit 1
