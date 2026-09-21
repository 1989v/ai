#!/usr/bin/env bash
# on-artifact-publish.sh — PostToolUse(Artifact) 훅
#
# 아티팩트가 발행되면 두 가지를 한다.
#   1. `catalog.py record` 로 **대기열에 적는다** — 셸에서 결정론적으로. 목록 50건 창과 무관하게 남고,
#      작업 레포의 origin 소유자로 볼트를 미리 채운다(설정 owners). 이미 등록된 것이면 갱신일만 올린다.
#   2. "이 세션이 끝나기 전에 /artifact-catalog 를 돌려라" 를 세션 컨텍스트에 넣는다 — 카탈로그 페이지는
#      Artifact 도구로만 다시 발행되므로 이 절반은 세션 몫이다. on-stop.sh 가 대기열이 빌 때까지 세션 종료를 막는다.
#
# 침묵하는 경우: publish 가 아닌 action(list/read/…) · 에셋 업로드 · 카탈로그 페이지 자신의 재발행.
# 설정(~/.claude/artifact-catalog.json)이 없으면 1 은 건너뛰고 2 만 한다.
# ARTIFACT_CATALOG_HOOK_LOG=<파일> 이 있으면 호출마다 한 줄 남긴다 (발화 증명용).
set -uo pipefail
command -v jq >/dev/null 2>&1 || exit 0
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CAT="$HERE/../scripts/catalog.py"

payload=$(cat)
tool=$(jq -r '.tool_name // empty' <<<"$payload")
[ "$tool" = "Artifact" ] || exit 0

action=$(jq -r '.tool_input.action // "publish"' <<<"$payload")
asset=$(jq -r '.tool_input.asset // false' <<<"$payload")
file=$(jq -r '.tool_input.file_path // empty' <<<"$payload")
cwd=$(jq -r '.cwd // empty' <<<"$payload")
favicon=$(jq -r '.tool_input.favicon // empty' <<<"$payload")
desc=$(jq -r '.tool_input.description // empty' <<<"$payload")
resp=$(jq -r '.tool_response | if type == "string" then . else tostring end' <<<"$payload")
url=$(grep -oE 'https://claude\.ai/artifact/[A-Za-z0-9]+' <<<"$resp" | head -1)

trace() { [ -n "${ARTIFACT_CATALOG_HOOK_LOG:-}" ] && printf '%s Artifact %s %s\n' "$(date +%FT%T)" "$action" "$1" >>"$ARTIFACT_CATALOG_HOOK_LOG"; return 0; }

if [ "$action" != "publish" ] || [ "$asset" = "true" ] || [ -z "$url" ]; then
  trace "skip"; exit 0
fi
case "$file" in */artifact-catalog/*.html) trace "skip-self"; exit 0 ;; esac

# 1. 대기열 — 설정이 없거나 스크립트가 실패해도 지시(2)는 낸다
record=""
if command -v python3 >/dev/null 2>&1; then
  args=(record --url "$url" --file "$file" --cwd "$cwd")
  [ -n "$favicon" ] && args+=(--favicon "$favicon")
  [ -n "$desc" ] && args+=(--description "$desc")
  record=$(python3 "$CAT" "${args[@]}" 2>/dev/null | tail -1) || record=""
fi
case "$record" in skip-self*) trace "skip-self"; exit 0 ;; esac

trace "nudge $url ${record:-no-record}"
jq -cn --arg url "$url" --arg rec "$record" '{
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    additionalContext: ("[artifact-catalog] 아티팩트가 발행됐다: " + $url +
      (if $rec == "" then " (대기열 기록 실패 — 설정 ~/.claude/artifact-catalog.json 확인)" else " — 대기열: " + $rec end) +
      ". 카탈로그 페이지는 정적이라 /artifact-catalog 를 돌려야 들어간다 — 대기열이 남아 있으면 세션을 끝낼 수 없다." +
      " 같은 세션에서 여러 번 발행해도 마지막에 한 번이면 된다. 카탈로그에 안 넣을 것이면 catalog.py queue --drop <id>.")
  }
}'
