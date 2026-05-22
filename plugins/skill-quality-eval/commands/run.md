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
2. **스냅샷 디렉토리 생성** — `scripts/snapshot.sh create-run {skill-id} {tag}` 로 신규 스냅샷 dir 확보
3. **원본 스킬 탐색** — baseline `/source-skill/` 의 SKILL.md 위치를 참고해 동일 상대경로의 현 시점 원본 스킬 찾기
4. **각 case 마다**:
   a. `scripts/fork-and-invoke.sh --output-kind actual` 로 fork + invoke → `actual.json` 생성
   b. `scripts/match.sh --expected {baseline}/cases/{id}/expected.json --actual {snapshot}/cases/{id}/actual.json --policy goldset/{skill-id}/schema/matching-policy.json` 호출
   c. match 결과 JSON 을 `cases/{id}/match.json` 으로 저장
   d. expected vs actual 의 사람용 diff 를 `cases/{id}/diff.md` 로 생성
5. **종합 리포트** — `report.md` + `report.json` 작성:
   - 케이스별 pass/fail/format-fail
   - 회귀 케이스의 path-level diff 요약
   - `diff-vs-baseline.md` 에 별도 회귀 종합표
6. **결과 보고**:
   - `✅ {N}/M pass, {K} fail` 또는 `❌ {K}/M 회귀 발견`
   - 회귀 시 의도된 변경이면 `/skill-eval:promote {skill-id} {snapshot-id}` 로 새 baseline 으로 승격 안내
   - 의도치 않은 회귀면 diff 보고 스킬 추가 수정 안내

## 출력 예시 (회귀 케이스)

```
❌ 1/1 회귀: goldset/hns-glossary/snapshots/2026-05-22-after-fix
   case-001: FAIL — 2 fields differ
     $.terms[name=Order].type   expected "Aggregate"   actual "Entity"
     $.terms[name=PaymentEvent] orphan-actual

   intended? → /skill-eval:promote hns:glossary 2026-05-22-after-fix
   unintended? → revert/edit skill, then /skill-eval:run hns:glossary
```

## 비용 다이얼 (v0.1)

- 케이스 N × invoke 1회. 반복 평가 (`repeat`) 는 v0.2+.
- `--model haiku` 사용 시 비용 1/10 이하 (baseline 도 haiku 로 박았어야 동일 모델 비교)
