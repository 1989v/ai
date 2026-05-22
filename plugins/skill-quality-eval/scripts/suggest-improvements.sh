#!/usr/bin/env bash
#
# suggest-improvements.sh — given a regression snapshot, propose concrete
#   edits to the source SKILL.md that would likely close the gap.
#
# The Phase-2 piece of the eval loop: measurement (run.md) → diagnosis
# (diff-vs-baseline) → **suggestion (this script)** → human applies edits →
# rerun.
#
# Input:
#   --snapshot-dir <path>      # the "after-fix" snapshot dir (the one with regressions)
#   --baseline-dir  <path>     # the baseline that snapshot is being compared against
#   [--model opus]             # opus default — suggester benefits from larger model
#   [--max-budget-usd 1.00]
#
# Output:
#   Writes {snapshot-dir}/suggestions.md and prints its path on stdout.
#   suggestions.md contains:
#     - top-K regression themes (clusters of similar diffs)
#     - per-theme: specific edit proposal referencing SKILL.md sections
#     - confidence + risk note

set -euo pipefail

SNAP_DIR=""; BASE_DIR=""
MODEL="opus"
MAX_BUDGET_USD="1.00"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --snapshot-dir) SNAP_DIR="$2"; shift 2 ;;
    --baseline-dir) BASE_DIR="$2"; shift 2 ;;
    --model)        MODEL="$2"; shift 2 ;;
    --max-budget-usd) MAX_BUDGET_USD="$2"; shift 2 ;;
    -h|--help) sed -n '3,25p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

[[ -d "$SNAP_DIR" ]] || { echo "snapshot dir not found: $SNAP_DIR" >&2; exit 65; }
[[ -d "$BASE_DIR" ]] || { echo "baseline dir not found: $BASE_DIR" >&2; exit 65; }
command -v claude >/dev/null || { echo "claude CLI not found" >&2; exit 69; }

# ─── Collect inputs ───────────────────────────────────────────────────
# Current SKILL.md (the "after-fix" version that produced regressions)
SOURCE_SKILL_MD=""
for cand in "$SNAP_DIR/source-skill/SKILL.md" "$SNAP_DIR/source-skill"/*/SKILL.md; do
  [[ -f "$cand" ]] && { SOURCE_SKILL_MD="$cand"; break; }
done
[[ -n "$SOURCE_SKILL_MD" ]] || { echo "no source SKILL.md found under $SNAP_DIR/source-skill/" >&2; exit 66; }

# Gather all match-*.json showing fails (across all cases in snapshot)
TMP_DIFFS="$(mktemp -t skill-eval-sugg-diffs-XXXXXX)"
TMP_PROMPT="$(mktemp -t skill-eval-sugg-prompt-XXXXXX)"
trap 'rm -f "$TMP_DIFFS" "$TMP_PROMPT"' EXIT

REGRESSION_COUNT=0
{
  echo "["
  first=1
  for case_dir in "$SNAP_DIR"/cases/*/; do
    [[ -d "$case_dir" ]] || continue
    case_id="$(basename "$case_dir")"
    for match_file in "$case_dir"/match-*.json; do
      [[ -f "$match_file" ]] || continue
      if jq -e '.result == "fail"' "$match_file" >/dev/null 2>&1; then
        [[ $first -eq 1 ]] || echo ","
        jq -c --arg case "$case_id" --arg run "$(basename "$match_file" .json)" \
          '{case: $case, run: $run, diffs: .diffs}' "$match_file"
        first=0
        REGRESSION_COUNT=$((REGRESSION_COUNT + 1))
      fi
    done
    # Also single-pass case.json convention
    if [[ -f "$case_dir/match.json" ]]; then
      if jq -e '.result == "fail"' "$case_dir/match.json" >/dev/null 2>&1; then
        [[ $first -eq 1 ]] || echo ","
        jq -c --arg case "$case_id" '{case: $case, run: "single", diffs: .diffs}' "$case_dir/match.json"
        first=0
        REGRESSION_COUNT=$((REGRESSION_COUNT + 1))
      fi
    fi
  done
  echo "]"
} > "$TMP_DIFFS"

if [[ "$REGRESSION_COUNT" -eq 0 ]]; then
  echo "[suggest-improvements] no regressions found — skipping suggester invocation" >&2
  cat > "$SNAP_DIR/suggestions.md" <<EOF
# Improvement Suggestions

No regressions detected in this snapshot. No suggestions to propose.
EOF
  echo "$SNAP_DIR/suggestions.md"
  exit 0
fi

echo "[suggest-improvements] $REGRESSION_COUNT regression(s) detected — calling $MODEL" >&2

# ─── Build prompt ─────────────────────────────────────────────────────
{
  cat <<'EOF'
You are reviewing a Claude Code skill that just failed its evaluation. Your job: propose **specific, concrete edits** to the SKILL.md that would likely close the regressions.

Output a single JSON object matching this schema:

```json
{
  "themes": [
    {
      "title": "<2-7 word theme name>",
      "regression_count": <int>,
      "root_cause": "<1-3 sentence diagnosis>",
      "proposed_edit": {
        "target_section": "<heading or line reference in SKILL.md>",
        "change_type": "add | modify | remove | reorder",
        "before": "<short excerpt of current text, or empty if 'add'>",
        "after":  "<new text>",
        "rationale": "<1-2 sentences linking this edit to the diagnosed root cause>"
      },
      "confidence": "high | medium | low",
      "risk": "<1 sentence — what could go wrong if this edit is applied>"
    }
  ],
  "overall_recommendation": "<1-3 sentence summary: apply one-by-one? bundle? more data needed?>"
}
```

Rules:
- Cluster similar regressions into themes (≤5 themes total)
- Each theme MUST propose a concrete edit, not just a diagnosis
- If a regression looks like LLM noise (LOW confidence), say so and recommend more N-repeat instead of an edit
- Reference the actual SKILL.md text in `before` / `target_section` — don't fabricate

────────────────────────────────────────────────
CURRENT SKILL.md (after-fix version that produced regressions):

EOF
  cat "$SOURCE_SKILL_MD"
  printf '\n────────────────────────────────────────────────\n'
  echo "REGRESSION DIFFS (JSON array, one entry per failed run):"
  echo ""
  cat "$TMP_DIFFS"
  printf '\n'
} > "$TMP_PROMPT"

# ─── Invoke ───────────────────────────────────────────────────────────
SUGG_SCHEMA='{"type":"object","required":["themes","overall_recommendation"],"properties":{"themes":{"type":"array","items":{"type":"object","required":["title","regression_count","root_cause","proposed_edit","confidence","risk"],"properties":{"title":{"type":"string"},"regression_count":{"type":"integer"},"root_cause":{"type":"string"},"proposed_edit":{"type":"object","required":["target_section","change_type","after","rationale"],"properties":{"target_section":{"type":"string"},"change_type":{"type":"string","enum":["add","modify","remove","reorder"]},"before":{"type":"string"},"after":{"type":"string"},"rationale":{"type":"string"}}},"confidence":{"type":"string","enum":["high","medium","low"]},"risk":{"type":"string"}}}},"overall_recommendation":{"type":"string"}}}'

RAW_LOG="$SNAP_DIR/.suggester-raw.json"
SUGG_JSON="$SNAP_DIR/suggestions.json"

if claude -p \
     --model "$MODEL" \
     --output-format json \
     --json-schema "$SUGG_SCHEMA" \
     --max-budget-usd "$MAX_BUDGET_USD" \
     --no-session-persistence \
     "$(cat "$TMP_PROMPT")" > "$RAW_LOG" 2>/dev/null
then
  if jq -e '.structured_output' "$RAW_LOG" >/dev/null 2>&1; then
    jq '.structured_output' "$RAW_LOG" > "$SUGG_JSON"
  elif jq -e '.result' "$RAW_LOG" >/dev/null 2>&1; then
    jq -r '.result' "$RAW_LOG" | jq . > "$SUGG_JSON" 2>/dev/null || \
      { echo "[suggest-improvements] result parse failed" >&2; exit 1; }
  fi
fi

if [[ ! -s "$SUGG_JSON" ]]; then
  echo "[suggest-improvements] suggester produced no JSON; check $RAW_LOG" >&2
  exit 1
fi

# ─── Render markdown ──────────────────────────────────────────────────
{
  echo "# Improvement Suggestions"
  echo ""
  echo "_Generated by skill-quality-eval's suggester (model: $MODEL)._"
  echo "_Snapshot: \`$(basename "$SNAP_DIR")\` vs baseline \`$(basename "$BASE_DIR")\`. Regressions analyzed: $REGRESSION_COUNT._"
  echo ""
  jq -r '"## Overall\n\n" + .overall_recommendation + "\n"' "$SUGG_JSON"
  echo ""
  jq -r '
    .themes
    | to_entries[]
    | "## Theme \(.key + 1): \(.value.title)\n\n"
      + "- **Regressions covered**: \(.value.regression_count)\n"
      + "- **Confidence**: \(.value.confidence)\n"
      + "- **Risk**: \(.value.risk)\n\n"
      + "### Root cause\n\n\(.value.root_cause)\n\n"
      + "### Proposed edit\n\n"
      + "- **Section**: `\(.value.proposed_edit.target_section)`\n"
      + "- **Change type**: \(.value.proposed_edit.change_type)\n\n"
      + (if .value.proposed_edit.before and (.value.proposed_edit.before | length > 0)
         then "**Before:**\n\n```\n\(.value.proposed_edit.before)\n```\n\n" else "" end)
      + "**After:**\n\n```\n\(.value.proposed_edit.after)\n```\n\n"
      + "### Rationale\n\n\(.value.proposed_edit.rationale)\n"
  ' "$SUGG_JSON"
} > "$SNAP_DIR/suggestions.md"

echo "$SNAP_DIR/suggestions.md"
