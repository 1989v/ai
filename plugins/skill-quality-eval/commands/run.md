---
description: "Run regression eval — fork current skill, N-repeat invoke, match-semantic vs baseline, auto-invoke suggester on regression"
argument-hint: "<skill-id> [--model haiku|opus] [--tag <name>] [--repeat N] [--no-suggester]"
---

# /skill-eval:run

스킬 수정 후 회귀 측정. 현재 스킬 상태를 fork → N회 실행 → 직전 baseline 의 `expected.json` 과 자동 매칭 (strict/structural + semantic judge) → 회귀 발견 시 자동으로 suggester 호출하여 SKILL.md 수정 제안 → 신규 스냅샷 디렉토리에 결과 적재.

## Usage

```
/skill-eval:run <skill-id> [--model haiku|opus] [--tag <name>] [--repeat N] [--no-suggester]
```

- `--tag` — 신규 스냅샷 디렉토리 suffix (기본 `after-fix-{HHMMSS}`)
- `--repeat` — N회 반복 (기본 3) → accuracy + stability 두 지표 동시 산출
- `--no-suggester` — 회귀 발견 시 suggester 자동 호출 끔 (비용 절감용)

## 사전 조건

- `goldset/{skill-id}/current` 심볼릭 링크가 baseline 을 가리키고 있어야 함 (없으면 `/skill-eval:baseline` 먼저 실행 안내)

## 진행 순서

1. **baseline 확인** — `scripts/snapshot.sh current {skill-id}` 로 현재 baseline 경로 확인. 없으면 `/skill-eval:baseline` 안내 후 중단
2. **calibration 점검** (선택) — `goldset/{skill-id}/judge-calibration/` 존재 시 `scripts/calibrate-judge.sh` 1회 실행. accuracy 임계 미달이면 경고만 출력 (semantic judge 가 못 미더우니 결과 해석 시 참고)
3. **스냅샷 디렉토리 생성** — `scripts/snapshot.sh create-run {skill-id} {tag}` 로 신규 스냅샷 dir 확보
4. **원본 스킬 탐색** — baseline `/source-skill/` 의 SKILL.md 위치를 참고해 동일 상대경로의 현 시점 원본 스킬 찾기
5. **각 case 마다**:
   a. `scripts/eval-case.sh --baseline-dir {baseline} --repeat N` → N회 fork+invoke + baseline 매칭 + canonical 그룹핑
   b. `eval-case.sh` 내부에서 `scripts/match-semantic.sh` 호출 (strict/structural 기본 + semantic 필드는 Haiku judge)
   c. 결과: `cases/{id}/actual-NNN.json`, `match-NNN.json`, `case-summary.json` (accuracy + stability)
6. **종합 리포트** — `report.md` + `report.json` 작성:
   - 케이스별 accuracy + stability + pass/fail/format-fail 분포
   - 회귀 케이스의 path-level diff (semantic 위반 포함)
   - `diff-vs-baseline.md` 에 별도 회귀 종합표
7. **Suggester 자동 호출** — 회귀 케이스가 1개 이상이고 `--no-suggester` 아니면 `scripts/suggest-improvements.sh` 자동 실행 → `suggestions.md` 생성. SKILL.md 의 어디를 어떻게 고치면 회귀가 풀릴지 구체 edit 제안
8. **결과 보고**:
   - `✅ {N}/M pass, stability {S}/N` 또는 `❌ {K}/M 회귀 발견`
   - 회귀 시 → suggester 가 만든 `suggestions.md` 경로 안내 → 사용자가 해당 SKILL.md edit 적용 후 `/skill-eval:run` 재실행 권장
   - 의도된 변경이면 `/skill-eval:promote {skill-id} {snapshot-id}` 로 새 baseline 으로 승격

## 출력 예시 (회귀 케이스)

```
❌ 1/1 회귀: goldset/hns-glossary/snapshots/2026-05-22-after-fix
   case-001: 0/3 accuracy, 2/3 stability — 3 fields differ across runs
     $.terms[name=Order].type        expected "Aggregate"   actual "Entity"
     $.terms[name=Order].description semantic-mismatch (judge confidence 0.92)
     $.terms[name=PaymentEvent]       orphan-actual

   📝 suggestions: goldset/hns-glossary/snapshots/2026-05-22-after-fix/suggestions.md
      → Theme 1: "Aggregate vs Entity 분류 룰 누락" (medium confidence)
        target_section: "## Iron Laws → 2. Type-first classification"
        change_type: add
      → Theme 2: "DLT 토픽 처리 명세 누락" (low confidence — N-repeat 권장)

   intended? → /skill-eval:promote hns:glossary 2026-05-22-after-fix
   unintended? → suggestions.md 검토 후 스킬 편집 → /skill-eval:run hns:glossary
```

## 비용 다이얼 (v0.2)

- case 당 N × invoke (기본 N=3 → 비용 3배)
- semantic judge 는 Haiku + 값 hash 캐시 → 동일 값 재호출 시 무료
- suggester 는 회귀가 1개 이상일 때만 호출 (정상 case 는 비용 0)
- `--model haiku` 사용 시 invoke 비용 1/10 이하 (baseline 도 haiku 로 박았어야 동일 모델 비교)
- `--no-suggester` 로 suggester 호출 끔 (회귀만 진단하고 개선 제안은 나중에)
