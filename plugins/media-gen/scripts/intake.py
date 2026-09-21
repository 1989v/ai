#!/usr/bin/env python3
"""media-gen 인테이크 — 장르별 필수 리소스를 검사하고 작업 폴더를 만든다.

장르별 필수/선택 입력의 단일 원본은 이 파일의 GENRES 다. 필수 입력이 하나라도 없으면
작업 폴더를 만들지 않고 종료 코드 2 로 끝난다 — 자리 표시자로 다음 단계에 갈 수 없다.

  intake.py requirements --genre G                  # 사용자에게 보여 줄 필수/선택 입력 표
  intake.py new --genre G --slug S [--home DIR]     # 검사 → 복사 → job.json → .current-job
            [--source P ...] [--ref-video P] [--style-ref P ...]
            [--concept TEXT] [--aspect 9:16] [--note TEXT]

검사는 macOS 내장 도구로 한다 — 이미지는 sips, 영상 길이는 mdls(있으면 ffprobe).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm"}
MIN_IMAGE_SHORT_SIDE = 512
PLACEHOLDER_BYTES = 20_000          # 이보다 작은 "사진" 은 단색·아이콘일 가능성이 높다
REF_VIDEO_SECONDS = (3, 30)         # Genjutsu 모션 트랜스퍼가 받는 레퍼런스 길이

GENRES = {
    "shortform-transform": {
        "label": "인물 사진 → 변신 숏폼",
        "required": {
            "source": "얼굴이 선명한 인물 사진 1장 이상 (2~3장이면 얼굴 재현이 낫다). 외모 담당",
            "ref_video": "레퍼런스 영상 1개 (3~30초). 움직임·변신 타이밍·카메라 담당",
        },
        "optional": {"concept": "변신 후 모습 한 줄 (예: 마법소녀 히어로 의상)", "aspect": "기본 9:16"},
    },
    "game-character": {
        "label": "게임 캐릭터 디자인 시트",
        "required": {"concept": "캐릭터 콘셉트 문장 (종족·직업·실루엣·색·분위기)"},
        "optional": {"style_ref": "스타일 참조 이미지", "source": "기존 캐릭터 이미지(재사용 시)"},
    },
    "game-background": {
        "label": "게임 배경 · 환경",
        "required": {"concept": "장면 설명 (장소·시간대·날씨·카메라 높이)", "aspect": "뷰포트 비율 (16:9 · 9:16 · 3:2 …)"},
        "optional": {"style_ref": "스타일 참조 이미지"},
    },
    "image": {
        "label": "일반 이미지",
        "required": {"concept": "무엇을 · 어떤 용도로 (썸네일 · 제품 컷 · 스타일 변환 …)"},
        "optional": {"source": "인물이 들어가면 그 사진", "style_ref": "스타일 참조", "aspect": "비율"},
    },
    "background-photo": {
        "label": "배경 사진 · 월페이퍼",
        "required": {"concept": "분위기·소재 (예: 새벽 안개 낀 침엽수림, 인물 없음)", "aspect": "16:9 · 9:16 · 21:9"},
        "optional": {"style_ref": "스타일 참조"},
    },
}

CANONICAL = {"source": "source", "ref_video": "ref-video", "style_ref": "style"}


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def image_dims(path):
    out = sh(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)])
    w = re.search(r"pixelWidth:\s*(\d+)", out)
    h = re.search(r"pixelHeight:\s*(\d+)", out)
    return (int(w.group(1)), int(h.group(1))) if w and h else None


def video_seconds(path):
    if shutil.which("ffprobe"):
        out = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
        try:
            return float(out.strip())
        except ValueError:
            pass
    out = sh(["mdls", "-name", "kMDItemDurationSeconds", "-raw", str(path)]).strip()
    try:
        return float(out)
    except ValueError:
        return None


def check_image(path, warnings):
    info = {"path": str(path), "bytes": path.stat().st_size}
    dims = image_dims(path)
    if dims:
        info["width"], info["height"] = dims
        if min(dims) < MIN_IMAGE_SHORT_SIDE:
            warnings.append(f"{path.name}: 짧은 변 {min(dims)}px < {MIN_IMAGE_SHORT_SIDE}px — 얼굴 재현이 흐려질 수 있다")
    else:
        warnings.append(f"{path.name}: 해상도를 읽지 못했다 (sips)")
    if info["bytes"] < PLACEHOLDER_BYTES:
        warnings.append(f"{path.name}: {info['bytes']}B — 사진이 아니라 단색·자리 표시자일 수 있다. 열어서 확인")
    return info


def check_video(path, warnings):
    info = {"path": str(path), "bytes": path.stat().st_size}
    secs = video_seconds(path)
    if secs is None:
        warnings.append(f"{path.name}: 길이를 읽지 못했다 (mdls/ffprobe) — 3~30초인지 직접 확인")
    else:
        info["seconds"] = round(secs, 1)
        lo, hi = REF_VIDEO_SECONDS
        if not lo <= secs <= hi:
            warnings.append(f"{path.name}: {secs:.1f}초 — 레퍼런스 영상은 {lo}~{hi}초여야 한다 (잘라서 다시)")
    return info


def resolve(paths, kind, errors):
    out = []
    for p in paths or []:
        path = Path(p).expanduser()
        if not path.is_file():
            errors.append(f"{kind}: 파일이 없다 — {p}")
            continue
        ext = path.suffix.lower()
        allowed = VIDEO_EXT if kind == "ref_video" else IMAGE_EXT
        if ext not in allowed:
            errors.append(f"{kind}: 형식 {ext} 은 받지 않는다 — {sorted(allowed)}")
            continue
        out.append(path)
    return out


def cmd_requirements(args):
    g = GENRES[args.genre]
    print(f"## {args.genre} — {g['label']}\n")
    print("| 구분 | 입력 | 설명 |\n|---|---|---|")
    for k, v in g["required"].items():
        print(f"| **필수** | `{k}` | {v} |")
    for k, v in g["optional"].items():
        print(f"| 선택 | `{k}` | {v} |")
    print("\n사진·영상은 첨부 대신 **로컬 경로**로 받는다 — 생성 도구는 파일 경로(또는 URL)를 요구한다.")
    if "source" in g["required"]:
        print("인물 사진은 생성 서비스(외부 서버)로 올라간다 — 본인·가족 사진만, 그리고 그 사실을 알린다.")


def cmd_new(args):
    g = GENRES[args.genre]
    errors, warnings = [], []
    sources = resolve(args.source, "source", errors)
    ref = resolve([args.ref_video] if args.ref_video else [], "ref_video", errors)
    styles = resolve(args.style_ref, "style_ref", errors)
    given = {
        "source": bool(sources), "ref_video": bool(ref), "style_ref": bool(styles),
        "concept": bool(args.concept and args.concept.strip()), "aspect": bool(args.aspect),
    }
    missing = [k for k in g["required"] if not given.get(k)]
    if missing or errors:
        print("인테이크 실패 — 작업 폴더를 만들지 않았다.", file=sys.stderr)
        for m in missing:
            print(f"  필수 누락: {m} — {g['required'][m]}", file=sys.stderr)
        for e in errors:
            print(f"  오류: {e}", file=sys.stderr)
        sys.exit(2)

    inputs = {}
    for path in sources:
        inputs.setdefault("source", []).append(check_image(path, warnings))
    for path in ref:
        inputs["ref_video"] = check_video(path, warnings)
    for path in styles:
        inputs.setdefault("style_ref", []).append(check_image(path, warnings))

    home = Path(args.home).expanduser()
    slug = re.sub(r"[^a-z0-9가-힣-]+", "-", args.slug.lower()).strip("-") or "job"
    job = home / f"{date.today().isoformat()}-{slug}"
    if job.exists():
        print(f"이미 있다: {job} — 다른 --slug 를 쓰거나 폴더를 치운다", file=sys.stderr)
        sys.exit(2)
    (job / "inputs").mkdir(parents=True)
    (job / "outputs").mkdir()

    def copy_in(items, key):
        for i, item in enumerate(items, 1):
            src = Path(item["path"])
            name = f"{CANONICAL[key]}-{i:02d}{src.suffix.lower()}" if key != "ref_video" else f"{CANONICAL[key]}{src.suffix.lower()}"
            shutil.copy2(src, job / "inputs" / name)
            item["copied_as"] = f"inputs/{name}"

    for key in ("source", "style_ref"):
        if key in inputs:
            copy_in(inputs[key], key)
    if "ref_video" in inputs:
        copy_in([inputs["ref_video"]], "ref_video")

    manifest = {
        "genre": args.genre, "slug": slug, "created": datetime.now().isoformat(timespec="seconds"),
        "status": "intake", "concept": args.concept or "", "aspect": args.aspect or "",
        "note": args.note or "", "inputs": inputs, "warnings": warnings,
    }
    (job / "job.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    home.mkdir(parents=True, exist_ok=True)
    (home / ".current-job").write_text(str(job) + "\n")

    print(f"작업 폴더: {job}")
    for key, val in inputs.items():
        for item in (val if isinstance(val, list) else [val]):
            dims = f"{item.get('width')}×{item.get('height')}" if "width" in item else f"{item.get('seconds', '?')}s"
            print(f"  {item['copied_as']}  ← {item['path']}  ({dims}, {item['bytes']:,}B)")
    for w in warnings:
        print(f"  경고: {w}")
    if "source" in inputs:
        print("  고지: 인물 사진이 생성 서비스(외부 서버)로 올라간다.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("requirements")
    r.add_argument("--genre", choices=sorted(GENRES), required=True)
    n = sub.add_parser("new")
    n.add_argument("--genre", choices=sorted(GENRES), required=True)
    n.add_argument("--slug", required=True)
    n.add_argument("--home", default=os.environ.get("MEDIA_GEN_HOME", "~/media-gen"))
    n.add_argument("--source", action="append")
    n.add_argument("--ref-video")
    n.add_argument("--style-ref", action="append")
    n.add_argument("--concept")
    n.add_argument("--aspect")
    n.add_argument("--note")
    args = ap.parse_args()
    {"requirements": cmd_requirements, "new": cmd_new}[args.cmd](args)


if __name__ == "__main__":
    main()
