#!/usr/bin/env python3
"""
doc_scan.py — git diff 기반 문서 영향 스캐너.

ADR-0023 Doc Index Tracking 의 비-LLM fast path. 현재 변경된 소스 파일이
어떤 문서에 영향을 미칠 수 있는지 lock 을 참조해 후보를 뽑는다.

Python 3 stdlib only.

Usage:
  python3 doc_scan.py [--repo ROOT] [--base REF] [--json]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SOURCE_EXTS = {".kt", ".java", ".py", ".ts", ".tsx", ".vue", ".go"}


def changed_files(repo: Path, base: str) -> list[str]:
    def run(args: list[str]) -> str:
        try:
            return subprocess.check_output(args, text=True)
        except subprocess.CalledProcessError:
            return ""

    diff = run(["git", "-C", str(repo), "diff", "--name-only", base])
    staged = run(["git", "-C", str(repo), "diff", "--name-only", "--cached"])
    untracked = run(["git", "-C", str(repo), "ls-files", "--others", "--exclude-standard"])
    files: set[str] = set()
    for block in (diff, staged, untracked):
        for line in block.strip().splitlines():
            line = line.strip()
            if line:
                files.add(line)
    return sorted(files)


def detect_deletions(repo: Path, base: str) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "diff", "--name-only", "--diff-filter=D", base],
            text=True,
        )
    except subprocess.CalledProcessError:
        return []
    return [l.strip() for l in out.strip().splitlines() if l.strip()]


def impacted_docs(changed: list[str], lock: dict) -> tuple[list[dict], list[str]]:
    links = lock.get("links", []) or []
    doc_by_source: dict[str, list[dict]] = {}
    for l in links:
        if not l.get("resolved"):
            continue
        doc_by_source.setdefault(l["source"], []).append(l)

    impacted: list[dict] = []
    new_sources: list[str] = []
    for path in changed:
        if path in doc_by_source:
            for link in doc_by_source[path]:
                impacted.append({
                    "source": path,
                    "doc": link["doc"],
                    "link_type": link["link_type"],
                    "service": link.get("service", "root"),
                })
        elif any(path.endswith(ext) for ext in SOURCE_EXTS):
            new_sources.append(path)
    return impacted, new_sources


def render_markdown(impacted: list[dict], new_sources: list[str], deleted: list[str]) -> str:
    lines = ["# Doc Impact Scan", ""]
    if not impacted and not new_sources and not deleted:
        lines.append("영향받는 문서 없음. clean.")
        return "\n".join(lines)

    if impacted:
        lines.append("## Impacted docs (기존 매핑)")
        lines.append("")
        lines.append("| Service | Doc | Source | Link |")
        lines.append("|---|---|---|---|")
        for item in sorted(impacted, key=lambda x: (x["service"], x["doc"])):
            lines.append(f"| {item['service']} | `{item['doc']}` | `{item['source']}` | {item['link_type']} |")
        lines.append("")

    if new_sources:
        lines.append("## New sources (문서 미연결)")
        lines.append("")
        for s in new_sources:
            lines.append(f"- `{s}`")
        lines.append("")
        lines.append("> 필요 시 `docs/doc-index.json` 의 `manual_links` 또는 `pattern_rules` 에 추가.")
        lines.append("")

    if deleted:
        lines.append("## Deleted sources (고아 문서 가능)")
        lines.append("")
        for s in deleted:
            lines.append(f"- `{s}`")
        lines.append("")
        lines.append("> 연결된 문서가 있으면 아카이브 또는 내용 갱신 검토.")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Doc impact scanner (ADR-0023)")
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--base", default="HEAD", help="git diff base ref")
    parser.add_argument("--json", action="store_true", help="JSON 출력")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    lock_path = repo / "docs" / "doc-index.lock.json"

    if not lock_path.exists():
        sys.stderr.write("lock 없음. doc_map.py --init 먼저 실행.\n")
        return 2

    lock = json.loads(lock_path.read_text())
    changed = changed_files(repo, args.base)
    deleted = detect_deletions(repo, args.base)
    impacted, new_sources = impacted_docs(changed, lock)

    if args.json:
        print(json.dumps({
            "changed": changed,
            "impacted": impacted,
            "new_sources": new_sources,
            "deleted": deleted,
        }, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(impacted, new_sources, deleted))

    return 0


if __name__ == "__main__":
    sys.exit(main())
