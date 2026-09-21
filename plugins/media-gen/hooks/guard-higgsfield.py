#!/usr/bin/env python3
"""PreToolUse(mcp__*higgsfield*) — 유료 호출은 승인 기록이 있을 때만 통과시킨다.

기본은 deny 다. 통과 조건은 셋 다:
  1. $MEDIA_GEN_HOME/.current-job (기본 ~/media-gen) 이 가리키는 작업 폴더에 approval.json 이 있다
  2. approved_by_user == true 이고 approved_at 이 24시간 안이다
  3. remaining_calls > 0 — 통과할 때마다 1 줄인다. 0 이면 다시 deny → 새 견적·새 승인

조회성 도구(이름이 get · list · search · wait · download 같은 조회 동사로 시작)는 말없이 통과한다.
이름이 애매하면 유료로 본다 — 잘못 막히면 승인 한 번이면 되지만, 잘못 통과하면 돈이 나간다.
bypass 권한 모드에서도 훅의 deny 는 듣는다. MEDIA_GEN_HOOK_LOG=<파일> 이 있으면 호출마다 한 줄 남긴다.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 서버 접두어를 뗀 도구 이름이 조회 동사로 시작하면 조회다 (get_generation_status 처럼 뒤에 generat 이 있어도).
# 그 밖의 이름은 전부 유료로 본다.
READ_ONLY_VERB = re.compile(r"^(get|list|search|check|wait|download|fetch|poll|describe|validate|debug|cancel|"
                            r"whoami|balance|history|usage|status|credit|quota)(_|$)", re.I)
APPROVAL_TTL = timedelta(hours=24)


def trace(line):
    log = os.environ.get("MEDIA_GEN_HOOK_LOG")
    if log:
        with open(log, "a") as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')} {line}\n")


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": "[media-gen] " + reason}}, ensure_ascii=False))
    sys.exit(0)


def allow(context):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "allow",
        "additionalContext": "[media-gen] " + context}}, ensure_ascii=False))
    sys.exit(0)


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        sys.exit(0)
    tool = payload.get("tool_name", "")
    if "higgsfield" not in tool.lower():
        sys.exit(0)
    if READ_ONLY_VERB.match(tool.split("__")[-1]):
        trace(f"{tool} read-only allow")
        sys.exit(0)

    home = Path(os.environ.get("MEDIA_GEN_HOME", "~/media-gen")).expanduser()
    pointer = home / ".current-job"
    how = ("허락 절차: /media-gen:create 의 ② 비용 단계 — budget.py estimate 로 표를 내고 사용자가 고른 뒤 "
           "budget.py approve --job <작업 폴더> --calls N --answer '<답변 원문>' 으로 기록한다. 그 전엔 이 도구를 부를 수 없다.")
    if not pointer.is_file():
        trace(f"{tool} deny no-job")
        deny(f"유료 힉스필드 호출 `{tool}` — 현재 작업 폴더가 없다({pointer}). " + how)
    job = Path(pointer.read_text().strip())
    approval = job / "approval.json"
    if not approval.is_file():
        trace(f"{tool} deny no-approval")
        deny(f"유료 힉스필드 호출 `{tool}` — 승인 기록이 없다({approval}). " + how)
    try:
        rec = json.loads(approval.read_text())
        approved_at = datetime.fromisoformat(rec["approved_at"])
    except (json.JSONDecodeError, KeyError, ValueError):
        trace(f"{tool} deny bad-approval")
        deny(f"유료 힉스필드 호출 `{tool}` — 승인 기록이 깨졌다({approval}). 다시 승인받는다.")
    if not rec.get("approved_by_user"):
        trace(f"{tool} deny not-approved")
        deny(f"유료 힉스필드 호출 `{tool}` — approved_by_user 가 참이 아니다. " + how)
    if datetime.now() - approved_at > APPROVAL_TTL:
        trace(f"{tool} deny expired")
        deny(f"유료 힉스필드 호출 `{tool}` — 승인이 24시간을 넘겼다({approved_at.isoformat(timespec='minutes')}). 견적부터 다시.")
    remaining = int(rec.get("remaining_calls", 0))
    if remaining <= 0:
        trace(f"{tool} deny exhausted")
        deny(f"유료 힉스필드 호출 `{tool}` — 승인된 호출 횟수를 다 썼다(승인 {rec.get('approved_calls')}회). "
             "비용표를 다시 내고 새로 승인받는다.")
    rec["remaining_calls"] = remaining - 1
    rec.setdefault("calls", []).append({"tool": tool, "at": datetime.now().isoformat(timespec="seconds")})
    approval.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n")
    trace(f"{tool} allow remaining={remaining - 1}")
    allow(f"유료 호출 통과 `{tool}` — 남은 승인 {remaining - 1}회 (작업 {job.name}). 결과는 outputs/ 에 받고 체크포인트 리뷰를 한다.")


if __name__ == "__main__":
    main()
