#!/usr/bin/env bash
#
# match.sh — compare expected.json vs actual.json under matching-policy.json
#
# Strategy (v0.1): canonicalize both sides per policy, then deep-equal.
#   - Normalize strings (case/trim/collapse-whitespace)
#   - Sort arrays declared with `match-by` by that key
#   - Replace `structural` field values with their type tag (so only type/presence is compared)
#   - Replace `semantic` field values with type tag (degraded to strict-on-type in v0.1)
#   - Plain (no policy) → strict via deep-equal of canonical form
#
# Usage:
#   match.sh --expected expected.json --actual actual.json --policy matching-policy.json
#
# Output (stdout):
#   JSON object: { "result": "pass|fail", "diffs": [{ "path": "...", "expected": ..., "actual": ... }] }
#
# Exit codes: 0 = pass, 1 = fail, 64 = bad args, 65 = malformed input

set -euo pipefail

EXPECTED=""; ACTUAL=""; POLICY=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --expected) EXPECTED="$2"; shift 2 ;;
    --actual)   ACTUAL="$2"; shift 2 ;;
    --policy)   POLICY="$2"; shift 2 ;;
    -h|--help)  sed -n '3,20p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

[[ -f "$EXPECTED" ]] || { echo "expected not found: $EXPECTED" >&2; exit 65; }
[[ -f "$ACTUAL" ]]   || { echo "actual not found: $ACTUAL" >&2; exit 65; }
command -v jq >/dev/null || { echo "jq not found" >&2; exit 69; }

POLICY_JSON='{}'
if [[ -n "$POLICY" && -f "$POLICY" ]]; then
  POLICY_JSON="$(jq -c . "$POLICY")"
fi
EXPECTED_JSON="$(jq -c . "$EXPECTED")"
ACTUAL_JSON="$(jq -c . "$ACTUAL")"

# Single jq pipeline canonicalizes both sides + computes diff
RESULT_JSON="$(jq -n -c \
   --argjson expected "$EXPECTED_JSON" \
   --argjson actual   "$ACTUAL_JSON" \
   --argjson pol      "$POLICY_JSON" '

# ─── normalization on strings (or recursively on containers) ───
def norm(rules):
  if type == "string" then
    . as $s
    | (if (rules.case // "") == "lower" then ascii_downcase else . end)
    | (if (rules.trim // false) then sub("^\\s+";"") | sub("\\s+$";"") else . end)
    | (if (rules["collapse-whitespace"] // false) then gsub("\\s+"; " ") else . end)
  elif type == "object" then with_entries(.value |= norm(rules))
  elif type == "array"  then map(norm(rules))
  else .
  end;

def strip_null(rules):
  if (rules["null-equals-missing"] // false) and (type == "object")
  then with_entries(select(.value != null))
  else .
  end;

# ─── canonicalize a value under a (sub-)policy ───
# p can be a string ("strict"/"structural"/"semantic") for leaf-mode,
# or an object with optional fields/match-by/normalize keys.
def canon(p):
  ((if (p | type) == "object" then (p.normalize // {}) else {} end) as $rules
   | strip_null($rules)
   | norm($rules)) as $v
  | if (p | type) == "string" then
      if p == "structural" or p == "semantic"
      then "<TYPE:" + ($v | type) + ">"
      else $v  # strict (or any unrecognized mode degrades to strict)
      end
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
         else $v
         end)
    end;

# ─── walk to enumerate diffs given canonical forms ───
def diffs(loc; e; a):
  if (e | type) == "object" and (a | type) == "object" then
    (((e | keys) + (a | keys)) | unique) as $ks
    | reduce $ks[] as $k (
        [];
        . + diffs(loc + "." + $k; e[$k] // null; a[$k] // null)
      )
  elif (e | type) == "array" and (a | type) == "array" then
    if (e | length) != (a | length) then
      [{ "path": loc, "kind": "array-length",
         "expected_len": (e | length), "actual_len": (a | length) }]
    else
      reduce range(0; e | length) as $i (
        [];
        . + diffs(loc + "[" + ($i | tostring) + "]"; e[$i]; a[$i])
      )
    end
  else
    if e == a then []
    else [{ "path": loc, "kind": "value-diff", "expected": e, "actual": a }]
    end
  end;

($pol["$root"] // $pol // {}) as $root_pol
| ($expected | canon($root_pol)) as $ec
| ($actual   | canon($root_pol)) as $ac
| diffs("$"; $ec; $ac)
| { "result": (if length == 0 then "pass" else "fail" end), "diffs": . }
')"

echo "$RESULT_JSON" | jq .

if echo "$RESULT_JSON" | jq -e '.result == "pass"' >/dev/null; then
  exit 0
else
  exit 1
fi
