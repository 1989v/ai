#!/usr/bin/env bash
#
# match.sh — compare expected.json vs actual.json under matching-policy.json
#
# Usage:
#   match.sh --expected expected.json --actual actual.json --policy matching-policy.json
#
# Output (stdout):
#   JSON object: { "result": "pass|fail", "diffs": [{"path": "...", "expected": ..., "actual": ...}] }
#
# Exit codes: 0 = pass, 1 = fail, 64 = bad args, 65 = malformed input
#
# v0.1 scope:
#   - strict (deep-equal with normalization)
#   - structural (key set + type check)
#   - semantic → degraded to strict with warning
#   - normalize: case=lower, trim, collapse-whitespace, null-equals-missing
#   - array match-by (order-independent pairing by key)
#   - default policy = strict throughout

set -euo pipefail

EXPECTED=""; ACTUAL=""; POLICY=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --expected) EXPECTED="$2"; shift 2 ;;
    --actual)   ACTUAL="$2"; shift 2 ;;
    --policy)   POLICY="$2"; shift 2 ;;
    -h|--help)
      sed -n '3,18p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

[[ -f "$EXPECTED" ]] || { echo "expected not found: $EXPECTED" >&2; exit 65; }
[[ -f "$ACTUAL" ]]   || { echo "actual not found: $ACTUAL" >&2; exit 65; }
command -v jq >/dev/null || { echo "jq not found" >&2; exit 69; }

# Policy file is optional; if missing, all-strict default
POLICY_JSON='{}'
if [[ -n "$POLICY" && -f "$POLICY" ]]; then
  POLICY_JSON="$(cat "$POLICY")"
fi

# v0.1 uses an all-in-jq comparator. Normalization rules at the root, then
# per-field strict/structural dispatch, then optional match-by for arrays.
RESULT_JSON="$(jq -n \
   --argfile expected "$EXPECTED" \
   --argfile actual   "$ACTUAL" \
   --argjson policy   "$POLICY_JSON" '

# ─── normalization ───
def normalize(rules):
  if type == "string" then
    . as $s
    | (if (rules.case // "") == "lower" then ascii_downcase else . end)
    | (if (rules.trim // false) then sub("^\\s+";"") | sub("\\s+$";"") else . end)
    | (if (rules["collapse-whitespace"] // false) then gsub("\\s+";" ") else . end)
  elif type == "object" then
    with_entries(.value |= normalize(rules))
  elif type == "array" then
    map(normalize(rules))
  else .
  end;

def null_equals_missing(rules; obj):
  if (rules["null-equals-missing"] // false) and (obj | type) == "object"
  then obj | with_entries(select(.value != null))
  else obj
  end;

# ─── core compare ───
# Returns array of diffs at given json path
def cmp($e; $a; mode; rules; path):
  ($e | normalize(rules)) as $en
  | ($a | normalize(rules)) as $an
  | if mode == "structural"
    then
      if ($en | type) != ($an | type)
      then [{path: path, kind: "type-mismatch", expected: ($en|type), actual: ($an|type)}]
      else []
      end
    else  # strict (default + semantic-degraded)
      if $en == $an
      then []
      else [{path: path, kind: "value-diff", expected: $en, actual: $an}]
      end
    end;

# ─── recursive walk with policy ───
def walk_compare($e; $a; $pol; path):
  ($pol.fields // {}) as $fields
  | ($pol.normalize // {}) as $rules
  | if ($e | type) == "object" and ($a | type) == "object"
    then
      (null_equals_missing($rules; $e)) as $ec
      | (null_equals_missing($rules; $a)) as $ac
      # union of keys
      | (($ec | keys) + ($ac | keys) | unique) as $all_keys
      | reduce $all_keys[] as $k (
          [];
          . + (
            ($fields[$k]) as $sub_pol
            | if $sub_pol == null then
                # No policy → strict
                cmp($ec[$k] // null; $ac[$k] // null; "strict"; $rules; path + "." + $k)
              elif ($sub_pol | type) == "string" then
                # Leaf mode: strict/structural/(semantic→strict)
                ( if $sub_pol == "semantic" then "strict" else $sub_pol end ) as $mode
                | cmp($ec[$k] // null; $ac[$k] // null; $mode; $rules; path + "." + $k)
              else
                # Nested policy object
                walk_compare($ec[$k] // null; $ac[$k] // null; $sub_pol; path + "." + $k)
              end
          )
        )
    elif ($e | type) == "array" and ($a | type) == "array"
    then
      ($pol["match-by"] // null) as $mkey
      | if $mkey == null
        then
          # ordered compare
          if ($e | length) != ($a | length)
          then [{path: path, kind: "array-length", expected: ($e|length), actual: ($a|length)}]
          else
            reduce range(0; $e|length) as $i (
              [];
              . + walk_compare($e[$i]; $a[$i]; (($pol.fields // {})["[*]"] // ($pol.fields // {}) // {}); path + "[" + ($i|tostring) + "]")
            )
          end
        else
          # match-by key: pair items, find orphans
          (($e | map({ (.[$mkey] // ""): . }) | add // {})) as $emap
          | (($a | map({ (.[$mkey] // ""): . }) | add // {})) as $amap
          | (($emap | keys) + ($amap | keys) | unique) as $all_keys
          | reduce $all_keys[] as $k (
              [];
              . + (
                if ($emap[$k] == null) then
                  [{path: path + "[" + $mkey + "=" + $k + "]", kind: "orphan-actual", actual: $amap[$k]}]
                elif ($amap[$k] == null) then
                  [{path: path + "[" + $mkey + "=" + $k + "]", kind: "orphan-expected", expected: $emap[$k]}]
                else
                  walk_compare($emap[$k]; $amap[$k]; ($pol | del(.["match-by"])); path + "[" + $mkey + "=" + $k + "]")
                end
              )
            )
        end
    else
      cmp($e; $a; "strict"; ($pol.normalize // {}); path)
    end;

# Entrypoint
($policy["$root"] // $policy // {}) as $root_policy
| walk_compare($expected; $actual; $root_policy; "$")
| { result: (if length == 0 then "pass" else "fail" end), diffs: . }
')"

# Print result JSON to stdout
echo "$RESULT_JSON"

# Exit code from .result
if echo "$RESULT_JSON" | jq -e '.result == "pass"' >/dev/null; then
  exit 0
else
  exit 1
fi
