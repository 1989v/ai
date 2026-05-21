---
description: "Move the `current` baseline pointer to a different snapshot — explicit, no auto-promotion"
argument-hint: "<skill-id> <snapshot-id>"
---

# /skill-eval:promote

`goldset/{skill-id}/current` 심볼릭 링크를 다른 스냅샷으로 이동한다. 이게 **유일한** baseline 갱신 경로다 (자동 갱신 없음).

## Usage

```
/skill-eval:promote <skill-id> <snapshot-id>
```

- `snapshot-id` — `goldset/{skill-id}/snapshots/` 아래 디렉토리 이름

## 진행 순서

1. **검증** — 대상 스냅샷 dir 존재 확인. 없으면 가능한 후보 목록 출력 후 중단
2. **expected.json 점검**:
   - **있음** (정상 baseline): 그대로 promote 진행
   - **없고 actual.json 만 있음**: "이 스냅샷은 run 결과라 baseline 으로 박으려면 actual → expected 승격 필요. 진행할까요?" 질의
     - **y**: 모든 case 의 `actual.json` 을 `expected.json` 으로 복사 + 사용자에게 "정답으로 확정한다" 명시 컨펌 1회
     - **n**: 중단
3. **symlink 이동** — `scripts/snapshot.sh promote {skill-id} {snapshot-id}` 호출
4. **결과 보고** — 이전 baseline 어디였는지 + 새 baseline 어디인지

## 출력 예시

```
✅ baseline 이동: hns:glossary
   from: 2026-05-22-baseline
   to:   2026-05-23-after-refactor (12 case 의 actual.json → expected.json 승격)

   이후 /skill-eval:run 의 비교 기준이 새 baseline 으로 바뀝니다.
```

## 안전 가드

- 이전 baseline 디렉토리는 보존됨 (history). 필요 시 다시 promote 로 되돌릴 수 있음
- run 결과 (actual.json) 를 baseline 으로 승격하는 흐름은 명시적 사용자 컨펌 필수 — "스킬 출력 = 정답" 으로 cyclic 박히는 사고 방지
