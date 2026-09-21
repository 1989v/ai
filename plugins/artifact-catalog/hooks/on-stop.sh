#!/usr/bin/env bash
# on-stop.sh — Stop 훅
#
# 발행됐는데 아직 카탈로그 등록부에 없는 아티팩트(대기열)가 있으면 세션 종료를 막고 /artifact-catalog 를 돌리게 한다.
# 「지시만 넣는」 훅은 지켜지지 않았다 — 발행한 세션이 그냥 끝나면 다음 세션의 list 50건 창에서 밀려 사라진다.
#
# 막지 않는 경우: stop_hook_active(이미 한 번 막아 이어진 턴 — 무한 루프 방지) · ARTIFACT_CATALOG_STOP_GATE=off ·
# 설정이 없음 · 대기열 비어 있음. 카탈로그에 안 넣기로 한 것은 `catalog.py queue --drop <id>` 로 뺀다.
set -uo pipefail
command -v jq >/dev/null 2>&1 || exit 0
command -v python3 >/dev/null 2>&1 || exit 0
[ "${ARTIFACT_CATALOG_STOP_GATE:-on}" != "off" ] || exit 0
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CAT="$HERE/../scripts/catalog.py"

payload=$(cat)
[ "$(jq -r '.stop_hook_active // false' <<<"$payload")" = "true" ] && exit 0

n=$(python3 "$CAT" pending --quiet 2>/dev/null) || exit 0
case "$n" in ''|*[!0-9]*) exit 0 ;; esac
[ "$n" -gt 0 ] || exit 0

lines=$(python3 "$CAT" pending 2>/dev/null | head -6)
jq -cn --arg n "$n" --arg lines "$lines" '{
  decision: "block",
  reason: ("[artifact-catalog] 카탈로그에 아직 안 들어간 아티팩트 " + $n + "건이 있다:\n" + $lines +
    "\n/artifact-catalog 를 돌려 등록부·카탈로그 페이지에 넣은 뒤 끝낸다. 넣지 않을 것이면 catalog.py queue --drop <id>.")
}'
