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
sys.path.insert(0, str(SCRIPT.parent))
import catalog  # noqa: E402

LIST_TXT = """50 published artifacts (most recent first):
- (mine) 전란 영웅 시안 — 광개토대왕·양만춘 — https://claude.ai/artifact/RQNmrsP57cGkchgxjVhBGH — updated 2026-09-13
- (mine) 사태 — 컨셉 원화 — https://claude.ai/artifact/1wtQqVUuyuVMLfWp32ZLQs — updated 2026-09-13
- (mine) mrt-search PRD — https://claude.ai/artifact/MynhtQ5WKFQ5eGWC95MySt — updated 2026-09-18
- (mine) 새로 나온 것 — https://claude.ai/artifact/NEWNEWNEWNEWNEWNEWNEWN — updated 2026-09-18
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
        self.env = {**os.environ, "ARTIFACT_CATALOG_CONFIG": str(self.cfg)}

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

    # --- 순수 함수 ---------------------------------------------------------
    def test_parse_list_keeps_mine_only_and_splits_title_with_dashes(self):
        rows = catalog.parse_list(LIST_TXT)
        self.assertEqual(4, len(rows))
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
        self.assertEqual({"MynhtQ5WKFQ5eGWC95MySt", "NEWNEWNEWNEWNEWNEWNEWN"}, ids2)
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


if __name__ == "__main__":
    unittest.main()
