"""intake · budget · 힉스필드 훅의 게이트 동작.

판정 근거는 스크립트가 실제로 내놓은 값이다 — 임시 홈에 작업을 만들고 종료 코드·파일·훅 JSON 을 읽는다.
훅은 「승인 없음 → deny」를 먼저 보고(빨간불), 승인 뒤 통과·차감·소진·만료를 본다.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zlib
import struct
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INTAKE = ROOT / "scripts" / "intake.py"
BUDGET = ROOT / "scripts" / "budget.py"
GUARD = ROOT / "hooks" / "guard-higgsfield.py"


def png(path, w=640, h=960, rgb=(200, 170, 150)):
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def run(cmd, **kw):
    return subprocess.run([sys.executable, *map(str, cmd)], capture_output=True, text=True, **kw)


def hook(tool, env):
    p = subprocess.run([sys.executable, str(GUARD)], input=json.dumps({"tool_name": tool, "tool_input": {}}),
                       capture_output=True, text=True, env=env)
    return json.loads(p.stdout)["hookSpecificOutput"] if p.stdout.strip() else None


class IntakeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.home = self.tmp / "home"
        self.photo = self.tmp / "kid.png"
        png(self.photo)
        self.video = self.tmp / "ref.mp4"
        self.video.write_bytes(b"\x00" * 1024)  # 길이는 못 읽는다 → 경고만

    def test_missing_ref_video_blocks_and_creates_nothing(self):
        p = run([INTAKE, "new", "--genre", "shortform-transform", "--slug", "kid", "--home", self.home,
                 "--source", self.photo])
        self.assertEqual(p.returncode, 2, p.stderr)
        self.assertIn("ref_video", p.stderr)
        self.assertFalse(self.home.exists())

    def test_complete_intake_copies_and_points_current_job(self):
        p = run([INTAKE, "new", "--genre", "shortform-transform", "--slug", "Kid Party", "--home", self.home,
                 "--source", self.photo, "--ref-video", self.video, "--concept", "마법소녀"])
        self.assertEqual(p.returncode, 0, p.stderr)
        job = Path((self.home / ".current-job").read_text().strip())
        self.assertTrue(job.name.endswith("-kid-party"))
        self.assertTrue((job / "inputs" / "source-01.png").is_file())
        self.assertTrue((job / "inputs" / "ref-video.mp4").is_file())
        m = json.loads((job / "job.json").read_text())
        self.assertEqual(m["inputs"]["source"][0]["width"], 640)
        self.assertTrue(any("자리 표시자" in w for w in m["warnings"]))   # 3.8KB 단색 PNG
        self.assertIn("외부 서버", p.stdout)

    def test_requirements_table_lists_required_first(self):
        p = run([INTAKE, "requirements", "--genre", "game-background"])
        self.assertEqual(p.returncode, 0)
        self.assertIn("**필수** | `concept`", p.stdout)
        self.assertIn("**필수** | `aspect`", p.stdout)


class BudgetTest(unittest.TestCase):
    def setUp(self):
        self.job = Path(tempfile.mkdtemp())
        self.plan = self.job / "plan.json"
        self.plan.write_text(json.dumps([
            {"stage": "IMAGE 1", "model": "nano-banana-pro", "count": 2},
            {"stage": "IMAGE 2", "model": "nano-banana-pro", "count": 2},
            {"stage": "모션", "model": "genjutsu-motion-transfer-720p-15s", "count": 1},
        ]))

    def test_estimate_totals_and_files(self):
        p = run([BUDGET, "estimate", "--provider", "higgsfield", "--plan", self.plan, "--job", self.job,
                 "--krw-per-usd", "1400"])
        self.assertEqual(p.returncode, 0, p.stderr)
        est = json.loads((self.job / "estimate.json").read_text())
        self.assertEqual(est["planned_credits"], 168.0)          # (4+4+104) × 1.5
        self.assertEqual(est["planned_calls"], 8)                # ceil(5 × 1.5)
        self.assertEqual(est["usd"], 10.5)                       # 168 × 0.0625
        self.assertEqual(est["krw"], 14700)
        self.assertIn("₩0 경로", (self.job / "estimate.md").read_text())

    def test_unknown_model_exits_4(self):
        self.plan.write_text(json.dumps([{"stage": "x", "model": "made-up", "count": 1}]))
        p = run([BUDGET, "estimate", "--provider", "higgsfield", "--plan", self.plan])
        self.assertEqual(p.returncode, 4)

    def test_stale_pricing_exits_3(self):
        p = run([BUDGET, "estimate", "--provider", "higgsfield", "--plan", self.plan, "--max-age-days", "-1"])
        self.assertEqual(p.returncode, 3)
        self.assertIn("검증일", p.stderr)

    def test_approve_requires_estimate_and_caps_calls(self):
        p = run([BUDGET, "approve", "--job", self.job, "--calls", "3", "--answer", "a"])
        self.assertEqual(p.returncode, 5)
        run([BUDGET, "estimate", "--provider", "higgsfield", "--plan", self.plan, "--job", self.job])
        p = run([BUDGET, "approve", "--job", self.job, "--calls", "99", "--answer", "a"])
        self.assertEqual(p.returncode, 5)
        p = run([BUDGET, "approve", "--job", self.job, "--calls", "3", "--answer", "a 로 진행"])
        self.assertEqual(p.returncode, 0, p.stderr)
        rec = json.loads((self.job / "approval.json").read_text())
        self.assertEqual(rec["remaining_calls"], 3)
        self.assertTrue(rec["approved_by_user"])


class GuardHookTest(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.job = self.home / "2026-09-21-kid"
        self.job.mkdir()
        self.env = {**os.environ, "MEDIA_GEN_HOME": str(self.home)}

    def approve(self, calls, approved_at=None):
        (self.home / ".current-job").write_text(str(self.job))
        (self.job / "approval.json").write_text(json.dumps({
            "approved_by_user": True, "remaining_calls": calls, "approved_calls": calls,
            "approved_at": (approved_at or datetime.now()).isoformat(timespec="seconds")}))

    def test_red_no_job_pointer_denies(self):
        out = hook("mcp__higgsfield__generate_video", self.env)
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("허락 절차", out["permissionDecisionReason"])

    def test_red_job_without_approval_denies(self):
        (self.home / ".current-job").write_text(str(self.job))
        out = hook("mcp__higgsfield__generate_image", self.env)
        self.assertEqual(out["permissionDecision"], "deny")

    def test_read_only_passes_silently(self):
        self.assertIsNone(hook("mcp__higgsfield__get_generation_status", self.env))
        self.assertIsNone(hook("mcp__higgsfield__list_characters", self.env))
        self.assertIsNone(hook("mcp__higgsfield__get_balance", self.env))

    def test_ambiguous_name_is_paid(self):
        out = hook("mcp__higgsfield__generate_and_animate", self.env)   # generate 가 있으면 조회가 아니다
        self.assertEqual(out["permissionDecision"], "deny")
        out = hook("mcp__higgsfield__soul_character", self.env)         # 모르는 이름 → 유료
        self.assertEqual(out["permissionDecision"], "deny")

    def test_green_approved_calls_decrement_then_exhaust(self):
        self.approve(2)
        out = hook("mcp__higgsfield__generate_image", self.env)
        self.assertEqual(out["permissionDecision"], "allow")
        self.assertIn("남은 승인 1회", out["additionalContext"])
        out = hook("mcp__higgsfield__generate_video", self.env)
        self.assertEqual(out["permissionDecision"], "allow")
        out = hook("mcp__higgsfield__generate_video", self.env)
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("다 썼다", out["permissionDecisionReason"])
        rec = json.loads((self.job / "approval.json").read_text())
        self.assertEqual(rec["remaining_calls"], 0)
        self.assertEqual(len(rec["calls"]), 2)

    def test_expired_approval_denies(self):
        self.approve(5, approved_at=datetime.now() - timedelta(hours=25))
        out = hook("mcp__higgsfield__generate_image", self.env)
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("24시간", out["permissionDecisionReason"])

    def test_other_servers_untouched(self):
        self.assertIsNone(hook("mcp__github__create_issue", self.env))


if __name__ == "__main__":
    unittest.main()
