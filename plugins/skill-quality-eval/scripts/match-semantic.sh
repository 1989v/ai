#!/usr/bin/env bash
#
# match-semantic.sh — match.sh + semantic-judge.sh for `semantic` fields.
#
# Flow:
#   1. Run match.sh (strict + structural baseline — semantic treated as type marker).
#   2. Walk policy to collect (path, expected, actual) triples where mode = semantic.
#   3. Call semantic-judge.sh for each triple (Haiku) — cached by value hash.
#   4. Append judge mismatches to diffs, recompute result.
#
# Same args as match.sh, plus:
#   --judge-model haiku      (default haiku)
#   --judge-cache-dir <path> (default /tmp/skill-eval-judge-cache; can also set SKILL_EVAL_JUDGE_CACHE)
#
# Output: same JSON shape as match.sh, with semantic-mismatch entries added to .diffs.

set -euo pipefail

EXPECTED=""; ACTUAL=""; POLICY=""
JUDGE_MODEL="haiku"
JUDGE_CACHE_DIR="${SKILL_EVAL_JUDGE_CACHE:-/tmp/skill-eval-judge-cache}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --expected) EXPECTED="$2"; shift 2 ;;
    --actual)   ACTUAL="$2"; shift 2 ;;
    --policy)   POLICY="$2"; shift 2 ;;
    --judge-model) JUDGE_MODEL="$2"; shift 2 ;;
    --judge-cache-dir) JUDGE_CACHE_DIR="$2"; shift 2 ;;
    -h|--help) sed -n '3,20p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done
[[ -f "$EXPECTED" ]] || { echo "expected not found" >&2; exit 65; }
[[ -f "$ACTUAL" ]]   || { echo "actual not found" >&2; exit 65; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MATCH="$SCRIPT_DIR/match.sh"
JUDGE="$SCRIPT_DIR/semantic-judge.sh"
export SKILL_EVAL_JUDGE_CACHE="$JUDGE_CACHE_DIR"

# ─── 1) base match (strict + structural) ────────────────────────────────
BASE="$("$MATCH" --expected "$EXPECTED" --actual "$ACTUAL" ${POLICY:+--policy "$POLICY"} || true)"

# No policy? semantic mode can't apply; just return base.
if [[ -z "$POLICY" || ! -f "$POLICY" ]]; then
  echo "$BASE"
  jq -e '.result == "pass"' <<<"$BASE" >/dev/null
  exit $?
fi

# ─── 2) walk policy + both JSONs in parallel, collect semantic pairs ────
EXPECTED_JSON="$(jq -c . "$EXPECTED")"
ACTUAL_JSON="$(jq -c . "$ACTUAL")"
POLICY_JSON="$(jq -c . "$POLICY")"

PAIRS="$(jq -n -c \
   --argjson e "$EXPECTED_JSON" \
   --argjson a "$ACTUAL_JSON" \
   --argjson p "$POLICY_JSON" '

def collect(loc; ev; av; pol):
  if (pol | type) == "string" then
    if pol == "semantic" then
      [{ path: loc, expected: ev, actual: av }]
    else [] end
  elif (pol | type) == "object" then
    ((pol.fields // {}) as $f
     | if (ev | type) == "object" and (av | type) == "object" then
         (((ev | keys) + (av | keys)) | unique) as $ks
         | reduce $ks[] as $k ([];
             . + collect("\(loc).\($k)"; ev[$k] // null; av[$k] // null; $f[$k] // {}))
       elif (ev | type) == "array" and (av | type) == "array" then
         (pol["match-by"] // null) as $mkey
         | (($f["[*]"] // { fields: $f })) as $elem_pol
         | if $mkey != null then
             (ev | map({(.[$mkey] // "" | tostring): .}) | add // {}) as $em
             | (av | map({(.[$mkey] // "" | tostring): .}) | add // {}) as $am
             | (($em | keys) + ($am | keys) | unique) as $ks2
             | reduce $ks2[] as $k ([];
                 . + collect("\(loc)[\($mkey)=\($k)]"; $em[$k] // null; $am[$k] // null; $elem_pol))
           else
             reduce range(0; [(ev | length), (av | length)] | min) as $i ([];
               . + collect("\(loc)[\($i)]"; ev[$i]; av[$i]; $elem_pol))
           end
       else [] end)
  else [] end;

collect("$"; $e; $a; ($p["$root"] // $p // {}))
')"

NUM_PAIRS="$(echo "$PAIRS" | jq 'length')"
echo "[match-semantic] $NUM_PAIRS semantic pair(s) detected via policy walk" >&2

# ─── 3) call judge for each pair (writes mismatches to temp file) ──────
TMP_DIFFS="$(mktemp -t skill-eval-semdiffs-XXXXXX)"
trap 'rm -f "$TMP_DIFFS"' EXIT
: > "$TMP_DIFFS"

echo "$PAIRS" | jq -c '.[]' | while IFS= read -r pair; do
  path="$(echo "$pair"   | jq -r '.path')"
  exp_val="$(echo "$pair" | jq -c '.expected')"
  act_val="$(echo "$pair" | jq -c '.actual')"

  # Skip when both null (e.g. orphan)
  if [[ "$exp_val" = "null" && "$act_val" = "null" ]]; then continue; fi

  judge_result="$("$JUDGE" --expected "$exp_val" --actual "$act_val" --field-path "$path" --model "$JUDGE_MODEL" 2>/dev/null \
                    || echo '{"match":false,"confidence":0.0,"reasoning":"judge invocation error"}')"

  if ! echo "$judge_result" | jq -e '.match == true' >/dev/null; then
    echo "$judge_result" | jq -c \
      --arg path "$path" --argjson e "$exp_val" --argjson a "$act_val" \
      '{ path: $path, kind: "semantic-mismatch", expected: $e, actual: $a, judge: . }' \
      >> "$TMP_DIFFS"
  fi
done

# ─── 4) merge into base result ─────────────────────────────────────────
SEMANTIC_DIFFS="$(jq -cs '.' "$TMP_DIFFS" 2>/dev/null || echo "[]")"
FINAL="$(jq -n -c --argjson base "$BASE" --argjson sem "$SEMANTIC_DIFFS" '
  ($base // {result:"pass", diffs:[]}) as $b
  | { result: (if ((($b.diffs // []) + $sem) | length) == 0 then "pass" else "fail" end),
      diffs: (($b.diffs // []) + $sem),
      semantic_pairs_checked: ($sem | length) }
')"

echo "$FINAL" | jq .

jq -e '.result == "pass"' <<<"$FINAL" >/dev/null
