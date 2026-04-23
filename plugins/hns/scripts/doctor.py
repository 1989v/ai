#!/usr/bin/env python3
"""
doctor.py — 프로젝트 문서/하네스 헬스체크.

4-layer weighted diagnostic. 각 레이어는 여러 체크를 수행하고
PASS / WARN / FAIL 판정을 낸다. 종합 스코어(0-100) 계산.

  L1 Index Integrity   (weight 30) — docs/index.yml + 등록된 파일 존재 + orphan
  L2 Agent Guidance    (weight 25) — CLAUDE.md + 필수 섹션
  L3 Harness Alignment (weight 25) — 네이밍/링크 규약 + 스테일 산출물
  L4 Evidence Coverage (weight 20) — spec/standard의 source 인용 유무

Exit codes:
  0  PASS
  1  FAIL (또는 --strict 시 WARN → FAIL)
  2  WARN (non-strict)

Python 3 stdlib only. YAML이 없으면 간이 파서로 docs/index.yml을 읽는다.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

SEV_PASS = "PASS"
SEV_WARN = "WARN"
SEV_FAIL = "FAIL"
SEV_ORDER = {SEV_PASS: 0, SEV_WARN: 1, SEV_FAIL: 2}

LAYERS = [
    ("L1", "Index Integrity", 30),
    ("L2", "Agent Guidance", 25),
    ("L3", "Harness Alignment", 25),
    ("L4", "Evidence Coverage", 20),
]

SOURCE_CITATION_RE = re.compile(r"<!--\s*source:\s*([^\s>]+)\s*-->")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass
class Finding:
    layer: str
    severity: str
    code: str
    title: str
    path: str | None = None
    hint: str | None = None


@dataclass
class LayerResult:
    id: str
    name: str
    weight: int
    status: str = SEV_PASS
    findings: list[Finding] = field(default_factory=list)

    def record(self, f: Finding) -> None:
        self.findings.append(f)
        if SEV_ORDER[f.severity] > SEV_ORDER[self.status]:
            self.status = f.severity


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def _iter_md(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.md"):
        if any(seg.startswith(".") for seg in p.parts):
            continue
        yield p


def _strip_code_blocks(text: str) -> str:
    """fenced(``` or ~~~) + inline(`) 코드 블록 제거 — 링크 오탐 방지용."""
    lines = text.splitlines()
    out = []
    in_fence = False
    fence_marker = ""
    for line in lines:
        stripped = line.lstrip()
        if in_fence:
            if stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = True
            fence_marker = stripped[:3]
            continue
        out.append(line)
    joined = "\n".join(out)
    return re.sub(r"`[^`\n]+`", "", joined)


def _parse_simple_yaml_list(text: str, key: str) -> list[str]:
    """매우 단순한 YAML 시퀀스 파서 — `key:` 하위 `- path/to/file` 항목만 추출."""
    out: list[str] = []
    in_block = False
    indent = 0
    for line in text.splitlines():
        stripped = line.lstrip()
        if not in_block:
            if stripped.startswith(f"{key}:"):
                in_block = True
                indent = len(line) - len(stripped)
            continue
        if not line.strip():
            continue
        cur_indent = len(line) - len(stripped)
        if cur_indent <= indent and not stripped.startswith("-"):
            break
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            item = item.strip("'\"")
            if ":" in item:
                for frag in item.split():
                    if frag.endswith(".md") or frag.endswith(".yml"):
                        item = frag.strip("'\",")
                        break
            out.append(item)
    return out


def layer1_index_integrity(root: Path, layer: LayerResult) -> None:
    index_path = root / "docs" / "index.yml"
    if not index_path.exists():
        layer.record(Finding(layer.id, SEV_FAIL, "L1-01", "docs/index.yml missing",
                             "docs/index.yml",
                             "run `/hns:init` or create a minimal index"))
        return

    text = _read_text(index_path)
    if not text.strip():
        layer.record(Finding(layer.id, SEV_FAIL, "L1-02", "docs/index.yml is empty",
                             "docs/index.yml"))
        return

    registered = _parse_simple_yaml_list(text, "documents")
    registered += _parse_simple_yaml_list(text, "docs")

    missing = []
    for item in registered:
        if not item.endswith(".md"):
            continue
        target = root / item if not item.startswith("docs/") else root / item
        if not (root / item).exists():
            missing.append(item)

    if missing:
        for m in missing[:10]:
            layer.record(Finding(layer.id, SEV_FAIL, "L1-10",
                                 "registered doc not found", m,
                                 "remove from index.yml or restore the file"))
        if len(missing) > 10:
            layer.record(Finding(layer.id, SEV_WARN, "L1-10",
                                 f"... and {len(missing) - 10} more missing entries"))

    docs_root = root / "docs"
    if docs_root.exists():
        on_disk = {str(p.relative_to(root)) for p in _iter_md(docs_root)}
        registered_set = set(registered)
        orphans = sorted(on_disk - registered_set)
        orphans = [o for o in orphans if "/legacies/" not in o and "/verify/" not in o]
        if orphans:
            for o in orphans[:10]:
                layer.record(Finding(layer.id, SEV_WARN, "L1-20",
                                     "doc not registered in index.yml", o,
                                     "add it under documents: or move to docs/legacies/"))
            if len(orphans) > 10:
                layer.record(Finding(layer.id, SEV_WARN, "L1-20",
                                     f"... and {len(orphans) - 10} more unregistered docs"))


def layer2_agent_guidance(root: Path, layer: LayerResult) -> None:
    claude_md = root / "CLAUDE.md"
    agents_md = root / "AGENTS.md"
    if not claude_md.exists():
        layer.record(Finding(layer.id, SEV_FAIL, "L2-01",
                             "CLAUDE.md missing at repo root",
                             "CLAUDE.md",
                             "run `/hns:init` or create a root agent guide"))
    else:
        text = _read_text(claude_md)
        if len(text.strip()) < 40:
            layer.record(Finding(layer.id, SEV_WARN, "L2-02",
                                 "CLAUDE.md is suspiciously short",
                                 "CLAUDE.md"))
        lowered = text.lower()
        if "build" not in lowered and "test" not in lowered and "run" not in lowered:
            layer.record(Finding(layer.id, SEV_WARN, "L2-03",
                                 "CLAUDE.md lacks build/test/run guidance",
                                 "CLAUDE.md",
                                 "add a Build or Commands section"))

    if not agents_md.exists() and not claude_md.exists():
        layer.record(Finding(layer.id, SEV_WARN, "L2-10",
                             "neither AGENTS.md nor CLAUDE.md present"))


def layer3_harness_alignment(root: Path, layer: LayerResult) -> None:
    broken = []
    for md in _iter_md(root):
        rel = md.relative_to(root)
        rel_str = str(rel)
        if rel_str.startswith(("docs/legacies/", "docs/verify/")):
            continue
        # plugin 내부 templates/ 는 사용자 프로젝트용 placeholder → 링크 검사 제외
        parts = rel.parts
        if "templates" in parts:
            continue
        text = _strip_code_blocks(_read_text(md))
        for m in MD_LINK_RE.finditer(text):
            target = m.group(2).split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if "{" in target or target.endswith("...") or target in {"url", "path"}:
                continue
            if target.startswith("/"):
                candidate = root / target.lstrip("/")
            else:
                candidate = (md.parent / target).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                continue
            if not candidate.exists():
                broken.append((str(rel), target))
                if len(broken) > 30:
                    break
        if len(broken) > 30:
            break

    for src, tgt in broken[:15]:
        layer.record(Finding(layer.id, SEV_FAIL, "L3-01", "broken internal link",
                             f"{src} -> {tgt}",
                             "fix the link or remove the reference"))
    if len(broken) > 15:
        layer.record(Finding(layer.id, SEV_WARN, "L3-01",
                             f"... and {len(broken) - 15} more broken links"))

    report = root / "harness-gc-report.md"
    if report.exists():
        age_days = (datetime.now(timezone.utc).timestamp() - report.stat().st_mtime) / 86400
        if age_days > 30:
            layer.record(Finding(layer.id, SEV_WARN, "L3-10",
                                 f"harness-gc-report.md is {int(age_days)} days old",
                                 "harness-gc-report.md",
                                 "run `/hns:gc` to refresh"))


def layer4_evidence_coverage(root: Path, layer: LayerResult) -> None:
    spec_roots = [root / "docs" / "specs", root / "docs" / "standards"]
    candidates = []
    for sr in spec_roots:
        if sr.exists():
            candidates.extend(_iter_md(sr))
    if not candidates:
        layer.record(Finding(layer.id, SEV_PASS, "L4-00",
                             "no spec/standard docs to evaluate"))
        return

    uncited = []
    for md in candidates:
        text = _read_text(md)
        if not SOURCE_CITATION_RE.search(text):
            uncited.append(str(md.relative_to(root)))

    total = len(candidates)
    missing = len(uncited)
    coverage = 1.0 - (missing / total) if total else 1.0
    if coverage < 0.5:
        severity = SEV_FAIL
    elif coverage < 0.8:
        severity = SEV_WARN
    else:
        severity = SEV_PASS

    if severity != SEV_PASS:
        for u in uncited[:10]:
            layer.record(Finding(layer.id, severity, "L4-01",
                                 "doc lacks `<!-- source: ... -->` citation", u,
                                 "add a source citation referencing the originating code"))
        if len(uncited) > 10:
            layer.record(Finding(layer.id, severity, "L4-01",
                                 f"... and {len(uncited) - 10} more uncited docs"))


def run_layers(root: Path) -> list[LayerResult]:
    results = [LayerResult(id=i, name=n, weight=w) for i, n, w in LAYERS]
    layer1_index_integrity(root, results[0])
    layer2_agent_guidance(root, results[1])
    layer3_harness_alignment(root, results[2])
    layer4_evidence_coverage(root, results[3])
    return results


def compute_score(results: list[LayerResult]) -> int:
    total_weight = sum(r.weight for r in results)
    score = 0.0
    for r in results:
        factor = 1.0 if r.status == SEV_PASS else 0.6 if r.status == SEV_WARN else 0.0
        score += r.weight * factor
    return round(100 * score / total_weight)


def overall_status(results: list[LayerResult], strict: bool) -> str:
    worst = max((SEV_ORDER[r.status] for r in results), default=0)
    sev = [k for k, v in SEV_ORDER.items() if v == worst][0]
    if strict and sev == SEV_WARN:
        return SEV_FAIL
    return sev


def format_text(results: list[LayerResult], score: int, status: str) -> str:
    lines = [
        f"# Doctor Report ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')})",
        "",
        f"**Score**: {score} / 100",
        f"**Status**: {status}",
        "",
    ]
    for r in results:
        lines.append(f"[Layer {r.id}/{len(results)}] {r.name} .......... {r.status}")
    lines.append("")
    for r in results:
        if not r.findings:
            continue
        lines.append(f"## {r.id} — {r.name}")
        for f in r.findings:
            loc = f" `{f.path}`" if f.path else ""
            hint = f" _({f.hint})_" if f.hint else ""
            lines.append(f"- [{f.severity} {f.code}] {f.title}{loc}{hint}")
        lines.append("")
    return "\n".join(lines)


def format_json(results: list[LayerResult], score: int, status: str) -> str:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "score": score,
        "status": status,
        "layers": [
            {
                "id": r.id,
                "name": r.name,
                "weight": r.weight,
                "status": r.status,
                "findings": [asdict(f) for f in r.findings],
            }
            for r in results
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def install_precommit_hook(root: Path, shell_path: Path) -> None:
    proc = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--git-dir"],
        text=True, capture_output=True, check=False,
    )
    if proc.returncode != 0:
        print("doctor: not a git repo; skipping pre-commit install", file=sys.stderr)
        return
    git_dir = (root / proc.stdout.strip()).resolve()
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook = hooks_dir / "pre-commit"
    if not hook.exists():
        hook.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    body = hook.read_text(encoding="utf-8")
    marker = str(shell_path)
    if marker in body:
        return
    with hook.open("a", encoding="utf-8") as fh:
        fh.write(f'"{marker}" "." --warn-only || true\n')
    hook.chmod(0o755)
    print(f"doctor: pre-commit hook installed at {hook}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".", help="프로젝트 루트")
    parser.add_argument("--strict", action="store_true",
                        help="WARN도 실패로 취급 (exit 1)")
    parser.add_argument("--warn-only", action="store_true",
                        help="FAIL이 있어도 exit 0 (pre-commit 용)")
    parser.add_argument("--json", action="store_true",
                        help="machine-readable JSON 출력")
    parser.add_argument("--output-md",
                        help="Markdown 리포트 저장 경로 (예: docs/verify/DOCTOR_REPORT.md)")
    parser.add_argument("--output-json",
                        help="JSON 리포트 저장 경로")
    parser.add_argument("--setup-precommit", action="store_true",
                        help="git pre-commit hook 설치 후 종료")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    if not root.exists():
        print(f"doctor: project root not found: {root}", file=sys.stderr)
        return 1

    if args.setup_precommit:
        install_precommit_hook(root, Path(__file__).resolve())
        return 0

    results = run_layers(root)
    score = compute_score(results)
    status = overall_status(results, strict=args.strict)

    text = format_text(results, score, status)
    payload_json = format_json(results, score, status)

    if args.output_md:
        out_md = root / args.output_md
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(text + "\n", encoding="utf-8")
    if args.output_json:
        out_j = root / args.output_json
        out_j.parent.mkdir(parents=True, exist_ok=True)
        out_j.write_text(payload_json + "\n", encoding="utf-8")

    if args.json:
        print(payload_json)
    else:
        print(text)

    if args.warn_only:
        return 0
    if status == SEV_FAIL:
        return 1
    if status == SEV_WARN:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
