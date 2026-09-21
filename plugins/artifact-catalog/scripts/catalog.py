#!/usr/bin/env python3
"""발행한 클로드 아티팩트의 등록부(catalog.json)를 볼트별로 유지하고, 카탈로그 페이지 HTML 을 만든다.

표준 라이브러리만 쓴다.

    catalog.py sync --list list.txt --out DIR   # Artifact list 출력 + 볼트 index.md 대조 → 갱신 반영, pending.json
    catalog.py assign DIR/pending.json          # vault·project 를 채운 pending 을 catalog.json 에 넣는다
    catalog.py build --out DIR                  # 페이지별 HTML 생성 (데이터 인라인)
    catalog.py page-url PAGE URL                # 첫 발행 뒤 페이지 URL 을 기록 (재발행 시 같은 URL)
    catalog.py record --url U --file F --cwd D  # (훅) 발행 직후 대기열에 넣는다 — 목록 50건 창과 무관하게 남는다
    catalog.py pending [--quiet]                # (Stop 훅) 등록부에 아직 없는 대기열 항목 — 있으면 세션을 못 끝낸다
    catalog.py queue --list | --drop ID         # 대기열 확인·수동 제거(카탈로그에 안 넣기로 한 것)

설정: $ARTIFACT_CATALOG_CONFIG 또는 ~/.claude/artifact-catalog.json
    { "vaults": { "<name>": "<path>" },
      "pages":  { "<page>": { "title": "...", "vault": "<name>" } },
      "owners": { "<github owner>": "<name>" } }   # (선택) 작업 레포의 origin 소유자 → 볼트. 훅이 vault 를 미리 채운다

대기열: $ARTIFACT_CATALOG_QUEUE 또는 ~/.claude/artifact-catalog.queue.json — 훅이 쓰고 assign 이 비운다.

볼트마다 <path>/claude/artifact/catalog.json 이 등록부다. index.md(발행일·노트·이모지)는 읽기만 한다.
**페이지는 볼트 하나만 담는다** — 회사·개인 아티팩트가 한 페이지에 섞이는 설정은 여기서 거부한다.
페이지 URL 은 그 볼트 catalog.json 의 pages 에 둔다.
"""
import argparse
import datetime
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "templates" / "catalog.html"
REL = Path("claude") / "artifact"

LIST_RE = re.compile(r"^- \((\w+)\) (.+?) — (https?://\S+) — updated (\d{4}-\d{2}-\d{2})\s*$")
INDEX_RE = re.compile(
    r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)\s*\|\s*(?:\[\[([^\]|]+)(?:\|[^\]]*)?\]\])?[^|]*\|\s*\[[^\]]*\]\((https?://[^)\s]+)\)"
)
ENTRY_KEYS = ["id", "url", "altId", "altUrl", "title", "icon", "project", "published",
              "updated", "note", "tags", "summary"]


# --- 파싱 ---------------------------------------------------------------------
def id_from_url(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


def norm_title(title):
    """매칭용 정규화 — 앞 이모지·뒤 괄호 주석을 떼고 기호·공백을 전부 지운다."""
    s = re.sub(r"^[^\w]+", "", title.strip())
    while True:
        t = re.sub(r"\s*\([^()]*\)\s*$", "", s)
        if t == s:
            break
        s = t
    return re.sub(r"[^\w]", "", s).lower()


def extract_icon(title):
    m = re.match(r"^([^\w]+)", title.strip())
    icon = m.group(1).strip() if m else ""
    return icon or None


def strip_icon(title):
    return re.sub(r"^[^\w]+", "", title.strip())


def parse_list(text):
    rows = []
    for line in text.splitlines():
        m = LIST_RE.match(line.strip())
        if not m or m.group(1) != "mine":
            continue
        url = m.group(3)
        rows.append({"id": id_from_url(url), "url": url, "title": m.group(2).strip(),
                     "updated": m.group(4)})
    return rows


def parse_index(text):
    rows = []
    for line in text.splitlines():
        m = INDEX_RE.match(line.strip())
        if not m:
            continue
        raw = m.group(2)
        url = m.group(4)
        rows.append({"id": id_from_url(url), "url": url, "title": strip_icon(raw),
                     "icon": extract_icon(raw), "note": m.group(3), "published": m.group(1)})
    return rows


# --- 설정·파일 -------------------------------------------------------------------
def load_config():
    path = Path(os.environ.get("ARTIFACT_CATALOG_CONFIG") or Path.home() / ".claude" / "artifact-catalog.json")
    if not path.exists():
        sys.exit(f"설정이 없다: {path}\n{__doc__.split('설정:')[1]}")
    cfg = json.loads(path.read_text(encoding="utf-8"))
    cfg["vaults"] = {k: Path(os.path.expanduser(v)) for k, v in cfg["vaults"].items()}
    for page, spec in cfg["pages"].items():
        if "vaults" in spec or not isinstance(spec.get("vault"), str):
            sys.exit(f"pages.{page}: 페이지는 vault 하나만 갖는다 — 여러 볼트를 한 페이지에 섞을 수 없다")
        if spec["vault"] not in cfg["vaults"]:
            sys.exit(f"pages.{page}.vault 가 모르는 볼트다: {spec['vault']!r} (vaults: {list(cfg['vaults'])})")
    for owner, vault in cfg.get("owners", {}).items():
        if vault not in cfg["vaults"]:
            sys.exit(f"owners.{owner} 가 모르는 볼트다: {vault!r} (vaults: {list(cfg['vaults'])})")
    return cfg


def queue_path():
    return Path(os.environ.get("ARTIFACT_CATALOG_QUEUE") or Path.home() / ".claude" / "artifact-catalog.queue.json")


def load_queue():
    p = queue_path()
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def save_queue(items):
    write_json(queue_path(), items)


def catalog_path(cfg, vault):
    return cfg["vaults"][vault] / REL / "catalog.json"


def load_catalog(cfg, vault):
    p = catalog_path(cfg, vault)
    if not p.exists():
        return {"entries": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save_catalog(cfg, vault, cat):
    cat["entries"].sort(key=lambda e: (e.get("published") or "", e.get("title") or ""), reverse=True)
    cat["entries"] = [{k: e[k] for k in ENTRY_KEYS if e.get(k) not in (None, [], "")} for e in cat["entries"]]
    ordered = {k: cat[k] for k in ("pages", "entries") if k in cat}
    p = catalog_path(cfg, vault)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_index(cfg, vault):
    p = cfg["vaults"][vault] / REL / "index.md"
    return parse_index(p.read_text(encoding="utf-8")) if p.exists() else []


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# --- sync ------------------------------------------------------------------------
class Lookup:
    """기존 항목을 id·altId·정규화 제목으로 찾는다."""

    def __init__(self, catalogs):
        self.by_id, self.by_title = {}, {}
        for vault, cat in catalogs.items():
            for e in cat["entries"]:
                self.by_id[e["id"]] = (vault, e)
                if e.get("altId"):
                    self.by_id[e["altId"]] = (vault, e)
                self.by_title.setdefault(norm_title(e["title"]), (vault, e))

    def find(self, row):
        return self.by_id.get(row["id"]) or self.by_title.get(norm_title(row["title"]))


def cmd_sync(args):
    cfg = load_config()
    list_rows = parse_list(Path(args.list).read_text(encoding="utf-8"))
    catalogs = {v: load_catalog(cfg, v) for v in cfg["vaults"]}
    indexes = {v: load_index(cfg, v) for v in cfg["vaults"]}
    lookup = Lookup(catalogs)
    changed, pending, matched_index_ids = set(), [], set()
    # 카탈로그 페이지 자체도 발행물이라 목록에 나타난다 — 기록된 URL 이나 설정의 제목으로 거른다
    page_ids = {id_from_url(u) for cat in catalogs.values() for u in cat.get("pages", {}).values()}
    page_titles = {norm_title(spec["title"]) for spec in cfg["pages"].values()}
    skipped_pages = 0

    def find_index(row):
        nt = norm_title(row["title"])
        for vault, rows in indexes.items():
            for r in rows:
                if r["id"] == row["id"] or norm_title(r["title"]) == nt:
                    return vault, r
        return None

    def is_catalog_page(row):
        return row["id"] in page_ids or norm_title(row["title"]) in page_titles

    updated = 0
    for row in list_rows:
        if is_catalog_page(row):
            skipped_pages += 1
            continue
        hit = lookup.find(row)
        if hit:
            vault, e = hit
            before = json.dumps(e, sort_keys=True)
            if e["id"] != row["id"]:            # 인덱스(uuid)로 들어온 항목이 목록(short id)에 나타났다
                e["altId"], e["altUrl"] = e["id"], e["url"]
                e["id"], e["url"] = row["id"], row["url"]
            e["title"] = row["title"]
            e["updated"] = max(e.get("updated") or "", row["updated"])
            e["published"] = e.get("published") or row["updated"]
            if json.dumps(e, sort_keys=True) != before:
                changed.add(vault)
                updated += 1
            continue
        item = {"id": row["id"], "url": row["url"], "title": row["title"], "vault": None,
                "project": None, "published": row["updated"], "updated": row["updated"],
                "source": "list"}
        ih = find_index(row)
        if ih:
            vault, r = ih
            matched_index_ids.add(r["id"])
            item.update({"vault": vault, "published": r["published"], "note": r["note"],
                         "icon": r["icon"]})
            if r["id"] != row["id"]:
                item["altId"], item["altUrl"] = r["id"], r["url"]
        pending.append(item)

    # 훅이 발행 직후 넣어 둔 것 — 목록 창과 무관하게 남아 있다. 이미 등록된 것은 여기서 대기열에서 뺀다
    queue, kept = load_queue(), []
    by_pending_id = {p["id"]: p for p in pending}
    for q in queue:
        if lookup.find(q) or is_catalog_page(q):
            continue
        kept.append(q)
        target = by_pending_id.get(q["id"])
        if target is None:
            target = {"id": q["id"], "url": q["url"], "title": q["title"], "vault": None, "project": None,
                      "published": q.get("published"), "updated": q.get("updated") or q.get("published"),
                      "source": "hook"}
            pending.append(target)
            by_pending_id[q["id"]] = target
        for k in ("vault", "icon", "summary"):
            target[k] = target.get(k) or q.get(k)
    if len(kept) != len(queue):
        save_queue(kept)

    # 목록 창 밖으로 밀린 것 — 인덱스에만 남아 있다
    for vault, rows in indexes.items():
        for r in rows:
            if r["id"] in matched_index_ids or lookup.find(r) or is_catalog_page(r):
                continue
            pending.append({"id": r["id"], "url": r["url"], "title": r["title"], "icon": r["icon"],
                            "note": r["note"], "vault": vault, "project": None,
                            "published": r["published"], "updated": r["published"], "source": "index"})

    for vault in changed:
        save_catalog(cfg, vault, catalogs[vault])
    out = Path(args.out)
    write_json(out / "pending.json", pending)

    unassigned = sum(1 for p in pending if p["vault"] is None)
    print(f"목록 {len(list_rows)}건 · 카탈로그 페이지 {skipped_pages} 제외 · 갱신 {updated} · 신규 후보 {len(pending)} (볼트 미정 {unassigned})")
    if pending:
        print(f"\n채울 것 → {out / 'pending.json'} (project 필수 · vault 가 null 이면 채운다 · 같은 아티팩트면 sameAs)")
        print("\n| vault | published | source | id | title |\n|---|---|---|---|---|")
        for p in pending:
            print(f"| {p['vault'] or '?'} | {p['published']} | {p['source']} | {p['id']} | {p['title']} |")
    projects = {}
    for vault, cat in catalogs.items():
        for e in cat["entries"]:
            projects.setdefault(vault, {}).setdefault(e["project"], 0)
            projects[vault][e["project"]] += 1
    if projects:
        print("\n쓰던 프로젝트명:")
        for vault, ps in projects.items():
            print(f"  {vault}: " + " · ".join(f"{k}({n})" for k, n in sorted(ps.items(), key=lambda x: -x[1])))


# --- assign ----------------------------------------------------------------------
def cmd_assign(args):
    cfg = load_config()
    pending = json.loads(Path(args.pending).read_text(encoding="utf-8"))
    for p in pending:
        if not (p.get("project") or "").strip():
            sys.exit(f"project 가 비어 있다: {p['id']} {p['title']}")
        if p.get("vault") not in cfg["vaults"]:
            sys.exit(f"vault 가 비어 있거나 모르는 값이다: {p['id']} {p['title']} → {p.get('vault')}")
    catalogs = {v: load_catalog(cfg, v) for v in cfg["vaults"]}
    by_id = {p["id"]: p for p in pending}

    def take_existing(entry_id):
        for vault, cat in catalogs.items():
            for e in cat["entries"]:
                if e["id"] == entry_id or e.get("altId") == entry_id:
                    cat["entries"].remove(e)
                    return e
        return None

    absorbed = set()
    for p in pending:
        target_id = p.pop("sameAs", None)
        if not target_id:
            continue
        target = by_id.get(target_id) or take_existing(target_id)
        if target is None:
            sys.exit(f"sameAs 대상을 못 찾았다: {p['id']} → {target_id}")
        absorbed.add(target_id)
        p["altId"], p["altUrl"] = target["id"], target["url"]
        for k in ("note", "icon", "summary", "tags"):
            p[k] = p.get(k) or target.get(k)
        p["published"] = min(p["published"], target.get("published") or p["published"])
        p["updated"] = max(p["updated"], target.get("updated") or p["updated"])

    counts = {}
    for p in pending:
        if p["id"] in absorbed:
            continue
        vault = p["vault"]
        take_existing(p["id"])
        entry = {k: p.get(k) for k in ENTRY_KEYS}
        catalogs[vault]["entries"].append(entry)
        counts[vault] = counts.get(vault, 0) + 1
    for vault, cat in catalogs.items():
        save_catalog(cfg, vault, cat)
    registered = {e["id"] for cat in catalogs.values() for e in cat["entries"]}
    registered |= {e["altId"] for cat in catalogs.values() for e in cat["entries"] if e.get("altId")}
    queue = load_queue()
    left = [q for q in queue if q["id"] not in registered]
    if len(left) != len(queue):
        save_queue(left)
    print("반영: " + (" · ".join(f"{v} +{n}" for v, n in counts.items()) or "0"))
    for vault, cat in catalogs.items():
        print(f"  {vault}: {len(cat['entries'])}건 → {catalog_path(cfg, vault)}")


# --- build -----------------------------------------------------------------------
def cmd_build(args):
    cfg = load_config()
    template = TEMPLATE.read_text(encoding="utf-8")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    for page, spec in cfg["pages"].items():
        vault = spec["vault"]
        cat = load_catalog(cfg, vault)      # 이 페이지의 볼트 하나만 읽는다
        entries = sorted(cat["entries"], key=lambda e: (e.get("published") or "", e["title"]), reverse=True)
        data = {"page": page, "title": spec["title"], "generated": today,
                "vault": vault, "entries": entries}
        payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        html = (template.replace("__TITLE__", spec["title"]).replace("__GENERATED__", today)
                .replace("__DATA_JSON__", payload))
        (out / f"{page}.html").write_text(html, encoding="utf-8")
        url = cat.get("pages", {}).get(page)
        print(f"{page} → {url or '(첫 발행)'} · {len(entries)}건 · {out / f'{page}.html'}")


def cmd_page_url(args):
    cfg = load_config()
    if args.page not in cfg["pages"]:
        sys.exit(f"모르는 페이지: {args.page} (설정: {list(cfg['pages'])})")
    vault = cfg["pages"][args.page]["vault"]
    cat = load_catalog(cfg, vault)
    cat.setdefault("pages", {})[args.page] = args.url
    save_catalog(cfg, vault, cat)
    print(f"{args.page} → {args.url} ({catalog_path(cfg, vault)})")


# --- record · pending · queue (훅이 부른다) ------------------------------------------
def read_title(path):
    """발행 파일의 <title> — Artifact 도구가 이름으로 쓰는 것과 같다(앞 8KB). 없으면 None."""
    try:
        head = Path(path).read_text(encoding="utf-8", errors="replace")[:8192]
    except OSError:
        return None
    m = re.search(r"<title>(.*?)</title>", head, re.S | re.I)
    return html.unescape(m.group(1)).strip() or None if m else None


def origin_owner(cwd):
    """작업 폴더 레포의 origin 소유자(github.com/<owner>/…). 레포 밖이면 None."""
    if not cwd:
        return None
    try:
        out = subprocess.run(["git", "-C", cwd, "remote", "get-url", "origin"], capture_output=True,
                             text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"github\.com[:/]([^/\s]+)/", out.stdout.strip())
    return m.group(1).lower() if m else None


def registered_ids(catalogs):
    ids = set()
    for cat in catalogs.values():
        for e in cat["entries"]:
            ids.add(e["id"])
            if e.get("altId"):
                ids.add(e["altId"])
    return ids


def cmd_record(args):
    cfg = load_config()
    catalogs = {v: load_catalog(cfg, v) for v in cfg["vaults"]}
    entry_id = id_from_url(args.url)
    title = args.title or read_title(args.file) or Path(args.file).stem
    page_ids = {id_from_url(u) for cat in catalogs.values() for u in cat.get("pages", {}).values()}
    page_titles = {norm_title(spec["title"]) for spec in cfg["pages"].values()}
    if entry_id in page_ids or norm_title(title) in page_titles:
        print(f"skip-self {entry_id}")
        return
    today = datetime.date.today().isoformat()
    for vault, cat in catalogs.items():
        for e in cat["entries"]:
            if entry_id in (e["id"], e.get("altId")):
                e["updated"] = max(e.get("updated") or "", today)
                save_catalog(cfg, vault, cat)
                print(f"registered {entry_id} · {vault} · updated={e['updated']}")
                return
    owner = origin_owner(args.cwd)
    vault = cfg.get("owners", {}).get(owner) or (owner if owner in cfg["vaults"] else None)
    queue = [q for q in load_queue() if q["id"] != entry_id]
    queue.append({"id": entry_id, "url": args.url, "title": title, "icon": args.favicon or None,
                  "summary": args.description or None, "vault": vault, "origin": owner,
                  "published": today, "updated": today, "source": "hook"})
    save_queue(queue)
    print(f"queued {entry_id} · vault={vault or '?'} · {title}")


def pending_items(cfg):
    catalogs = {v: load_catalog(cfg, v) for v in cfg["vaults"]}
    done = registered_ids(catalogs)
    queue = load_queue()
    left = [q for q in queue if q["id"] not in done]
    if len(left) != len(queue):
        save_queue(left)
    return left


def cmd_pending(args):
    left = pending_items(load_config())
    if args.quiet:
        print(len(left))
        return
    for q in left:
        print(f"{q['id']} · {q.get('vault') or '?'} · {q['title']} · {q['url']}")
    print(f"{len(left)}건 대기")


def cmd_queue(args):
    queue = load_queue()
    if args.drop:
        left = [q for q in queue if q["id"] != args.drop]
        if len(left) == len(queue):
            sys.exit(f"대기열에 없다: {args.drop}")
        save_queue(left)
        print(f"dropped {args.drop} ({len(left)}건 남음)")
        return
    for q in queue:
        print(f"{q['id']} · {q.get('vault') or '?'} · {q['title']} · {q['url']}")
    print(f"{len(queue)}건 · {queue_path()}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync"); s.add_argument("--list", required=True); s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_sync)
    a = sub.add_parser("assign"); a.add_argument("pending"); a.set_defaults(fn=cmd_assign)
    b = sub.add_parser("build"); b.add_argument("--out", required=True); b.set_defaults(fn=cmd_build)
    u = sub.add_parser("page-url"); u.add_argument("page"); u.add_argument("url"); u.set_defaults(fn=cmd_page_url)
    r = sub.add_parser("record"); r.add_argument("--url", required=True); r.add_argument("--file", required=True)
    r.add_argument("--cwd", default=""); r.add_argument("--title"); r.add_argument("--favicon"); r.add_argument("--description")
    r.set_defaults(fn=cmd_record)
    pd = sub.add_parser("pending"); pd.add_argument("--quiet", action="store_true"); pd.set_defaults(fn=cmd_pending)
    q = sub.add_parser("queue"); q.add_argument("--list", action="store_true"); q.add_argument("--drop"); q.set_defaults(fn=cmd_queue)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
