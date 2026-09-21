"""catalog.py 의 파싱·매칭·병합 규칙.

판정 근거는 스크립트가 실제로 내놓은 값이다 — 임시 볼트 두 개를 만들어 sync/assign/build 를
그대로 부르고, 결과 catalog.json 과 HTML 을 읽는다.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "catalog.py"
STOP_HOOK = HERE.parent / "hooks" / "on-stop.sh"
sys.path.insert(0, str(SCRIPT.parent))
import catalog  # noqa: E402

LIST_TXT = """50 published artifacts (most recent first):
- (mine) 전란 영웅 시안 — 광개토대왕·양만춘 — https://claude.ai/artifact/RQNmrsP57cGkchgxjVhBGH — updated 2026-09-13
- (mine) 사태 — 컨셉 원화 — https://claude.ai/artifact/1wtQqVUuyuVMLfWp32ZLQs — updated 2026-09-13
- (mine) mrt-search PRD — https://claude.ai/artifact/MynhtQ5WKFQ5eGWC95MySt — updated 2026-09-18
- (mine) 새로 나온 것 — https://claude.ai/artifact/NEWNEWNEWNEWNEWNEWNEWN — updated 2026-09-18
- (mine) 파비콘 달린 것 — https://claude.ai/artifact/FAVFAVFAVFAVFAVFAVFAVF — favicon 🧠 — updated 2026-09-22
- (shared) 남의 것 — https://claude.ai/artifact/OTHEROTHEROTHEROTHER — updated 2026-09-18
(More may exist — pass a higher `limit` (up to 50).)
"""

INDEX_1989V = """---
title: 클로드 아티팩트 아카이브 (1989v)
---
| 발행 | 제목 | 노트 | 원본 |
|---|---|---|---|
| 2026-09-13 | 🏹 사태 컨셉 원화 | [[landslide-concept-art]] | [열기](https://claude.ai/code/artifact/07a9d8c2-3bda-402b-bc90-a4f7283096a4) |
| 2026-09-12 | 🏹 전란 영웅 시안 — 광개토대왕·양만춘 | [[jeonran-heroes]] | [열기](https://claude.ai/code/artifact/c59eda58-6f77-4a07-a736-92b75a70325e) |
| 2026-08-17 | 🏛️ K-Heritage — 1989v 디자인 시스템 | [[k-heritage-design-system]] | [열기](https://claude.ai/code/artifact/069f5785-4f06-442a-90fd-33a512fca1e7) |
"""

INDEX_WORK = """| 발행 | 제목 | 노트 | 원본 |
|---|---|---|---|
| 2026-09-17 | 🔍 mrt-search PRD v0.4 (검색 4레포 → 모노리스) | [[mrt-search-prd]] | [열기](https://claude.ai/artifact/MynhtQ5WKFQ5eGWC95MySt) |
"""


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.v1 = root / "1989v"
        self.v2 = root / "work"
        for v, idx in ((self.v1, INDEX_1989V), (self.v2, INDEX_WORK)):
            (v / "claude" / "artifact").mkdir(parents=True)
            (v / "claude" / "artifact" / "index.md").write_text(idx, encoding="utf-8")
        self.cfg = root / "config.json"
        self.cfg.write_text(json.dumps({
            "vaults": {"1989v": str(self.v1), "work": str(self.v2)},
            "pages": {
                "1989v": {"title": "1989v 아티팩트", "vault": "1989v"},
                "work": {"title": "work 아티팩트", "vault": "work"},
            },
        }), encoding="utf-8")
        self.list_txt = root / "list.txt"
        self.list_txt.write_text(LIST_TXT, encoding="utf-8")
        self.out = root / "out"
        self.queue = root / "queue.json"
        self.env = {**os.environ, "ARTIFACT_CATALOG_CONFIG": str(self.cfg),
                    "ARTIFACT_CATALOG_QUEUE": str(self.queue)}

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args, check=True):
        p = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                           text=True, env=self.env)
        if check and p.returncode != 0:
            self.fail(f"{args} failed:\n{p.stdout}\n{p.stderr}")
        return p

    def cat(self, vault):
        return json.loads((vault / "claude" / "artifact" / "catalog.json").read_text(encoding="utf-8"))

    # --- record · pending · queue (훅 경로) ------------------------------------
    def git_repo(self, origin):
        d = Path(self.tmp.name) / ("repo-" + origin.rsplit("/", 1)[-1])
        d.mkdir()
        subprocess.run(["git", "-C", str(d), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(d), "remote", "add", "origin", origin], check=True)
        return d

    def page_file(self, title):
        f = Path(self.tmp.name) / (title + ".html")
        f.write_text(f"<title>{title}</title>\n<style>body{{}}</style>\n<p>본문</p>", encoding="utf-8")
        return f

    def test_record_queues_with_title_from_file_and_vault_from_origin_owner(self):
        cfg = json.loads(self.cfg.read_text(encoding="utf-8"))
        cfg["owners"] = {"1989v": "1989v", "myrealtrip": "work"}
        self.cfg.write_text(json.dumps(cfg), encoding="utf-8")
        repo = self.git_repo("https://1989v@github.com/1989v/msa.git")
        f = self.page_file("검색 세 축 현황판")
        p = self.run_cli("record", "--url", "https://claude.ai/artifact/QUEUEQUEUEQUEUEQUEUEQU",
                         "--file", str(f), "--cwd", str(repo), "--favicon", "🚦", "--description", "현황")
        self.assertIn("queued QUEUEQUEUEQUEUEQUEUEQU · vault=1989v", p.stdout)
        q = json.loads(self.queue.read_text(encoding="utf-8"))
        self.assertEqual(1, len(q))
        self.assertEqual({"title": "검색 세 축 현황판", "vault": "1989v", "origin": "1989v", "icon": "🚦",
                          "summary": "현황", "source": "hook"},
                         {k: q[0][k] for k in ("title", "vault", "origin", "icon", "summary", "source")})
        # 회사 레포에서 발행하면 work — 볼트가 섞이지 않는다
        repo2 = self.git_repo("git@github.com:myrealtrip/mrt3-search.git")
        p = self.run_cli("record", "--url", "https://claude.ai/artifact/WORKWORKWORKWORKWORKWO",
                         "--file", str(f), "--cwd", str(repo2))
        self.assertIn("vault=work", p.stdout)
        # 레포 밖이면 미정 — 추정하지 않는다
        p = self.run_cli("record", "--url", "https://claude.ai/artifact/NOWHERENOWHERENOWHEREN",
                         "--file", str(f), "--cwd", self.tmp.name)
        self.assertIn("vault=?", p.stdout)
        self.assertEqual("3", self.run_cli("pending", "--quiet").stdout.strip())

    def test_record_skips_catalog_page_and_only_touches_updated_for_registered_ids(self):
        self.run_cli("sync", "--list", str(self.list_txt), "--out", str(self.out))
        pending = json.loads((self.out / "pending.json").read_text(encoding="utf-8"))
        for p in pending:
            p["vault"] = p["vault"] or "1989v"; p["project"] = "테스트"
        (self.out / "pending.json").write_text(json.dumps(pending), encoding="utf-8")
        self.run_cli("assign", str(self.out / "pending.json"))
        registered = self.cat(self.v1)["entries"][0]
        f = self.page_file(registered["title"])
        p = self.run_cli("record", "--url", registered["url"], "--file", str(f))
        self.assertIn("registered", p.stdout)
        self.assertFalse(self.queue.exists(), "등록된 것은 대기열에 안 들어간다")
        # 카탈로그 페이지 자신
        f = self.page_file("1989v 아티팩트")
        p = self.run_cli("record", "--url", "https://claude.ai/artifact/PAGEPAGEPAGEPAGEPAGEPA", "--file", str(f))
        self.assertIn("skip-self", p.stdout)
        self.assertFalse(self.queue.exists())

    def test_sync_surfaces_queue_items_and_assign_drains_them(self):
        f = self.page_file("훅으로만 들어온 것")
        self.run_cli("record", "--url", "https://claude.ai/artifact/HOOKONLYHOOKONLYHOOKON", "--file", str(f))
        # 목록에도 있는 것은 목록 행에 훅의 vault·icon 이 합쳐진다
        f2 = self.page_file("새로 나온 것")
        self.run_cli("record", "--url", "https://claude.ai/artifact/NEWNEWNEWNEWNEWNEWNEWN", "--file", str(f2),
                     "--favicon", "🆕")
        self.run_cli("sync", "--list", str(self.list_txt), "--out", str(self.out))
        pending = {p["id"]: p for p in json.loads((self.out / "pending.json").read_text(encoding="utf-8"))}
        self.assertEqual("hook", pending["HOOKONLYHOOKONLYHOOKON"]["source"])
        self.assertEqual("list", pending["NEWNEWNEWNEWNEWNEWNEWN"]["source"])
        self.assertEqual("🆕", pending["NEWNEWNEWNEWNEWNEWNEWN"]["icon"])
        self.assertEqual("2", self.run_cli("pending", "--quiet").stdout.strip())
        for p in pending.values():
            p["vault"] = p["vault"] or "1989v"; p["project"] = "테스트"
        (self.out / "pending.json").write_text(json.dumps(list(pending.values())), encoding="utf-8")
        self.run_cli("assign", str(self.out / "pending.json"))
        self.assertEqual("0", self.run_cli("pending", "--quiet").stdout.strip())
        self.assertEqual([], json.loads(self.queue.read_text(encoding="utf-8")))
        titles = {e["title"] for e in self.cat(self.v1)["entries"]}
        self.assertIn("훅으로만 들어온 것", titles)

    def test_queue_drop_is_the_only_way_out_without_registering(self):
        f = self.page_file("안 넣을 것")
        self.run_cli("record", "--url", "https://claude.ai/artifact/DROPDROPDROPDROPDROPDR", "--file", str(f))
        self.assertEqual("1", self.run_cli("pending", "--quiet").stdout.strip())
        self.run_cli("queue", "--drop", "DROPDROPDROPDROPDROPDR")
        self.assertEqual("0", self.run_cli("pending", "--quiet").stdout.strip())
        self.assertNotEqual(0, self.run_cli("queue", "--drop", "DROPDROPDROPDROPDROPDR", check=False).returncode)

    # --- 순수 함수 ---------------------------------------------------------
    def test_parse_list_reads_optional_favicon_segment(self):
        rows = {r["id"]: r for r in catalog.parse_list(LIST_TXT)}
        self.assertEqual(("파비콘 달린 것", "🧠", "2026-09-22"),
                         (rows["FAVFAVFAVFAVFAVFAVFAVF"]["title"], rows["FAVFAVFAVFAVFAVFAVFAVF"]["icon"],
                          rows["FAVFAVFAVFAVFAVFAVFAVF"]["updated"]))
        self.assertIsNone(rows["NEWNEWNEWNEWNEWNEWNEWN"]["icon"])

    def test_parse_list_keeps_mine_only_and_splits_title_with_dashes(self):
        rows = catalog.parse_list(LIST_TXT)
        self.assertEqual(5, len(rows))
        self.assertEqual("전란 영웅 시안 — 광개토대왕·양만춘", rows[0]["title"])
        self.assertEqual("RQNmrsP57cGkchgxjVhBGH", rows[0]["id"])
        self.assertEqual("2026-09-13", rows[0]["updated"])

    def test_parse_index_extracts_icon_note_and_id(self):
        rows = catalog.parse_index(INDEX_1989V)
        self.assertEqual("🏹", rows[0]["icon"])
        self.assertEqual("사태 컨셉 원화", rows[0]["title"])
        self.assertEqual("landslide-concept-art", rows[0]["note"])
        self.assertEqual("07a9d8c2-3bda-402b-bc90-a4f7283096a4", rows[0]["id"])
        self.assertEqual("🏛️", rows[2]["icon"])

    def test_norm_title_matches_dash_and_paren_variants(self):
        self.assertEqual(catalog.norm_title("사태 — 컨셉 원화"), catalog.norm_title("🏹 사태 컨셉 원화"))
        self.assertEqual(catalog.norm_title("검색 다음 세 갈래"),
                         catalog.norm_title("🔭 검색 다음 세 갈래 (09-10 발행 · 09-13 갱신)"))
        self.assertNotEqual(catalog.norm_title("mrt-search PRD"), catalog.norm_title("mrt-search PRD v0.4"))

    # --- sync: 첫 실행 --------------------------------------------------------
    def test_first_sync_places_index_matches_and_leaves_unknown_pending(self):
        p = self.run_cli("sync", "--list", str(self.list_txt), "--out", str(self.out))
        pending = json.loads((self.out / "pending.json").read_text(encoding="utf-8"))
        # 인덱스와 매칭된 셋은 볼트가 정해졌고 project 만 비어 있다
        by_id = {e["id"]: e for e in pending}
        self.assertEqual("1989v", by_id["1wtQqVUuyuVMLfWp32ZLQs"]["vault"])   # 제목 정규화 매칭
        self.assertEqual("2026-09-13", by_id["1wtQqVUuyuVMLfWp32ZLQs"]["published"])
        self.assertEqual("landslide-concept-art", by_id["1wtQqVUuyuVMLfWp32ZLQs"]["note"])
        self.assertEqual("07a9d8c2-3bda-402b-bc90-a4f7283096a4", by_id["1wtQqVUuyuVMLfWp32ZLQs"]["altId"])
        self.assertEqual("work", by_id["MynhtQ5WKFQ5eGWC95MySt"]["vault"])    # URL id 매칭
        self.assertEqual("2026-09-17", by_id["MynhtQ5WKFQ5eGWC95MySt"]["published"])
        self.assertEqual("2026-09-18", by_id["MynhtQ5WKFQ5eGWC95MySt"]["updated"])
        self.assertEqual("mrt-search PRD", by_id["MynhtQ5WKFQ5eGWC95MySt"]["title"])  # 제목은 list 것
        # 인덱스에만 있는 옛 것(창 밖)도 후보로 올라온다
        self.assertEqual("1989v", by_id["069f5785-4f06-442a-90fd-33a512fca1e7"]["vault"])
        self.assertEqual("index", by_id["069f5785-4f06-442a-90fd-33a512fca1e7"]["source"])
        # 어디에도 없는 것은 vault 도 비어 있다
        self.assertIsNone(by_id["NEWNEWNEWNEWNEWNEWNEWN"]["vault"])
        self.assertIn("새로 나온 것", p.stdout)
        # 남의 것은 안 들어온다
        self.assertNotIn("OTHEROTHEROTHEROTHER", by_id)
        # 아직 catalog.json 은 없다 — pending 을 assign 해야 쓴다
        self.assertFalse((self.v1 / "claude" / "artifact" / "catalog.json").exists())

    # --- assign → catalog.json ------------------------------------------------
    def assign_all(self):
        self.run_cli("sync", "--list", str(self.list_txt), "--out", str(self.out))
        pending = json.loads((self.out / "pending.json").read_text(encoding="utf-8"))
        for e in pending:
            e["project"] = "전란" if "전란" in e["title"] else "기타"
            if e["vault"] is None:
                e["vault"] = "work"
        (self.out / "pending.json").write_text(json.dumps(pending, ensure_ascii=False), encoding="utf-8")
        return self.run_cli("assign", str(self.out / "pending.json"))

    def test_assign_writes_each_vault_and_refuses_blank_project(self):
        self.assign_all()
        c1, c2 = self.cat(self.v1), self.cat(self.v2)
        ids1 = {e["id"] for e in c1["entries"]}
        ids2 = {e["id"] for e in c2["entries"]}
        self.assertEqual({"RQNmrsP57cGkchgxjVhBGH", "1wtQqVUuyuVMLfWp32ZLQs",
                          "069f5785-4f06-442a-90fd-33a512fca1e7"}, ids1)
        self.assertEqual({"MynhtQ5WKFQ5eGWC95MySt", "NEWNEWNEWNEWNEWNEWNEWN", "FAVFAVFAVFAVFAVFAVFAVF"}, ids2)
        # 빈 project 는 거부
        bad = self.out / "bad.json"
        bad.write_text(json.dumps([{"id": "X", "title": "x", "vault": "work", "project": "",
                                    "published": "2026-01-01", "updated": "2026-01-01",
                                    "url": "https://claude.ai/artifact/X"}]), encoding="utf-8")
        p = self.run_cli("assign", str(bad), check=False)
        self.assertNotEqual(0, p.returncode)
        self.assertIn("project", p.stderr)

    def test_second_sync_updates_dates_without_pending(self):
        self.assign_all()
        newer = LIST_TXT.replace("MynhtQ5WKFQ5eGWC95MySt — updated 2026-09-18",
                                 "MynhtQ5WKFQ5eGWC95MySt — updated 2026-09-20")
        self.list_txt.write_text(newer, encoding="utf-8")
        p = self.run_cli("sync", "--list", str(self.list_txt), "--out", str(self.out))
        pending = json.loads((self.out / "pending.json").read_text(encoding="utf-8"))
        self.assertEqual([], pending)
        e = next(x for x in self.cat(self.v2)["entries"] if x["id"] == "MynhtQ5WKFQ5eGWC95MySt")
        self.assertEqual("2026-09-20", e["updated"])
        self.assertEqual("2026-09-17", e["published"])   # 발행일은 안 움직인다
        self.assertIn("갱신 1", p.stdout)

    def test_same_as_merges_list_entry_with_index_row(self):
        # 목록 제목과 인덱스 제목이 달라 자동 매칭이 안 된 경우 — sameAs 로 잇는다
        (self.v1 / "claude" / "artifact" / "index.md").write_text(
            INDEX_1989V.replace("🏹 사태 컨셉 원화", "🏹 사태 원화 시안"), encoding="utf-8")
        self.run_cli("sync", "--list", str(self.list_txt), "--out", str(self.out))
        pending = json.loads((self.out / "pending.json").read_text(encoding="utf-8"))
        by_id = {e["id"]: e for e in pending}
        self.assertIsNone(by_id["1wtQqVUuyuVMLfWp32ZLQs"]["vault"])
        self.assertIn("07a9d8c2-3bda-402b-bc90-a4f7283096a4", by_id)  # 인덱스 행이 따로 떠 있다
        for e in pending:
            e["project"] = "p"
            e["vault"] = e["vault"] or "1989v"
        by_id["1wtQqVUuyuVMLfWp32ZLQs"]["sameAs"] = "07a9d8c2-3bda-402b-bc90-a4f7283096a4"
        (self.out / "pending.json").write_text(json.dumps(pending, ensure_ascii=False), encoding="utf-8")
        self.run_cli("assign", str(self.out / "pending.json"))
        entries = {e["id"]: e for e in self.cat(self.v1)["entries"]}
        self.assertNotIn("07a9d8c2-3bda-402b-bc90-a4f7283096a4", entries)   # 흡수됐다
        merged = entries["1wtQqVUuyuVMLfWp32ZLQs"]
        self.assertEqual("07a9d8c2-3bda-402b-bc90-a4f7283096a4", merged["altId"])
        self.assertEqual("landslide-concept-art", merged["note"])
        self.assertEqual("2026-09-13", merged["published"])

    # --- build ---------------------------------------------------------------
    def test_build_renders_public_and_all_pages_with_embedded_data(self):
        self.assign_all()
        self.run_cli("build", "--out", str(self.out))
        pub = (self.out / "1989v.html").read_text(encoding="utf-8")
        work = (self.out / "work.html").read_text(encoding="utf-8")
        self.assertIn("<title>1989v 아티팩트</title>", pub)
        self.assertIn("mrt-search PRD", work)
        self.assertNotIn("mrt-search PRD", pub)          # 회사 것은 개인 페이지에 없다
        self.assertNotIn("전란", work)                    # 개인 것은 회사 페이지에 없다
        self.assertNotIn("__DATA_JSON__", pub)
        data = json.loads(pub.split("id=\"catalog-data\"", 1)[1].split(">", 1)[1].split("</script>", 1)[0])
        self.assertEqual({"전란", "기타"}, {e["project"] for e in data["entries"]})
        self.assertEqual("1989v", data["vault"])

    def test_page_url_is_recorded_in_the_pages_own_vault(self):
        self.assign_all()
        self.run_cli("page-url", "work", "https://claude.ai/artifact/WORKWORK")
        self.assertEqual("https://claude.ai/artifact/WORKWORK", self.cat(self.v2)["pages"]["work"])
        self.assertNotIn("pages", self.cat(self.v1))
        p = self.run_cli("build", "--out", str(self.out))
        self.assertIn("work → https://claude.ai/artifact/WORKWORK", p.stdout)
        self.assertIn("1989v → (첫 발행)", p.stdout)

    def test_sync_skips_the_catalog_pages_themselves(self):
        # 카탈로그 페이지도 발행된 아티팩트라 다음 list 에 나타난다 — 등록부 후보로 올라오면 안 된다
        self.assign_all()
        self.run_cli("page-url", "1989v", "https://claude.ai/artifact/PAGE1989V")
        extra = LIST_TXT.replace("(More may exist",
                                 "- (mine) 1989v 아티팩트 — https://claude.ai/artifact/PAGE1989V — updated 2026-09-19\n"
                                 "- (mine) work 아티팩트 — https://claude.ai/artifact/PAGEWORKNOTYETRECORDED — updated 2026-09-19\n"
                                 "(More may exist")
        self.list_txt.write_text(extra, encoding="utf-8")
        p = self.run_cli("sync", "--list", str(self.list_txt), "--out", str(self.out))
        pending = json.loads((self.out / "pending.json").read_text(encoding="utf-8"))
        self.assertEqual([], pending)
        self.assertIn("카탈로그 페이지 2", p.stdout)

    def test_sync_skips_catalog_page_rows_that_live_only_in_index_md(self):
        # 볼트 사본 규칙이 index.md 에 카탈로그 페이지 행을 넣는다 — 목록 창 밖으로 밀린 뒤에도 후보로 올라오면 안 된다
        self.assign_all()
        self.run_cli("page-url", "work", "https://claude.ai/artifact/PAGEWORK")
        idx = self.v2 / "claude" / "artifact" / "index.md"
        idx.write_text(INDEX_WORK +
                       "| 2026-09-18 | 🗂️ work 아티팩트 (카탈로그) | [[artifact-catalog-work]] | [열기](https://claude.ai/artifact/PAGEWORK) |\n" +
                       "| 2026-09-18 | 🗂️ 1989v 아티팩트 (카탈로그 · 잘못 놓인 행) | [[x]] | [열기](https://claude.ai/code/artifact/00000000-0000-0000-0000-000000000000) |\n",
                       encoding="utf-8")
        self.run_cli("sync", "--list", str(self.list_txt), "--out", str(self.out))
        pending = json.loads((self.out / "pending.json").read_text(encoding="utf-8"))
        self.assertEqual([], pending)

    def test_sync_creates_the_out_dir(self):
        out = self.out / "nested" / "deeper"
        self.run_cli("sync", "--list", str(self.list_txt), "--out", str(out))
        self.assertTrue((out / "pending.json").exists())

    def test_config_cannot_put_two_vaults_on_one_page(self):
        # 회사·개인을 한 페이지에 섞는 설정은 구조적으로 불가능해야 한다 — 목록 필드도, 다른 볼트를 가리키는 페이지도 거부
        cfg = json.loads(self.cfg.read_text(encoding="utf-8"))
        cfg["pages"]["all"] = {"title": "전체", "vaults": ["1989v", "work"]}
        self.cfg.write_text(json.dumps(cfg), encoding="utf-8")
        p = self.run_cli("build", "--out", str(self.out), check=False)
        self.assertNotEqual(0, p.returncode)
        self.assertIn("vault", p.stderr)
        cfg["pages"] = {"1989v": {"title": "a", "vault": "1989v"}, "mixed": {"title": "b", "vault": "nope"}}
        self.cfg.write_text(json.dumps(cfg), encoding="utf-8")
        p = self.run_cli("build", "--out", str(self.out), check=False)
        self.assertNotEqual(0, p.returncode)
        self.assertIn("nope", p.stderr)




HOOK = HERE.parent / "hooks" / "on-artifact-publish.sh"
PUBLISH_TEXT = ("Published /tmp/x/report.html at https://claude.ai/artifact/AbCdEfGhIjKlMnOpQrStUv (Version 1) "
                "Icon: \"chart\".\n\nLive subscription: arming in the background …")


class HookTest(unittest.TestCase):
    """발행 직후 훅 — 대기열에 적고, 카탈로그에 넣으라는 지시를 세션에 넣는다. Stop 훅은 대기열이 남으면 종료를 막는다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "v" / "claude" / "artifact").mkdir(parents=True)
        self.cfg = root / "config.json"
        self.cfg.write_text(json.dumps({"vaults": {"1989v": str(root / "v")},
                                        "pages": {"1989v": {"title": "1989v 아티팩트", "vault": "1989v"}}}),
                            encoding="utf-8")
        self.queue = root / "queue.json"
        self.page = root / "report.html"
        self.page.write_text("<title>훅 검사 보고서</title><p>본문</p>", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, payload, env=None, hook=None):
        base = {"ARTIFACT_CATALOG_CONFIG": str(self.cfg), "ARTIFACT_CATALOG_QUEUE": str(self.queue)}
        p = subprocess.run(["bash", str(hook or HOOK)], input=json.dumps(payload), capture_output=True, text=True,
                           env={**os.environ, **base, **(env or {})})
        return p

    def stop(self, active=False):
        return self.run_hook({"session_id": "s1", "hook_event_name": "Stop", "stop_hook_active": active},
                             hook=STOP_HOOK)

    def test_publish_records_into_queue_and_stop_hook_blocks_until_registered(self):
        payload = self.publish(); payload["tool_input"]["file_path"] = str(self.page)
        payload["tool_response"] = PUBLISH_TEXT.replace("/tmp/x/report.html", str(self.page))
        p = self.run_hook(payload)
        self.assertEqual(0, p.returncode, p.stderr)
        self.assertIn("대기열: queued AbCdEfGhIjKlMnOpQrStUv", p.stdout)
        q = json.loads(self.queue.read_text(encoding="utf-8"))
        self.assertEqual([("AbCdEfGhIjKlMnOpQrStUv", "훅 검사 보고서")], [(x["id"], x["title"]) for x in q])
        # 대기열이 남아 있으면 세션 종료를 막는다 — 빨간불
        out = json.loads(self.stop().stdout)
        self.assertEqual("block", out["decision"])
        self.assertIn("훅 검사 보고서", out["reason"])
        self.assertIn("/artifact-catalog", out["reason"])
        # 이미 한 번 막아 이어진 턴은 통과(무한 루프 방지) · 끄기 스위치 · 대기열 제거 뒤엔 통과
        self.assertEqual("", self.stop(active=True).stdout.strip())
        self.assertEqual("", self.run_hook({"hook_event_name": "Stop"}, env={"ARTIFACT_CATALOG_STOP_GATE": "off"},
                                           hook=STOP_HOOK).stdout.strip())
        self.queue.write_text("[]", encoding="utf-8")
        self.assertEqual("", self.stop().stdout.strip())

    def test_stop_hook_is_silent_without_config(self):
        p = self.run_hook({"hook_event_name": "Stop"}, env={"ARTIFACT_CATALOG_CONFIG": str(Path(self.tmp.name) / "none.json")},
                          hook=STOP_HOOK)
        self.assertEqual(0, p.returncode)
        self.assertEqual("", p.stdout.strip())

    def publish(self, **tool_input):
        return {"session_id": "s1", "hook_event_name": "PostToolUse", "tool_name": "Artifact",
                "tool_input": {"file_path": "/tmp/x/report.html", **tool_input}, "tool_response": PUBLISH_TEXT}

    def test_publish_emits_additional_context_with_url_and_skill_name(self):
        p = self.run_hook(self.publish())
        self.assertEqual(0, p.returncode, p.stderr)
        out = json.loads(p.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual("PostToolUse", out["hookSpecificOutput"]["hookEventName"])
        self.assertIn("/artifact-catalog", ctx)
        self.assertIn("https://claude.ai/artifact/AbCdEfGhIjKlMnOpQrStUv", ctx)

    def test_republish_with_url_still_nudges(self):
        p = self.run_hook(self.publish(url="https://claude.ai/artifact/AbCdEfGhIjKlMnOpQrStUv"))
        self.assertIn("/artifact-catalog", p.stdout)

    def test_silent_on_non_publish_actions_and_assets(self):
        for payload in (
            {**self.publish(), "tool_input": {"action": "list"}, "tool_response": "50 published artifacts…"},
            {**self.publish(), "tool_input": {"action": "read", "url": "https://claude.ai/artifact/X"}},
            self.publish(asset=True, url="https://claude.ai/artifact/X"),
            {**self.publish(), "tool_name": "Write", "tool_response": {"filePath": "/tmp/x/report.html"}},
        ):
            p = self.run_hook(payload)
            self.assertEqual(0, p.returncode, p.stderr)
            self.assertEqual("", p.stdout.strip(), payload["tool_input"])

    def test_silent_when_the_catalog_page_itself_is_published(self):
        # 카탈로그 재발행이 또 카탈로그를 돌리라고 하면 끝이 없다
        for path in ("/scratch/artifact-catalog/1989v.html", "/scratch/artifact-catalog/work.html"):
            payload = self.publish(); payload["tool_input"]["file_path"] = path
            payload["tool_response"] = PUBLISH_TEXT.replace("/tmp/x/report.html", path)
            self.assertEqual("", self.run_hook(payload).stdout.strip(), path)

    def test_trace_log_records_every_invocation_when_asked(self):
        # 라이브 발화 증명용 — 발행이 아니어도(list) 한 줄은 남긴다
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "hook.log"
            self.run_hook({**self.publish(), "tool_input": {"action": "list"}, "tool_response": "…"},
                          env={"ARTIFACT_CATALOG_HOOK_LOG": str(log)})
            self.run_hook(self.publish(), env={"ARTIFACT_CATALOG_HOOK_LOG": str(log)})
            lines = log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(2, len(lines))
            self.assertIn("Artifact list", lines[0])
            self.assertIn("nudge", lines[1])


if __name__ == "__main__":
    unittest.main()
