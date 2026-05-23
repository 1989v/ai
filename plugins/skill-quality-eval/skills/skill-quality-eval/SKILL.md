---
name: skill-quality-eval
description: Claude Code 스킬의 품질을 정량 평가하고 가다듬는 closed loop. 정답셋 생성, 회귀 측정 (N회 반복 → accuracy/stability), 의미 매칭 (Haiku judge), 개선 제안 (suggester) 까지 자동. 자연어 트리거 — "스킬 평가", "정답셋 만들어", "스킬 baseline 박아", "회귀 측정", "스킬 가다듬자", "스킬 개선 제안", "이 스킬 품질 어때".
---

# skill-quality-eval — Router

`skill-quality-eval` 플러그인의 4 커맨드 (`baseline` / `run` / `compare` / `promote`) 를 사용자 자연어 의도로 라우팅하는 진입점.

## 트리거 (자연어 → 커맨드 매핑)

| 사용자 의도 | 라우팅 | 예시 발화 |
|---|---|---|
| 정답셋 첫 생성 / baseline 박기 | `/skill-eval:baseline {skill-id}` | "hns:glossary 정답셋 만들어", "baseline 박아줘", "이 스킬 정답 등록" |
| 회귀 측정 / 품질 평가 | `/skill-eval:run {skill-id}` | "스킬 평가 돌려", "회귀 측정", "이 스킬 품질 어때", "현재 스킬이 baseline 대비 잘 동작해?" |
| 두 스냅샷 비교 | `/skill-eval:compare {snap-a} {snap-b}` | "스냅샷 두 개 비교", "어제 결과랑 오늘 결과 차이" |
| baseline 갱신 (current 심볼릭 링크 이동) | `/skill-eval:promote {skill-id} {snap}` | "이 결과를 새 baseline 으로", "현재 baseline 으로 승격" |
| 개선 제안만 (이미 회귀 있는 스냅샷에 대해) | `scripts/suggest-improvements.sh` 직접 호출 | "이 회귀에 대한 SKILL.md 수정 제안", "어디 고쳐야 회귀 풀려" |

## 라우팅 절차

1. **의도 분류** — 사용자 발화에서 위 표의 트리거 중 가장 가까운 것 선택. 모호하면 사용자에게 1회 확인.
2. **스킬 ID 추출** — "hns:glossary", "/ideabank:init" 등 콜론 포함 패턴 또는 마지막 언급된 스킬 이름. 없으면 사용자에게 어떤 스킬인지 질의.
3. **사전 조건 확인** — `goldset/{skill-id}/schema/output.schema.json` 존재 여부. 없으면 `examples/{skill-id}/` 에서 복사 권유 또는 사용자가 직접 정의하도록 안내.
4. **커맨드 호출** — 위 표의 슬래시 커맨드 실행. 인자는 자연어에서 추출 (`--repeat N` 등은 명시 언급된 경우만).
5. **결과 정리** — 커맨드 출력을 사용자에게 보고. 회귀 발견 시 `suggestions.md` 경로 강조.

## 흐름 (closed loop)

```
사용자: "hns:glossary 품질 평가"
  ↓ (router → run)
/skill-eval:run hns:glossary
  ↓ (fork + N회 invoke + match-semantic)
회귀 0건 → ✅ "accuracy {n}/{N}, stability {s}/{N}" 보고 → 끝
회귀 N건 → suggester 자동 호출 → suggestions.md 생성
  ↓
사용자: suggestions.md 참고 → SKILL.md 편집
  ↓
사용자: "다시 평가"
  ↓ (router → run)
회귀 0건 → /skill-eval:promote 안내 → 사용자 확정 시 새 baseline 으로 승격
```

## 비-트리거 (이 스킬이 처리하지 않는 것)

- "스킬을 새로 만들어줘" → `superpowers:writing-skills`
- "스킬을 정적 룰로 검증" → `hns:validate` (static analysis)
- "스킬 호출 결과 디버깅" → `ai-debugger:*`

skill-quality-eval 은 **이미 존재하는 스킬을 실행 결과로 정량 평가** 하는 도구. 스킬 작성·정적 검사·디버깅과는 명확히 역할 분리.

## 사전 준비 (goldset 디렉토리 컨벤션)

```
goldset/{skill-id}/
├── schema/output.schema.json       # 평가용 JSON 계약 (사람이 1회 정의)
├── schema/matching-policy.json     # 필드별 매칭 모드 (strict/structural/semantic + match-by)
├── fixtures/                        # 코드베이스 의존 스킬의 입력 (옵션)
├── cases/case-001/input.yml         # 스킬 호출 인자 — 답을 누설하는 description 등 금지
├── judge-calibration/*.yml          # semantic judge 신뢰도 측정용 정답셋 (옵션)
├── snapshots/{YYYY-MM-DD-tag}/      # 평가 1회 = 디렉토리 1개
└── current → snapshots/{baseline}   # 활성 baseline (심볼릭 링크)
```

자세한 spec → `references/snapshot-layout.md`, `references/matching-policy.md`, `references/overlay-template.md`.

## 비용 가이드

| 작업 | 모델 | 케이스당 비용 (대략) |
|---|---|---|
| baseline 1회 (N=3) | Opus | ~$1.00 |
| run 1회 (N=3) | Haiku | ~$0.40 |
| run 1회 (N=3) | Opus | ~$1.00 |
| semantic judge (Haiku) | Haiku | ~$0.20 per pair (캐시 hit 시 $0) |
| suggester (회귀 시 1회) | Opus | ~$0.30 |
| calibration set 평가 | Haiku | ~$0.05 × N pairs |

대형 스킬 + N=5 + Opus 면 case 당 ~$2-3. 비용 다이얼: `--model haiku`, `--repeat 2`, `--no-suggester`.
