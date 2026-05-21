#!/usr/bin/env bash
# verify-source.sh — Check whether a file:line citation contains the expected text.
#
# Usage:
#   verify-source.sh <path> <line>               # single line
#   verify-source.sh <path> <start> <end>        # line range
#   verify-source.sh --match <path> <start> <end> <expected_substr>
#
# Exit codes:
#   0  — file/line exists (and substring matched if provided)
#   1  — file missing
#   2  — line out of range
#   3  — substring mismatch
#
# When invoked without --match, prints the extracted line range to stdout.

set -euo pipefail

MATCH_MODE=0
if [[ "${1:-}" == "--match" ]]; then
  MATCH_MODE=1
  shift
fi

PATH_ARG="${1:-}"
START="${2:-}"
END="${3:-$START}"
EXPECTED="${4:-}"

if [[ -z "$PATH_ARG" || -z "$START" ]]; then
  echo "usage: verify-source.sh [--match] <path> <start> [end] [expected]" >&2
  exit 64
fi

if [[ ! -f "$PATH_ARG" ]]; then
  exit 1
fi

# Validate integers
if ! [[ "$START" =~ ^[0-9]+$ ]] || ! [[ "$END" =~ ^[0-9]+$ ]]; then
  exit 64
fi

TOTAL=$(wc -l < "$PATH_ARG")
if (( START < 1 || END > TOTAL || START > END )); then
  exit 2
fi

EXTRACTED=$(sed -n "${START},${END}p" "$PATH_ARG")

if (( MATCH_MODE == 1 )); then
  if [[ -z "$EXPECTED" ]]; then
    echo "usage: verify-source.sh --match <path> <start> <end> <expected>" >&2
    exit 64
  fi
  # Normalize whitespace + markdown leaders for both
  norm() {
    sed -E 's/^[[:space:]]*[-*#0-9.]+[[:space:]]*//; s/[[:space:]]+/ /g; s/^ //; s/ $//' \
      | tr '[:upper:]' '[:lower:]'
  }
  EXTRACTED_NORM=$(printf "%s" "$EXTRACTED" | norm)
  EXPECTED_NORM=$(printf "%s" "$EXPECTED" | norm)

  if [[ "$EXTRACTED_NORM" == *"$EXPECTED_NORM"* ]]; then
    exit 0
  fi

  # Trigram overlap fallback (80% threshold)
  trigrams() {
    local s="$1"
    local n=${#s}
    local i
    for (( i=0; i<n-2; i++ )); do
      printf "%s\n" "${s:$i:3}"
    done | sort -u
  }
  EXP_TG=$(trigrams "$EXPECTED_NORM")
  EXT_TG=$(trigrams "$EXTRACTED_NORM")
  if [[ -z "$EXP_TG" ]]; then exit 3; fi
  COMMON=$(comm -12 <(echo "$EXP_TG") <(echo "$EXT_TG") | wc -l | tr -d ' ')
  TOTAL_TG=$(echo "$EXP_TG" | wc -l | tr -d ' ')
  if (( TOTAL_TG == 0 )); then exit 3; fi
  # 80% threshold
  THRESH=$(( TOTAL_TG * 8 / 10 ))
  if (( COMMON >= THRESH )); then
    exit 0
  fi
  exit 3
fi

printf "%s\n" "$EXTRACTED"
exit 0
