#!/usr/bin/env python3
"""
doc_map.py — 소스↔문서 커버리지 추적기.

ADR-0023 Doc Index Tracking 구현체. 정책(docs/doc-index.json)을 읽고
현재 리포지토리 상태를 스캔하여 lock(docs/doc-index.lock.json)을 생성한다.

Python 3 stdlib only.

Usage:
  python3 doc_map.py [--repo ROOT] [--init] [--check]

- --init:  최초 실행. lock 생성 + init report 첨부.
- --check: lock 재생성 후 기존 lock 과 diff. drift 있으면 exit 1.
- (기본): lock 갱신.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


CITATION_RE = re.compile(r"<!--\s*source:\s*(?P<path>[^\s>]+)\s*-->")
SERVICE_TIERS = {
    "product", "order", "search", "gateway", "common", "charting",
    "analytics", "experiment", "member", "wishlist", "admin", "auth",
    "chatbot", "gifticon", "inventory", "fulfillment", "warehouse",
}


@dataclass
class Policy:
    version: int
    source_roots: list[str]
    doc_roots: list[str]
    ignore_patterns: list[str]
    source_extensions: list[str]
    manual_links: list[dict]
    pattern_rules: list[dict]
    protected_docs: list[str]


@dataclass
class ScanResult:
    sources: dict[str, dict] = field(default_factory=dict)
    docs: dict[str, dict] = field(default_factory=dict)
    links: list[dict] = field(default_factory=list)
    missing_docs: list[dict] = field(default_factory=list)
    dangling_docs: list[dict] = field(default_factory=list)


def load_policy(path: Path) -> Policy:
    data = json.loads(path.read_text())
    return Policy(
        version=data.get("version", 1),
        source_roots=data.get("source_roots", []),
        doc_roots=data.get("doc_roots", []),
        ignore_patterns=data.get("ignore_patterns", []),
        source_extensions=data.get("source_extensions", []),
        manual_links=data.get("manual_links", []) or [],
        pattern_rules=data.get("pattern_rules", []) or [],
        protected_docs=data.get("protected_docs", []) or [],
    )


def resolve_service_tier(rel_path: str) -> str:
    first = rel_path.split("/", 1)[0]
    return first if first in SERVICE_TIERS else "root"


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def walk_sources(repo: Path, policy: Policy) -> dict[str, dict]:
    result: dict[str, dict] = {}
    exts = set(policy.source_extensions)
    for root in policy.source_roots:
        root_dir = repo / root
        if not root_dir.exists():
            continue
        for path in root_dir.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(repo).as_posix()
            if matches_any(rel, policy.ignore_patterns):
                continue
            if path.suffix not in exts:
                continue
            result[rel] = {
                "service": resolve_service_tier(rel),
                "size": path.stat().st_size,
            }
    return result


def walk_docs(repo: Path, policy: Policy) -> dict[str, dict]:
    result: dict[str, dict] = {}
    candidates: list[Path] = []
    for root in policy.doc_roots:
        root_dir = repo / root
        if root_dir.exists():
            candidates.extend(root_dir.rglob("*.md"))
    for svc in SERVICE_TIERS:
        svc_docs = repo / svc / "docs"
        if svc_docs.exists():
            candidates.extend(svc_docs.rglob("*.md"))
        svc_claude = repo / svc / "CLAUDE.md"
        if svc_claude.exists():
            candidates.append(svc_claude)

    for path in candidates:
        rel = path.relative_to(repo).as_posix()
        if matches_any(rel, policy.ignore_patterns):
            continue
        text = _safe_read(path)
        citations = CITATION_RE.findall(text)
        result[rel] = {
            "service": resolve_service_tier(rel),
            "citations": citations,
            "sha": hashlib.sha1(text.encode("utf-8")).hexdigest()[:10],
        }
    return result


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def build_links(policy: Policy, sources: dict, docs: dict) -> list[dict]:
    links: list[dict] = []

    for doc_path, doc_info in docs.items():
        for cite in doc_info["citations"]:
            links.append({
                "doc": doc_path,
                "source": cite,
                "link_type": "explicit",
                "service": doc_info["service"],
                "resolved": cite in sources,
            })

    for entry in policy.manual_links:
        doc = entry["doc"]
        for src_pattern in entry.get("sources", []):
            matched = [s for s in sources if fnmatch.fnmatch(s, src_pattern)]
            if matched:
                for s in matched:
                    links.append({
                        "doc": doc,
                        "source": s,
                        "link_type": "manual",
                        "service": sources[s]["service"],
                        "resolved": True,
                    })
            else:
                links.append({
                    "doc": doc,
                    "source": src_pattern,
                    "link_type": "manual",
                    "service": "root",
                    "resolved": False,
                })

    for rule in policy.pattern_rules:
        src_pattern = rule["source"]
        doc_pattern = rule["doc"]
        for s in sources:
            if fnmatch.fnmatch(s, src_pattern):
                resolved_doc = doc_pattern.replace("{service}", sources[s]["service"])
                links.append({
                    "doc": resolved_doc,
                    "source": s,
                    "link_type": "pattern",
                    "rule": rule.get("name", ""),
                    "service": sources[s]["service"],
                    "resolved": resolved_doc in docs,
                })

    return links


def diagnose(sources: dict, docs: dict, links: list[dict]) -> tuple[list, list]:
    linked_sources = {l["source"] for l in links if l["resolved"]}
    linked_docs = {l["doc"] for l in links if l["resolved"]}

    missing = [
        {"source": s, "service": info["service"]}
        for s, info in sources.items()
        if s not in linked_sources
    ]
    dangling = [
        {"doc": d, "service": info["service"]}
        for d, info in docs.items()
        if d not in linked_docs
    ]
    return missing, dangling


def coverage(sources: dict, missing: list) -> dict:
    by_service: dict[str, dict] = {}
    for s, info in sources.items():
        svc = info["service"]
        by_service.setdefault(svc, {"total": 0, "linked": 0})
        by_service[svc]["total"] += 1
    missing_by_svc: dict[str, int] = {}
    for m in missing:
        missing_by_svc[m["service"]] = missing_by_svc.get(m["service"], 0) + 1
    for svc, stats in by_service.items():
        stats["linked"] = stats["total"] - missing_by_svc.get(svc, 0)
        stats["coverage_pct"] = round(stats["linked"] / stats["total"] * 100, 1) if stats["total"] else 0.0
    return by_service


def build_lock(result: ScanResult, coverage_map: dict) -> dict:
    return {
        "_note": "AUTO-GENERATED by ai/plugins/hns/scripts/doc_map.py (ADR-0023). 직접 편집 금지. 정책은 docs/doc-index.json.",
        "version": 1,
        "summary": {
            "source_count": len(result.sources),
            "doc_count": len(result.docs),
            "link_count": len(result.links),
            "missing_count": len(result.missing_docs),
            "dangling_count": len(result.dangling_docs),
            "coverage_by_service": coverage_map,
        },
        "links": sorted(result.links, key=lambda x: (x["doc"], x["source"])),
        "missing_docs": sorted(result.missing_docs, key=lambda x: x["source"]),
        "dangling_docs": sorted(result.dangling_docs, key=lambda x: x["doc"]),
    }


def write_lock(path: Path, lock: dict) -> None:
    path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n")


def write_init_report(path: Path, lock: dict) -> None:
    summary = lock["summary"]
    cov = summary["coverage_by_service"]
    lines = [
        "# Doc Index — Initial Scan Report",
        "",
        f"- sources: {summary['source_count']}",
        f"- docs: {summary['doc_count']}",
        f"- resolved links: {summary['link_count']}",
        f"- missing (source without doc): {summary['missing_count']}",
        f"- dangling (doc without source): {summary['dangling_count']}",
        "",
        "## Coverage by service",
        "",
        "| Service | Total | Linked | Coverage |",
        "|---|---:|---:|---:|",
    ]
    for svc in sorted(cov):
        stats = cov[svc]
        lines.append(f"| {svc} | {stats['total']} | {stats['linked']} | {stats['coverage_pct']}% |")
    lines.extend([
        "",
        "## Next steps",
        "",
        "1. `docs/doc-index.json` 의 `manual_links` / `pattern_rules` 를 채워 coverage 향상",
        "2. 문서 상단에 `<!-- source: path/to/file.kt -->` 주석으로 explicit citation 추가",
        "3. 재실행: `python3 ai/plugins/hns/scripts/doc_map.py`",
        "",
    ])
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description="Doc-source coverage tracker (ADR-0023)")
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--init", action="store_true", help="초기 스캔 + 리포트 생성")
    parser.add_argument("--check", action="store_true", help="lock drift 검사, drift 시 exit 1")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    policy_path = repo / "docs" / "doc-index.json"
    lock_path = repo / "docs" / "doc-index.lock.json"
    report_path = repo / "docs" / "doc-index-init-report.md"

    if not policy_path.exists():
        sys.stderr.write(f"policy 없음: {policy_path}\n")
        return 2

    policy = load_policy(policy_path)
    sources = walk_sources(repo, policy)
    docs = walk_docs(repo, policy)
    links = build_links(policy, sources, docs)
    missing, dangling = diagnose(sources, docs, links)

    result = ScanResult(
        sources=sources, docs=docs, links=links,
        missing_docs=missing, dangling_docs=dangling,
    )
    cov = coverage(sources, missing)
    lock = build_lock(result, cov)

    if args.check:
        if not lock_path.exists():
            sys.stderr.write("lock 없음. --init 먼저 실행.\n")
            return 1
        previous = json.loads(lock_path.read_text())
        if previous != lock:
            sys.stderr.write("doc-index drift 감지. `python3 ai/plugins/hns/scripts/doc_map.py` 로 lock 갱신 후 커밋.\n")
            return 1
        print("doc-index clean.")
        return 0

    write_lock(lock_path, lock)
    if args.init:
        write_init_report(report_path, lock)
        print(f"wrote {lock_path} + {report_path}")
    else:
        print(f"wrote {lock_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
