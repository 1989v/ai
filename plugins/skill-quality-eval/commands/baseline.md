---
description: "Create a baseline snapshot for a target skill — fork + invoke + human confirms expected.json once"
argument-hint: "<skill-id> [--model haiku|opus] [--tag baseline]"
---

# /skill-eval:baseline

평가 대상 스킬의 **baseline 스냅샷**을 생성한다. fork 본을 1회 실행 → JSON 출력 → 사용자가 "이게 정답인가?" 컨펌 → `expected.json` 으로 박힘 → `current` 심볼릭 링크가 새 baseline 으로 이동.

## Usage

```
/skill-eval:baseline <skill-id> [--model haiku|opus] [--tag baseline]
```

- `skill-id` — 평가 대상 스킬 (예: `hns:glossary`, `ideabank:init`)
- `--model` — invoke 시 사용 모델 (기본 opus)
- `--tag` — 스냅샷 디렉토리 suffix (기본 `baseline`)

## 사전 준비 (사람 1회 작업)

평가 대상 프로젝트 루트에서:

```
goldset/{skill-id}/
├── schema/
│   ├── output.schema.json     # 평가용 JSON 계약 (필수)
│   └── matching-policy.json   # 매칭 정책 (옵션 — 없으면 strict 디폴트)
├── fixtures/                  # 코드베이스 의존 스킬의 입력 픽스처 (옵션)
└── cases/
    └── case-001/input.yml     # 스킬 호출 인자 (최소 1개)
```

자세한 spec → `references/snapshot-layout.md`, `references/matching-policy.md`.

## 진행 순서 (Claude 가 수행할 단계)

1. **검증** — `goldset/{skill-id}/schema/output.schema.json` 과 `cases/case-001/input.yml` 존재 확인. 없으면 사용자에게 안내 후 중단
2. **스냅샷 디렉토리 생성** — `scripts/snapshot.sh create-baseline {skill-id} {tag}` 호출, 반환된 경로를 사용
3. **원본 스킬 위치 탐색**
   - `~/.claude/plugins/cache/*/`{plugin}`/*/skills/`{skill-name}`/SKILL.md` 우선
   - 없으면 사용자에게 경로 입력 요청
4. **fork + invoke** — 각 case 마다 `scripts/fork-and-invoke.sh` 호출 (`--output-kind expected`)
5. **사용자 컨펌** — 생성된 `expected.json` 을 화면에 출력, "이게 정답인가요? (y/n)" 질의
   - **y**: 그대로 박음 + `report.md` 생성 + step 6 진행
   - **n**: 스냅샷 디렉토리 폐기 (rm -rf) + 사용자에게 사유 질의 → 스킬 또는 input 수정 후 재시도 안내
6. **promote** — `scripts/snapshot.sh promote {skill-id} {snapshot-id}` 호출하여 `current` 심볼릭 링크 이동
7. **결과 보고** — baseline 디렉토리 경로 + 케이스별 expected 요약 + 다음 단계 (`/skill-eval:run`) 안내

## 출력 예시

```
✅ baseline 생성 완료: goldset/hns-glossary/snapshots/2026-05-22-baseline
   case-001: terms 24개 (Aggregate 5, Entity 8, VO 6, Service 5)
   다음: 스킬 수정 후 /skill-eval:run hns:glossary
```

## 주의

- **baseline 갱신은 명시적 `/skill-eval:promote` 만 가능**. 두 번째 호출은 별도 스냅샷을 만들지만 `current` 는 자동 이동하지 않는다 (cyclic 차단)
- 사용자 컨펌 단계에서 expected 가 의도와 다르면, 스킬 자체를 먼저 손보고 다시 `/skill-eval:baseline` 실행
