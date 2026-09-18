#!/usr/bin/env bash
# on-artifact-publish.sh — PostToolUse(Artifact) 훅
#
# 아티팩트가 발행되면 "이 세션이 끝나기 전에 /artifact-catalog 를 돌려라" 를 세션 컨텍스트에 넣는다.
# 카탈로그 페이지는 데이터를 안에 박은 정적 HTML 이라 돌려야 새 항목이 들어가고,
# Artifact list 는 최근 50건 창이라 미루면 앞의 것부터 등록부에 못 들어간다.
#
# 훅이 sync 자체를 대신하지는 않는다 — Artifact list 는 클로드 도구라 셸에서 부를 수 없다.
# 침묵하는 경우: publish 가 아닌 action(list/read/…) · 에셋 업로드 · 카탈로그 페이지 자신의 재발행.
# ARTIFACT_CATALOG_HOOK_LOG=<파일> 이 있으면 호출마다 한 줄 남긴다 (발화 증명용).
set -uo pipefail
command -v jq >/dev/null 2>&1 || exit 0

payload=$(cat)
tool=$(jq -r '.tool_name // empty' <<<"$payload")
[ "$tool" = "Artifact" ] || exit 0

action=$(jq -r '.tool_input.action // "publish"' <<<"$payload")
asset=$(jq -r '.tool_input.asset // false' <<<"$payload")
file=$(jq -r '.tool_input.file_path // empty' <<<"$payload")
resp=$(jq -r '.tool_response | if type == "string" then . else tostring end' <<<"$payload")
url=$(grep -oE 'https://claude\.ai/artifact/[A-Za-z0-9]+' <<<"$resp" | head -1)

trace() { [ -n "${ARTIFACT_CATALOG_HOOK_LOG:-}" ] && printf '%s Artifact %s %s\n' "$(date +%FT%T)" "$action" "$1" >>"$ARTIFACT_CATALOG_HOOK_LOG"; return 0; }

if [ "$action" != "publish" ] || [ "$asset" = "true" ] || [ -z "$url" ]; then
  trace "skip"; exit 0
fi
case "$file" in */artifact-catalog/*.html) trace "skip-self"; exit 0 ;; esac

trace "nudge $url"
jq -cn --arg url "$url" '{
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    additionalContext: ("[artifact-catalog] 아티팩트가 발행됐다: " + $url +
      " — 이 세션이 끝나기 전에 /artifact-catalog 를 한 번 돌려 등록부와 카탈로그 페이지에 넣는다" +
      " (페이지는 정적이라 돌려야 들어가고, Artifact list 는 50건 창이라 미루면 앞의 것부터 잃는다)." +
      " 같은 세션에서 여러 번 발행해도 마지막에 한 번이면 된다.")
  }
}'
