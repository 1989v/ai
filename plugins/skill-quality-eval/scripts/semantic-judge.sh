#!/usr/bin/env bash
#
# semantic-judge.sh — Haiku-as-judge for natural-language field matching
#
# Used by match.sh when matching-policy declares a field as `semantic`.
# Input two JSON values (expected, actual). Output JSON:
#   { "match": bool, "confidence": 0-1, "reasoning": "<short rationale>" }
#
# Cache: keyed by sha256(expected || actual). Cache dir defaults to
#   $SKILL_EVAL_JUDGE_CACHE (env) or /tmp/skill-eval-judge-cache/.
#
# Usage:
#   semantic-judge.sh --expected '"foo bar"' --actual '"foo, bar"' [--field-path '$.terms[0].description'] [--model haiku]
#   semantic-judge.sh --expected-file e.json --actual-file a.json [--field-path ...] [--no-cache]

set -euo pipefail

EXPECTED_JSON=""; ACTUAL_JSON=""
EXPECTED_FILE=""; ACTUAL_FILE=""
FIELD_PATH=""
MODEL="haiku"
MAX_BUDGET_USD="0.30"
USE_CACHE="1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --expected) EXPECTED_JSON="$2"; shift 2 ;;
    --actual)   ACTUAL_JSON="$2"; shift 2 ;;
    --expected-file) EXPECTED_FILE="$2"; shift 2 ;;
    --actual-file)   ACTUAL_FILE="$2"; shift 2 ;;
    --field-path) FIELD_PATH="$2"; shift 2 ;;
    --model)      MODEL="$2"; shift 2 ;;
    --max-budget-usd) MAX_BUDGET_USD="$2"; shift 2 ;;
    --no-cache) USE_CACHE="0"; shift ;;
    -h|--help) sed -n '3,20p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

if [[ -n "$EXPECTED_FILE" ]]; then EXPECTED_JSON="$(cat "$EXPECTED_FILE")"; fi
if [[ -n "$ACTUAL_FILE" ]]; then ACTUAL_JSON="$(cat "$ACTUAL_FILE")"; fi
if [[ -z "$EXPECTED_JSON" || -z "$ACTUAL_JSON" ]]; then
  echo "expected and actual required" >&2; exit 64
fi

command -v claude >/dev/null || { echo "claude CLI not found" >&2; exit 69; }
command -v jq >/dev/null || { echo "jq not found" >&2; exit 69; }

# ─── cache lookup ─────────────────────────────────────────────────────
CACHE_DIR="${SKILL_EVAL_JUDGE_CACHE:-/tmp/skill-eval-judge-cache}"
mkdir -p "$CACHE_DIR"
CACHE_KEY="$(echo -n "${EXPECTED_JSON}::${ACTUAL_JSON}::${MODEL}" | shasum -a 256 | awk '{print $1}')"
CACHE_FILE="$CACHE_DIR/$CACHE_KEY.json"

if [[ "$USE_CACHE" = "1" && -f "$CACHE_FILE" ]]; then
  cat "$CACHE_FILE"
  exit 0
fi

# ─── fast-path: identical values bypass LLM ──────────────────────────
if [[ "$(echo "$EXPECTED_JSON" | jq -c .)" = "$(echo "$ACTUAL_JSON" | jq -c .)" ]]; then
  echo '{"match": true, "confidence": 1.0, "reasoning": "values are identical"}' \
    | tee "$CACHE_FILE"
  exit 0
fi

# ─── call Haiku ───────────────────────────────────────────────────────
JUDGE_SCHEMA='{"type":"object","required":["match","confidence","reasoning"],"properties":{"match":{"type":"boolean"},"confidence":{"type":"number","minimum":0,"maximum":1},"reasoning":{"type":"string"}}}'

PROMPT="You are judging whether two values mean the same thing semantically. The values are field values extracted from a structured skill output (skill-quality-eval).

Field path: ${FIELD_PATH:-<unknown>}

Expected value (canonical / ground-truth):
$EXPECTED_JSON

Actual value (skill output):
$ACTUAL_JSON

Decide: do these two values convey the same meaning in this context? Minor wording differences = match. Different facts / different referents / contradicting claims = mismatch.

Respond ONLY with a single JSON object matching the schema. confidence: 1.0 = clearly equivalent, 0.5 = ambiguous, 0.0 = clearly different. reasoning: 1 short sentence."

RAW="$(mktemp -t skill-eval-judge-XXXXXX)"
trap 'rm -f "$RAW"' EXIT

if claude -p \
     --model "$MODEL" \
     --output-format json \
     --json-schema "$JUDGE_SCHEMA" \
     --max-budget-usd "$MAX_BUDGET_USD" \
     --no-session-persistence \
     "$PROMPT" > "$RAW" 2>/dev/null
then
  if jq -e '.structured_output' "$RAW" >/dev/null 2>&1; then
    jq -c '.structured_output' "$RAW" | tee "$CACHE_FILE"
    exit 0
  elif jq -e '.result' "$RAW" >/dev/null 2>&1; then
    result_str="$(jq -r '.result' "$RAW")"
    if echo "$result_str" | jq -e . >/dev/null 2>&1; then
      echo "$result_str" | jq -c . | tee "$CACHE_FILE"
      exit 0
    fi
  fi
fi

# ─── judge failure → conservative default (mismatch with low confidence) ─
echo '{"match": false, "confidence": 0.0, "reasoning": "judge invocation failed; defaulting to mismatch"}' | tee "$CACHE_FILE"
exit 0
