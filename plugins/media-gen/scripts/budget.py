#!/usr/bin/env python3
"""media-gen 비용 게이트 — 호출 계획을 크레딧·$·₩ 표로 내고, 사용자 승인을 기록한다.

  budget.py estimate --provider higgsfield --plan plan.json --job DIR
            [--retry-factor 1.5] [--usd-per-credit X] [--krw-per-usd 1400] [--max-age-days 60]
  budget.py approve --job DIR --calls N --answer "사용자 답변 원문"

plan.json: [{"stage": "IMAGE 1 앵커", "model": "nano-banana-pro", "count": 2}, ...]

종료 코드 — 3: 단가표 검증일이 오래됐다(재검증 전엔 견적 없음) · 4: 모르는 모델 · 5: 승인 전제 미충족.
단가는 옆의 pricing.json 이 단일 원본이다. 잔액·비용 조회 도구가 있으면 그 값이 이기고, 그때 이 파일을 갱신한다.
"""
import argparse
import json
import math
import sys
from datetime import date, datetime
from pathlib import Path

PRICING = Path(__file__).resolve().parent / "pricing.json"


def load_pricing():
    return json.loads(PRICING.read_text())


def cmd_estimate(args):
    pricing = load_pricing()
    verified = date.fromisoformat(pricing["verified"])
    age = (date.today() - verified).days
    if age > args.max_age_days:
        print(f"단가표 검증일 {verified} — {age}일 지났다. 요금 페이지를 다시 확인해 pricing.json 의 "
              f"verified 와 단가를 갱신한 뒤에만 견적을 낸다 (--max-age-days {args.max_age_days}).", file=sys.stderr)
        sys.exit(3)
    prov = pricing["providers"].get(args.provider)
    if not prov:
        print(f"모르는 프로바이더: {args.provider} — pricing.json 에 있는 것: {sorted(pricing['providers'])}", file=sys.stderr)
        sys.exit(4)
    plan = json.loads(Path(args.plan).read_text())
    unknown = [p["model"] for p in plan if p["model"] not in prov["models"]]
    if unknown:
        print(f"모르는 모델: {unknown} — pricing.json 에 있는 것: {sorted(prov['models'])}. "
              f"실제 도구 스키마·요금표에서 단가를 확인해 추가한 뒤 다시.", file=sys.stderr)
        sys.exit(4)

    usd_per_credit = args.usd_per_credit or prov["usd_per_credit_topup"]
    krw = args.krw_per_usd or pricing.get("krw_per_usd_default", 1400)
    rows, credits, calls = [], 0.0, 0
    for p in plan:
        unit = prov["models"][p["model"]]["credits"]
        sub = unit * p["count"]
        credits += sub
        calls += p["count"]
        rows.append((p["stage"], p["model"], p["count"], unit, sub))
    planned_calls = math.ceil(calls * args.retry_factor)
    planned_credits = credits * args.retry_factor
    usd = planned_credits * usd_per_credit

    lines = [f"## 비용 견적 — {args.provider} (단가 검증 {verified}, {age}일 전)", "",
             "| 단계 | 모델 | 횟수 | 단가(cr) | 소계(cr) |", "|---|---|---:|---:|---:|"]
    lines += [f"| {s} | `{m}` | {c} | {u:g} | {sub:g} |" for s, m, c, u, sub in rows]
    lines += ["", f"- 계획 합계 **{credits:g}cr / {calls}회** → 재시도 여유 ×{args.retry_factor:g} = "
                  f"**{planned_credits:g}cr / {planned_calls}회 승인 요청**",
              f"- 탑업 기준 ${usd_per_credit:g}/cr → **≈ ${usd:,.2f} ≈ ₩{usd * krw:,.0f}** (환율 {krw:,.0f}원/$)"]
    for name, plan_info in prov.get("plans", {}).items():
        per = plan_info["usd_month"] / plan_info["credits"]
        lines.append(f"- 구독 {name}(${plan_info['usd_month']}/월·{plan_info['credits']}cr) 잔량으로 쓰면 "
                     f"추가 지출 ₩0, 환산 ≈ ${planned_credits * per:,.2f}")
    lines += [f"- **₩0 경로**: {prov['free_path']}", "",
              "선택지 — (a) MCP 로 생성(위 금액) · (b) 구독 잔량으로 생성 · (c) ₩0 수동 경로 · (d) 중단"]
    text = "\n".join(lines)
    print(text)

    if args.job:
        job = Path(args.job).expanduser()
        (job / "estimate.md").write_text(text + "\n")
        (job / "estimate.json").write_text(json.dumps({
            "provider": args.provider, "plan": plan, "retry_factor": args.retry_factor,
            "planned_calls": planned_calls, "planned_credits": planned_credits,
            "usd": round(usd, 2), "krw": round(usd * krw), "estimated_at": datetime.now().isoformat(timespec="seconds"),
        }, ensure_ascii=False, indent=2) + "\n")


def cmd_approve(args):
    job = Path(args.job).expanduser()
    est = job / "estimate.json"
    if not est.is_file():
        print(f"승인 전제 미충족: {est} 가 없다 — estimate 를 먼저 돌려 사용자에게 표를 보인다.", file=sys.stderr)
        sys.exit(5)
    if not args.answer.strip():
        print("승인 전제 미충족: --answer 에 사용자의 답변 원문이 있어야 한다.", file=sys.stderr)
        sys.exit(5)
    planned = json.loads(est.read_text())["planned_calls"]
    if args.calls > planned:
        print(f"승인 전제 미충족: 승인 호출 {args.calls} > 견적 {planned}. 더 필요하면 견적을 다시 낸다.", file=sys.stderr)
        sys.exit(5)
    record = {"approved_by_user": True, "remaining_calls": args.calls, "approved_calls": args.calls,
              "approved_at": datetime.now().isoformat(timespec="seconds"), "answer": args.answer.strip(),
              "provider": json.loads(est.read_text())["provider"]}
    (job / "approval.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(f"승인 기록: {job / 'approval.json'} — 유료 호출 {args.calls}회, 24시간 유효")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("estimate")
    e.add_argument("--provider", required=True)
    e.add_argument("--plan", required=True)
    e.add_argument("--job")
    e.add_argument("--retry-factor", type=float, default=1.5)
    e.add_argument("--usd-per-credit", type=float)
    e.add_argument("--krw-per-usd", type=float)
    e.add_argument("--max-age-days", type=int, default=60)
    a = sub.add_parser("approve")
    a.add_argument("--job", required=True)
    a.add_argument("--calls", type=int, required=True)
    a.add_argument("--answer", required=True)
    args = ap.parse_args()
    {"estimate": cmd_estimate, "approve": cmd_approve}[args.cmd](args)


if __name__ == "__main__":
    main()
