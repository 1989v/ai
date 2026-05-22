#!/usr/bin/env bash
#
# eval-case.sh — orchestrate N-repeat invokes for a single case + compute
#   accuracy (vs baseline) + stability (variance across the N runs).
#
# Why N-repeat: LLM calls are non-deterministic. 1 invoke can't distinguish
#   "actually passes" / "got lucky" / "actually fails" / "lost a coin flip".
#   N invokes reveal two orthogonal signals:
#     accuracy  = (# runs matching baseline) / N         → how often correct
#     stability = (size of largest canonical-equiv class) / N  → how consistent
#
# Usage:
#   eval-case.sh \
#     --skill-id hns-glossary \
#     --snapshot-dir /path/to/snapshots/{tag}/ \
#     --case-id case-001 \
#     --source-skill-dir /path/to/skill \
#     --schema /path/to/output.schema.json \
#     --input /path/to/input.yml \
#     --policy /path/to/matching-policy.json \
#     [--baseline-dir /path/to/baseline-snap]   # if omitted: this IS the baseline run (no compare)
#     [--repeat 3]                              # default 3
#     [--model haiku]
#     [--max-budget-usd 3.00]
#     [--retry 1]
#
# Output structure (under {snapshot-dir}/cases/{case-id}/):
#   actual-001.json, actual-002.json, ... actual-N.json
#   canon-001.json, ... canon-N.json                       (canonical form via match policy)
#   match-001.json, match-002.json, ... match-N.json       (vs baseline, if --baseline-dir given)
#   case-summary.json                                       (accuracy + stability + per-run results)

set -euo pipefail

SKILL_ID=""; SNAPSHOT_DIR=""; CASE_ID=""
SOURCE_SKILL_DIR=""; SCHEMA=""; INPUT=""; POLICY=""
BASELINE_DIR=""
REPEAT="3"
MODEL="opus"
MAX_BUDGET_USD="3.00"
RETRY="1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill-id) SKILL_ID="$2"; shift 2 ;;
    --snapshot-dir) SNAPSHOT_DIR="$2"; shift 2 ;;
    --case-id) CASE_ID="$2"; shift 2 ;;
    --source-skill-dir) SOURCE_SKILL_DIR="$2"; shift 2 ;;
    --schema) SCHEMA="$2"; shift 2 ;;
    --input) INPUT="$2"; shift 2 ;;
    --policy) POLICY="$2"; shift 2 ;;
    --baseline-dir) BASELINE_DIR="$2"; shift 2 ;;
    --repeat) REPEAT="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --max-budget-usd) MAX_BUDGET_USD="$2"; shift 2 ;;
    --retry) RETRY="$2"; shift 2 ;;
    -h|--help) sed -n '3,40p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

for v in SKILL_ID SNAPSHOT_DIR CASE_ID SOURCE_SKILL_DIR SCHEMA INPUT; do
  if [[ -z "${!v}" ]]; then echo "missing required: --${v,,}" >&2; exit 64; fi
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORK_INVOKE="$SCRIPT_DIR/fork-and-invoke.sh"
MATCH="$SCRIPT_DIR/match.sh"
CASE_DIR="$SNAPSHOT_DIR/cases/$CASE_ID"
mkdir -p "$CASE_DIR"

# Per-run budget so total roughly bounded
PER_RUN_BUDGET="$(echo "$MAX_BUDGET_USD / $REPEAT" | bc -l 2>/dev/null || echo "$MAX_BUDGET_USD")"
PER_RUN_BUDGET="$(printf '%.2f' "$PER_RUN_BUDGET")"

echo "[eval-case] $SKILL_ID/$CASE_ID — N=$REPEAT, model=$MODEL, per-run budget=\$$PER_RUN_BUDGET" >&2

# ─── 1) N invokes ─────────────────────────────────────────────
declare -a RUN_FILES
for ((i=1; i<=REPEAT; i++)); do
  iter_id="$(printf '%03d' "$i")"
  iter_dir="$CASE_DIR/.runs/$iter_id"
  mkdir -p "$iter_dir"

  echo "[eval-case] === run $i/$REPEAT ===" >&2

  # fork-and-invoke writes to {snapshot-dir}/cases/{case-id}/{output-kind}.json
  # we then rename to actual-NNN.json
  if "$FORK_INVOKE" \
       --skill-id "$SKILL_ID" \
       --snapshot-dir "$SNAPSHOT_DIR" \
       --case-id "$CASE_ID" \
       --source-skill-dir "$SOURCE_SKILL_DIR" \
       --schema "$SCHEMA" \
       --input "$INPUT" \
       --output-kind "actual" \
       --model "$MODEL" \
       --max-budget-usd "$PER_RUN_BUDGET" \
       --retry "$RETRY" 2>&1 | sed 's/^/  /' >&2
  then
    mv "$CASE_DIR/actual.json" "$CASE_DIR/actual-${iter_id}.json"
    RUN_FILES+=("$CASE_DIR/actual-${iter_id}.json")
  else
    echo "[eval-case] run $i FAILED (format-fail or budget exhausted)" >&2
    echo '{"format_fail": true}' > "$CASE_DIR/actual-${iter_id}.json"
    RUN_FILES+=("$CASE_DIR/actual-${iter_id}.json")
  fi
done

# ─── 2) compute canonical form of each run for stability grouping ─────
POLICY_FILE_ARG=""
if [[ -n "$POLICY" && -f "$POLICY" ]]; then
  POLICY_FILE_ARG="--policy $POLICY"
fi

declare -a CANON_HASHES
for ((i=1; i<=REPEAT; i++)); do
  iter_id="$(printf '%03d' "$i")"
  run_file="$CASE_DIR/actual-${iter_id}.json"
  canon_file="$CASE_DIR/canon-${iter_id}.json"

  # Canonical form = match.sh's internal canon() applied to actual vs itself.
  # We trick it: match actual against itself, then re-derive canonical via jq -S.
  # Simpler: jq -S . (sorted-keys) is a decent proxy when policy is empty.
  # When policy exists, we use a dedicated jq invocation that just canonicalizes.
  if [[ -f "$POLICY" ]]; then
    # Canonicalize using same policy semantics as match.sh
    jq -n -c \
       --argjson actual "$(jq -c . "$run_file")" \
       --argjson pol    "$(jq -c . "$POLICY")" '
       def norm(rules):
         if type == "string" then
           . as $s | (if (rules.case // "") == "lower" then ascii_downcase else . end)
                   | (if (rules.trim // false) then sub("^\\s+";"") | sub("\\s+$";"") else . end)
                   | (if (rules["collapse-whitespace"] // false) then gsub("\\s+"; " ") else . end)
         elif type == "object" then with_entries(.value |= norm(rules))
         elif type == "array"  then map(norm(rules))
         else . end;
       def strip_null(rules):
         if (rules["null-equals-missing"] // false) and (type == "object")
         then with_entries(select(.value != null)) else . end;
       def canon(p):
         ((if (p | type) == "object" then (p.normalize // {}) else {} end) as $rules
          | strip_null($rules) | norm($rules)) as $v
         | if (p | type) == "string" then
             if p == "structural" or p == "semantic"
             then "<TYPE:" + ($v | type) + ">" else $v end
           else
             ((p.fields // {}) as $fields
              | if ($v | type) == "object" then
                  ($v | keys) as $ks
                  | reduce $ks[] as $k ({}; . + { ($k): ($v[$k] | canon($fields[$k] // {})) })
                elif ($v | type) == "array" then
                  ((p["match-by"] // null) as $mkey
                   | (if $mkey != null then ($v | sort_by(.[$mkey] // "")) else $v end)) as $arr
                  | (($fields["[*]"] // { "fields": $fields }) as $elem_pol
                     | $arr | map(canon($elem_pol)))
                else $v end)
           end;
       ($pol["$root"] // $pol // {}) as $rp
       | $actual | canon($rp)
    ' > "$canon_file"
  else
    jq -S -c . "$run_file" > "$canon_file"
  fi

  hash="$(shasum -a 256 "$canon_file" | awk '{print $1}')"
  CANON_HASHES+=("$hash")
done

# ─── 3) compute stability (size of largest canonical-equiv class / N) ──
STABILITY_RAW="$(printf '%s\n' "${CANON_HASHES[@]}" | sort | uniq -c | sort -rn | head -1 | awk '{print $1}')"
STABILITY_PCT="$(echo "scale=2; $STABILITY_RAW / $REPEAT" | bc -l)"

# ─── 4) compute accuracy (matches baseline) if baseline given ─────────
ACCURACY_RAW=0
declare -a MATCH_RESULTS
if [[ -n "$BASELINE_DIR" && -f "$BASELINE_DIR/cases/$CASE_ID/expected.json" ]]; then
  EXPECTED="$BASELINE_DIR/cases/$CASE_ID/expected.json"
  for ((i=1; i<=REPEAT; i++)); do
    iter_id="$(printf '%03d' "$i")"
    actual="$CASE_DIR/actual-${iter_id}.json"
    match_file="$CASE_DIR/match-${iter_id}.json"
    # If the run was format-fail, skip match (counts as miss)
    if jq -e '.format_fail == true' "$actual" >/dev/null 2>&1; then
      echo '{"result":"format-fail","diffs":[]}' > "$match_file"
      MATCH_RESULTS+=("format-fail")
      continue
    fi
    if "$MATCH" --expected "$EXPECTED" --actual "$actual" $POLICY_FILE_ARG > "$match_file" 2>/dev/null; then
      ACCURACY_RAW=$((ACCURACY_RAW + 1))
      MATCH_RESULTS+=("pass")
    else
      MATCH_RESULTS+=("fail")
    fi
  done
fi
ACCURACY_PCT="$(echo "scale=2; $ACCURACY_RAW / $REPEAT" | bc -l)"

# ─── 5) write case-summary.json ───────────────────────────────────────
{
  echo "{"
  echo "  \"case_id\": \"$CASE_ID\","
  echo "  \"repeat\": $REPEAT,"
  echo "  \"model\": \"$MODEL\","
  echo "  \"accuracy\": $ACCURACY_PCT,"
  echo "  \"accuracy_raw\": \"$ACCURACY_RAW/$REPEAT\","
  echo "  \"stability\": $STABILITY_PCT,"
  echo "  \"stability_raw\": \"$STABILITY_RAW/$REPEAT\","
  echo "  \"baseline\": $(if [[ -n "$BASELINE_DIR" ]]; then echo "\"$(basename "$BASELINE_DIR")\""; else echo "null"; fi),"
  echo "  \"runs\": ["
  for ((i=1; i<=REPEAT; i++)); do
    iter_id="$(printf '%03d' "$i")"
    match_result="${MATCH_RESULTS[$((i-1))]:-no-baseline}"
    canon_hash="${CANON_HASHES[$((i-1))]:0:12}"
    comma=$([[ $i -lt $REPEAT ]] && echo "," || echo "")
    echo "    {\"iter\": $i, \"match\": \"$match_result\", \"canon_hash\": \"$canon_hash\"}$comma"
  done
  echo "  ]"
  echo "}"
} | jq . > "$CASE_DIR/case-summary.json"

echo "[eval-case] $SKILL_ID/$CASE_ID — accuracy=$ACCURACY_RAW/$REPEAT ($ACCURACY_PCT) stability=$STABILITY_RAW/$REPEAT ($STABILITY_PCT)" >&2
cat "$CASE_DIR/case-summary.json"
