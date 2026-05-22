# skill-quality-eval

Claude Code 스킬의 품질을 객관 수치로 평가하는 메타 플러그인. fork + JSON-schema + 스냅샷 디렉토리 3축 모델.

## 무엇을 하는가

- **fork** — 평가 대상 스킬을 임시 디렉토리에 복사 + JSON 출력 강제 overlay 주입. **원본 스킬에는 절대 손대지 않는다.**
- **invoke** — `claude --plugin-dir <fork-dir> --json-schema <schema>` 로 fork 본을 실행, 응답의 `structured_output` 필드를 검증된 JSON 으로 수집.
- **match** — baseline 의 `expected.json` 과 deep-equal 비교 (v0.1 = strict only). 회귀 발견 즉시 diff 표시.
- **snapshot** — 평가 1회 = 디렉토리 1개. 그 시점 스킬 사본 / schema / 정답 / 결과 / diff 가 한 곳에. 회귀 추적이 디렉토리 구조로 표현됨.

## v0.2 범위 (현재)

- 4 커맨드: `baseline` / `run` / `compare` / `promote`
- **N-repeat** (`eval-case.sh`) — case 마다 N회 invoke → accuracy + stability 두 지표
- **Semantic judge** (`semantic-judge.sh` Haiku) — 자연어 필드의 의미 동등성 평가 + 값 hash 캐시
- **match-semantic** (`match-semantic.sh`) — strict/structural 기본 + semantic 필드는 judge 위임
- **Calibration set** (`calibrate-judge.sh`) — judge 신뢰도 정량 측정 (judge-calibration/ 디렉토리)
- **Suggester** (`suggest-improvements.sh` Opus) — 회귀 발견 시 SKILL.md 의 어디를 어떻게 고치면 좋을지 구체 edit 제안
- 첫 dogfooding 대상: `hns:glossary` (`examples/hns-glossary/` 참조)

## 평가 loop (v0.2)

**측정 → 진단 → 개선 → 재측정** 의 closed loop:

1. `/skill-eval:baseline` — N 회 호출 → 사람 1회 컨펌 → expected.json 박힘 + accuracy/stability 첫 기록
2. 사용자가 스킬 수정
3. `/skill-eval:run` — N 회 호출 → match-semantic 으로 매칭 → 회귀 발견 시 suggester 호출 → suggestions.md 생성
4. 사용자가 suggestions.md 참고해서 SKILL.md 추가 수정
5. `/skill-eval:run` 다시 → accuracy/stability 비교 → 개선 여부 확인
6. 의도된 개선이면 `/skill-eval:promote` 로 새 baseline 으로 승격

## v0.2 에서 제외 (v0.3+ 예정)

- CI 게이팅 모드 (exit code 임계값)
- 캐시 TTL/eviction 정책 (현재는 무한 캐시)
- multi-acceptable expected (`oneOf` 정답 후보 집합)
- 부수효과 큰 스킬 평가 (`/ideabank:impl` 등) — isolated workspace 필요
- tier 프리셋 (dev/ci/full)

## Quickstart (5분)

평가 대상 프로젝트 루트에서:

```bash
# 1) Goldset 디렉토리 + schema 정의
mkdir -p goldset/hns-glossary/{schema,fixtures,cases/case-001}
cp ai/plugins/skill-quality-eval/examples/hns-glossary/schema/* goldset/hns-glossary/schema/
cp -r ai/plugins/skill-quality-eval/examples/hns-glossary/fixtures/toy-domain goldset/hns-glossary/fixtures/
echo "skill-id: hns-glossary\nargs: '--shallow'" > goldset/hns-glossary/cases/case-001/input.yml

# 2) baseline 생성 (사람 1회 컨펌)
claude
/skill-eval:baseline hns-glossary

# 3) 스킬 수정 후 회귀 측정
/skill-eval:run hns-glossary

# 4) 직전 baseline 과 비교 (자동, 결과는 diff-vs-baseline.md)
ls goldset/hns-glossary/snapshots/

# 5) 의도된 개선이면 새 baseline 으로 승격
/skill-eval:promote hns-glossary {snapshot-id}
```

## 디렉토리 컨벤션

```
goldset/{skill-id}/
├── schema/
│   ├── output.schema.json        # 평가용 JSON 계약
│   └── matching-policy.json      # 필드별 매칭 모드 / sort-by / match-by
├── fixtures/                      # 코드베이스 의존 스킬의 입력 픽스처
├── snapshots/
│   ├── 2026-05-22-baseline/
│   │   ├── source-skill/         # 그 시점 원본 스킬 사본
│   │   ├── forked-skill/         # source + JSON overlay
│   │   ├── cases/{id}/
│   │   │   ├── input.yml
│   │   │   └── expected.json     # 정답 (baseline 만 보유)
│   │   ├── report.md
│   │   └── report.json
│   └── 2026-05-23-after-fix/
│       ├── source-skill/
│       ├── forked-skill/
│       ├── cases/{id}/
│       │   ├── actual.json       # 실제 출력
│       │   └── diff.md
│       ├── diff-vs-baseline.md
│       └── report.md
└── current -> snapshots/2026-05-22-baseline
```

자세한 spec 은 `references/snapshot-layout.md`, `references/matching-policy.md`, `references/overlay-template.md` 참조.

## 의존성

- `claude` CLI (Claude Code 2.x+) — `--plugin-dir` / `--json-schema` 플래그 사용
- `jq` (≥ 1.6) — JSON 비교 / 정규화

## 라이선스

MIT
