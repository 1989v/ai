#!/usr/bin/env bash
#
# snapshot.sh — manage goldset snapshot directories
#
# Subcommands:
#   create-baseline {skill-id} [tag]    # New baseline snapshot dir, returns path
#   create-run      {skill-id} [tag]    # New after-fix snapshot dir, returns path
#   current         {skill-id}          # Print path of current baseline (resolves symlink)
#   promote         {skill-id} {snap}   # Move `current` symlink to {snap}
#   list            {skill-id}          # List snapshots (chronological)
#
# Resolves goldset root from the first existing of:
#   $SKILL_EVAL_GOLDSET_ROOT, $PWD/goldset, $PWD/.goldset

set -euo pipefail

usage() {
  sed -n '3,20p' "$0" >&2
  exit 64
}

resolve_goldset_root() {
  if [[ -n "${SKILL_EVAL_GOLDSET_ROOT:-}" ]]; then
    echo "$SKILL_EVAL_GOLDSET_ROOT"; return
  fi
  if [[ -d "$PWD/goldset" ]]; then
    echo "$PWD/goldset"; return
  fi
  if [[ -d "$PWD/.goldset" ]]; then
    echo "$PWD/.goldset"; return
  fi
  echo "$PWD/goldset"  # default; caller may need to mkdir
}

skill_dir() {
  local skill_id="${1:?skill-id required}"
  local goldset_root
  goldset_root="$(resolve_goldset_root)"
  echo "$goldset_root/${skill_id//:/-}"
}

today_iso() { date -u +"%Y-%m-%d"; }

cmd_create_baseline() {
  local skill_id="${1:?skill-id required}"
  local tag="${2:-baseline}"
  local sdir; sdir="$(skill_dir "$skill_id")"
  local snap_id="$(today_iso)-${tag}"
  local snap_dir="$sdir/snapshots/$snap_id"

  if [[ -e "$snap_dir" ]]; then
    echo "snapshot already exists: $snap_dir" >&2
    return 1
  fi

  mkdir -p "$snap_dir"/{source-skill,forked-skill,cases}
  echo "$snap_dir"
}

cmd_create_run() {
  local skill_id="${1:?skill-id required}"
  local tag="${2:-auto-$(date -u +%H%M%S)}"
  local sdir; sdir="$(skill_dir "$skill_id")"
  local snap_id="$(today_iso)-${tag}"
  local snap_dir="$sdir/snapshots/$snap_id"

  # Ensure unique
  local seq=1
  while [[ -e "$snap_dir" ]]; do
    snap_id="$(today_iso)-${tag}-${seq}"
    snap_dir="$sdir/snapshots/$snap_id"
    seq=$((seq + 1))
  done

  mkdir -p "$snap_dir"/{source-skill,forked-skill,cases}
  echo "$snap_dir"
}

cmd_current() {
  local skill_id="${1:?skill-id required}"
  local sdir; sdir="$(skill_dir "$skill_id")"
  local link="$sdir/current"
  if [[ ! -L "$link" ]]; then
    echo "no current baseline set for $skill_id (expected symlink at $link)" >&2
    return 1
  fi
  # Resolve to absolute path
  local target; target="$(readlink "$link")"
  if [[ "$target" = /* ]]; then
    echo "$target"
  else
    echo "$sdir/$target"
  fi
}

cmd_promote() {
  local skill_id="${1:?skill-id required}"
  local snap="${2:?snapshot-id required}"
  local sdir; sdir="$(skill_dir "$skill_id")"
  local snap_dir="$sdir/snapshots/$snap"

  if [[ ! -d "$snap_dir" ]]; then
    echo "snapshot not found: $snap_dir" >&2
    return 1
  fi

  local link="$sdir/current"
  # Use relative target so the goldset is portable
  (cd "$sdir" && ln -sfn "snapshots/$snap" current)
  echo "promoted: $skill_id -> $snap"
  echo "current symlink: $link -> snapshots/$snap"
}

cmd_list() {
  local skill_id="${1:?skill-id required}"
  local sdir; sdir="$(skill_dir "$skill_id")"
  if [[ ! -d "$sdir/snapshots" ]]; then
    echo "no snapshots yet" >&2
    return 0
  fi
  local cur=""
  if [[ -L "$sdir/current" ]]; then
    cur="$(basename "$(readlink "$sdir/current")")"
  fi
  for d in "$sdir"/snapshots/*/; do
    [[ -d "$d" ]] || continue
    local name
    name="$(basename "$d")"
    local marker=""
    [[ "$name" = "$cur" ]] && marker="  (current baseline)"
    echo "$name$marker"
  done | sort
}

main() {
  local cmd="${1:-}"; shift || true
  case "$cmd" in
    create-baseline) cmd_create_baseline "$@" ;;
    create-run)      cmd_create_run "$@" ;;
    current)         cmd_current "$@" ;;
    promote)         cmd_promote "$@" ;;
    list)            cmd_list "$@" ;;
    -h|--help|"")    usage ;;
    *)               echo "unknown subcommand: $cmd" >&2; usage ;;
  esac
}

main "$@"
