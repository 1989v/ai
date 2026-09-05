---
name: setup-hooks
description: Use to install hns lifecycle hooks in a project — SessionStart recovery, PreCompact preservation, pre-commit compile gate, post-edit lint, Stop evidence gate — plus the doctor pre-commit hook and docs-health CI. Verifies each hook with an injected failure before reporting success.
disable-model-invocation: true
argument-hint: "[reminder|feedback|enforce] [--no-ci]"
---

# /hns:setup-hooks

훅 스키마 참조: `references/hooks-reference.md`. 템플릿: `${CLAUDE_PLUGIN_ROOT}/templates/hooks/`.

## 1. 수준 선택
인자가 없으면 묻는다: `reminder` / `feedback` / `enforce` (설명은 `templates/hooks/README.md` 표).

## 2. 스크립트 설치
```bash
mkdir -p .claude/hooks/hns && cp "${CLAUDE_PLUGIN_ROOT}/templates/hooks/scripts/"*.sh .claude/hooks/hns/ && chmod +x .claude/hooks/hns/*.sh
```

## 3. settings 병합
`templates/hooks/settings.hooks.json` 의 `hooks` 를 `.claude/settings.json` 에 병합한다(기존 항목 유지, hns 항목은 command 경로 `.claude/hooks/hns/` 로 식별해 중복 방지). `enforce` 가 아니면 `Stop` 항목은 넣지 않는다.
```bash
python3 - <<'PY'
import json, pathlib
tier = "{tier}"
src = json.load(open("${CLAUDE_PLUGIN_ROOT}/templates/hooks/settings.hooks.json"))["hooks"]
p = pathlib.Path(".claude/settings.json"); dst = json.loads(p.read_text()) if p.exists() else {}
hooks = dst.setdefault("hooks", {})
for ev, groups in src.items():
    if ev == "Stop" and tier != "enforce": continue
    cur = hooks.setdefault(ev, [])
    cur[:] = [g for g in cur if not any("/.claude/hooks/hns/" in h.get("command", "") for h in g.get("hooks", []))]
    cur.extend(groups)
p.parent.mkdir(exist_ok=True); p.write_text(json.dumps(dst, ensure_ascii=False, indent=2) + "\n")
PY
```

## 4. 환경 파일
`templates/hooks/hns-hooks.env.example` → `.claude/hns-hooks.env`. `HNS_HOOK_TIER` 를 선택값으로, `HNS_COMPILE_CMD` 는 빌드 파일에서 추정해 제안(Gradle: `./gradlew compileKotlin compileTestKotlin -q`, npm: `npx tsc -b`, Python: `python -m compileall -q .`), `HNS_LINT_CMD` 는 린터가 있을 때만. 사용자 확인 후 저장.

## 5. 빨간불 확인 (필수)
설치한 스크립트에 실패 입력을 주입해 차단/알림이 나오는지 보고, 정상 입력에 침묵하는지 본다. 출력을 그대로 보여준 뒤에만 "설치됨" 이라고 말한다.
```bash
echo '{"tool_input":{"command":"git commit -m x"}}' | HNS_HOOK_TIER=enforce HNS_COMPILE_CMD=false .claude/hooks/hns/commit-gate.sh   # deny JSON
echo '{"tool_input":{"command":"git commit -m x"}}' | HNS_HOOK_TIER=enforce HNS_COMPILE_CMD=true  .claude/hooks/hns/commit-gate.sh   # 출력 없음
echo '{"source":"compact"}' | .claude/hooks/hns/session-start-recover.sh   # 진행 노트가 있으면 additionalContext, 없으면 침묵
```
세션에 반영되려면 **새 세션**이 필요하다고 안내한다.

## 6. doctor 훅 + CI (`--no-ci` 로 생략)
- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py" . --setup-precommit` — 기존 pre-commit 에 append(marker 로 중복 방지), `--warn-only`.
- `templates/ci/docs-health.yml` → `.github/workflows/docs-health.yml` + 얇은 트리거 래퍼(`workflow_call`, `plugin_repo` 입력). 시크릿 `ANTHROPIC_API_KEY_FOR_WORKFLOWS`(필수) `RUNNER_GH_TOKEN`(선택) 안내. 모드 전환은 `/hns:health-mode`.
- `.gitignore` 에 `docs/verify/`.

## 제거
```bash
rm -rf .claude/hooks/hns .claude/hns-hooks.env      # + settings.json 의 hns 항목 삭제
sed -i '' '/doctor.py.*--warn-only/d' .git/hooks/pre-commit
```

## NEVER
- 사용자 확인 없이 settings.json 덮어쓰기(항상 병합)
- 빨간불을 보지 않고 "훅 켰다" 고 보고
- CI 시크릿 값을 파일에 쓰기
