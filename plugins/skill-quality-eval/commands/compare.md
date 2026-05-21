---
description: "Diff two snapshots — case-by-case match results + structural delta between any two evaluation runs"
argument-hint: "<skill-id> <snapshot-a> <snapshot-b>"
---

# /skill-eval:compare

임의의 두 스냅샷을 비교한다. baseline ↔ run, run ↔ run 모두 가능.

## Usage

```
/skill-eval:compare <skill-id> <snapshot-a> <snapshot-b>
```

- `snapshot-a`, `snapshot-b` — `goldset/{skill-id}/snapshots/` 아래 디렉토리 이름 (예: `2026-05-22-baseline`)

## 진행 순서

1. **존재 확인** — 두 스냅샷 dir 이 모두 존재하는지 검증
2. **케이스 union** — A 와 B 의 cases/ 디렉토리 키 합집합 산출
3. **각 case 마다**:
   - 양쪽이 `expected.json` 만 가진 경우 (baseline ↔ baseline): expected 끼리 매칭
   - 한쪽이 `expected.json`, 다른 쪽이 `actual.json`: expected 와 actual 매칭
   - 양쪽이 `actual.json` (run ↔ run): actual 끼리 매칭
   - 한쪽에만 case 존재: "case-A-only" / "case-B-only" 로 마킹
   - `scripts/match.sh` 호출 → 결과 수집
4. **delta 표 출력**:
   ```
   case-id              A status     B status     diff summary
   case-001             pass         fail         2 fields differ
   case-002             pass         pass         identical
   case-003             —            pass         (B 에만 존재)
   ```
5. **structural delta** — 두 스냅샷의 SKILL.md 차이도 함께 출력 (`diff -u {A}/source-skill {B}/source-skill`)

## 출력 위치

`compare` 는 신규 스냅샷을 만들지 않는다. 결과는 stdout 으로만 출력 (사람이 직접 보고 판단).

## 사용 시나리오

- **regression 진단**: baseline ↔ 최신 run 비교 (자동으로 매 run 마다 생성되는 `diff-vs-baseline.md` 의 ad-hoc 버전)
- **세 번째 옵션 검토**: 두 개의 후보 변경 (run-A, run-B) 중 어느 게 더 baseline 에 가까운지
- **장기 추세**: 한 달 전 run 과 오늘 run 비교
