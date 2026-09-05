#!/usr/bin/env bash
# hns:kb — 프로젝트 밖 지식베이스(Obsidian LLM Wiki 볼트)를 읽기 전용으로 조회한다.
#   kb-search.sh --status                 볼트 이름 · 페이지 수 · 마지막 ingest 제목 (한 줄)
#   kb-search.sh <keyword>...             wiki/index.md 에서 키워드가 맞는 줄을 점수순으로 (최대 8줄)
#   kb-search.sh --page <name>            페이지 파일 경로 + updated 날짜
# 설정: HNS_KB_PATH (환경변수 > .claude/hns-hooks.env). 없으면 아무것도 내지 않고 exit 0.
set -u
PROJECT="${CLAUDE_PROJECT_DIR:-$PWD}"; ENV_FILE="$PROJECT/.claude/hns-hooks.env"
KB="${HNS_KB_PATH:-}"
if [ -z "$KB" ] && [ -f "$ENV_FILE" ]; then
  KB=$(sed -n 's/^HNS_KB_PATH=//p' "$ENV_FILE" | head -1 | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
fi
[ -z "$KB" ] && exit 0
KB="${KB/#\~/$HOME}"; KB="${KB//\$HOME/$HOME}"
if [ ! -f "$KB/wiki/index.md" ]; then
  [ -f "$KB/wiki/.index.md.icloud" ] && echo "KB is evicted from iCloud ($KB/wiki) — open the folder in Finder to download" >&2
  exit 0
fi
exec python3 - "$KB" "$@" <<'PY'
import os, re, sys, glob
kb = sys.argv[1]; args = sys.argv[2:]
wiki = os.path.join(kb, "wiki"); name = os.path.basename(kb.rstrip("/"))
def pages():  # wiki/ 가 우선, raw/ 기록 페이지도 조회 가능 (읽기 전용)
    out = {}
    for base in (os.path.join(kb, "raw"), wiki):
        for p in glob.glob(os.path.join(base, "**", "*.md"), recursive=True):
            out[os.path.splitext(os.path.basename(p))[0]] = p
    return out
def updated(path):
    try:
        head = open(path, encoding="utf-8").read(600)
    except Exception:
        return "?"
    m = re.search(r"^updated:\s*(\S+)", head, re.M); return m.group(1) if m else "?"
if args[:1] == ["--status"]:
    n = len(glob.glob(os.path.join(wiki, "**", "*.md"), recursive=True)); last = ""
    try:
        for line in open(os.path.join(wiki, "log.md"), encoding="utf-8"):
            if line.startswith("## ["): last = line.strip()
    except Exception: pass
    last = re.sub(r"^## \[[^\]]*\]\s*\S+\s*\|\s*", "", re.sub(r"\s*→.*$", "", last))[:120]
    print(f"KB {name}: {n} pages · last: {last or '(no log)'}"); sys.exit(0)
if args[:1] == ["--page"] and len(args) > 1:
    p = pages().get(args[1])
    print(f"{p}\t{updated(p)}" if p else f"(not found) {args[1]}", file=sys.stdout if p else sys.stderr); sys.exit(0 if p else 1)
kws = [a.lower() for a in args if a.strip()]
if not kws: sys.exit(0)
pg = pages(); hits = []
for line in open(os.path.join(wiki, "index.md"), encoding="utf-8"):
    s = line.strip()
    if not s.startswith("-") or "[[" not in s: continue
    low = s.lower(); score = sum(1 for k in kws if k in low)
    if score == 0: continue
    m = re.search(r"\[\[([^\]|#]+)", s); page = m.group(1).strip() if m else ""
    summary = re.sub(r"^-\s*\[\[[^\]]+\]\]\s*[—-]?\s*", "", s)
    hits.append((score, page, updated(pg.get(page, "")) if page in pg else "?", summary[:160]))
hits.sort(key=lambda h: (-h[0], h[1]))
for score, page, upd, summary in hits[:8]:
    print(f"{score}\t{page}\t{upd}\t{summary}")
PY
