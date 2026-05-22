#!/usr/bin/env bash
#
# calibrate-judge.sh — measure semantic-judge's accuracy against a labelled
#   calibration set. Used as a "trust check" before relying on judge verdicts
#   in actual evaluation. Avoids the judge-of-judge infinite regress by:
#   (a) keeping the calibration set human-labelled (ground_truth field)
#   (b) only reporting accuracy + warning when below threshold; no auto-correction
#
# Calibration set format:
#   goldset/{skill-id}/judge-calibration/{name}.yml
#   ---
#   expected: "the value the skill should emit"
#   actual:   "the candidate value"
#   ground_truth: pass | fail        # human's verdict
#   note: "optional explanation"
#
# Usage:
#   calibrate-judge.sh --calibration-dir goldset/hns-glossary/judge-calibration \
#                      [--model haiku] [--threshold 0.8]
#
# Output: JSON {accuracy, total, correct, mismatches: [...]} to stdout.
# Exit code: 0 if accuracy >= threshold, 1 otherwise (CI-friendly).

set -euo pipefail

CAL_DIR=""
MODEL="haiku"
THRESHOLD="0.8"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --calibration-dir) CAL_DIR="$2"; shift 2 ;;
    --model)           MODEL="$2"; shift 2 ;;
    --threshold)       THRESHOLD="$2"; shift 2 ;;
    -h|--help) sed -n '3,20p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

if [[ -z "$CAL_DIR" || ! -d "$CAL_DIR" ]]; then
  echo "calibration dir not found: $CAL_DIR" >&2
  echo '{"accuracy": null, "total": 0, "correct": 0, "mismatches": [], "skipped": true, "reason": "no calibration dir"}'
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JUDGE="$SCRIPT_DIR/semantic-judge.sh"
command -v jq >/dev/null || { echo "jq not found" >&2; exit 69; }

# Find all .yml files in calibration dir
mapfile -t CAL_FILES < <(find "$CAL_DIR" -maxdepth 2 -name '*.yml' -type f | sort)
if [[ "${#CAL_FILES[@]}" -eq 0 ]]; then
  echo '{"accuracy": null, "total": 0, "correct": 0, "mismatches": [], "skipped": true, "reason": "empty calibration set"}'
  exit 0
fi

TMP_MIS="$(mktemp -t skill-eval-calmis-XXXXXX)"
trap 'rm -f "$TMP_MIS"' EXIT
: > "$TMP_MIS"

CORRECT=0
TOTAL=0

for f in "${CAL_FILES[@]}"; do
  # Pull fields out of YAML using a python-free approach: we accept a strict
  # subset (top-level keys only, simple scalar values, no nested structures).
  # If you need richer YAML, switch to yq.
  EXPECTED="$(awk -F': ' '/^expected:/ {sub(/^expected: */,""); print; exit}' "$f")"
  ACTUAL="$(awk -F': ' '/^actual:/ {sub(/^actual: */,""); print; exit}' "$f")"
  GROUND="$(awk -F': ' '/^ground_truth:/ {sub(/^ground_truth: */,""); print; exit}' "$f")"

  if [[ -z "$EXPECTED" || -z "$ACTUAL" || -z "$GROUND" ]]; then
    echo "[calibrate-judge] skipping malformed: $f" >&2
    continue
  fi

  # Treat values as JSON strings (quote if not already JSON)
  if ! echo "$EXPECTED" | jq -e . >/dev/null 2>&1; then EXPECTED="$(jq -nc --arg v "$EXPECTED" '$v')"; fi
  if ! echo "$ACTUAL"   | jq -e . >/dev/null 2>&1; then ACTUAL="$(jq -nc --arg v "$ACTUAL" '$v')"; fi

  TOTAL=$((TOTAL + 1))
  judge_result="$("$JUDGE" --expected "$EXPECTED" --actual "$ACTUAL" --model "$MODEL" 2>/dev/null \
                    || echo '{"match":false,"confidence":0,"reasoning":"judge error"}')"
  judge_verdict="$(echo "$judge_result" | jq -r 'if .match then "pass" else "fail" end')"

  if [[ "$judge_verdict" = "$GROUND" ]]; then
    CORRECT=$((CORRECT + 1))
  else
    echo "$judge_result" | jq -c \
      --arg file "$(basename "$f")" --arg ground "$GROUND" \
      --argjson exp "$EXPECTED" --argjson act "$ACTUAL" \
      '{ case: $file, ground_truth: $ground, judge_said: (if .match then "pass" else "fail" end),
         expected: $exp, actual: $act, judge: . }' >> "$TMP_MIS"
  fi
done

if [[ "$TOTAL" -eq 0 ]]; then
  echo '{"accuracy": null, "total": 0, "correct": 0, "mismatches": [], "skipped": true, "reason": "no readable calibration cases"}'
  exit 0
fi

ACCURACY="$(echo "scale=4; $CORRECT / $TOTAL" | bc -l)"
MISMATCHES="$(jq -cs '.' "$TMP_MIS" 2>/dev/null || echo "[]")"

RESULT="$(jq -n \
  --argjson acc "$ACCURACY" --argjson total "$TOTAL" --argjson correct "$CORRECT" \
  --argjson mis "$MISMATCHES" --argjson th "$THRESHOLD" --arg model "$MODEL" '
  { accuracy: $acc, total: $total, correct: $correct, threshold: $th, model: $model,
    pass_threshold: ($acc >= $th), mismatches: $mis }')"

echo "$RESULT" | jq .
jq -e '.pass_threshold == true' <<<"$RESULT" >/dev/null
