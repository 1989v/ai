---
name: code-check
description: Use to record a code check that must be re-verified on every future change — a defect worth remembering, a user correction about code, or a finding kept by review. Judges promotion in a fresh context, then appends to docs/checks/ with its source. This is the only entrance to those files.
when_to_use: 체크리스트에 넣어줘, 이거 항상 확인하게, 코딩 때 꼭 보게, 새 검토항목, 재발 방지
argument-hint: "[check description] [--scope common|<module>]"
---

# /hns:code-check

**흉터 목록의 유일한 입구.** `docs/checks/*.md` 는 이 스킬만 쓴다 — 다른 스킬·에이전트·세션이 직접 append 하지 않는다.

두 시점이 **같은 파일**을 본다: `hns:implementer` 가 코딩 전에 읽고(자기대조), 구현 후 리뷰가 검증 영역으로 읽는다(적대적 사냥). 그래서 한 곳만 갱신하면 양쪽에 반영된다.

> 이건 **운영 체크**(코딩할 때마다 대조할 규칙)지 맥락 메모가 아니다.
> "이거 꼭 체크하게" = 여기. "다음에 이어가게 기억해둬" = auto memory. 헷갈리면 **묻는다**.
> 규칙의 대상이 코드가 아니면(도구 오용·경로 규칙·톤) 여기가 아니라 `/hns:evolve` 다.

## 입력
- 후보 — 자연어 설명(무엇을·왜), 또는 구현 후 리뷰가 `keep` 으로 판정한 발견, 또는 `/hns:wrapup` 의 반복 실패
- (선택) 대상 모듈. 없으면 2단계에서 정한다

## 1. 승격 심판 (fresh context — 필수)
후보를 만든 세션은 자기가 다룬 이슈를 중요하게 본다. 판정은 **새 서브에이전트**에 맡긴다(`Agent`, 읽기 전용). 넘길 것: 후보 전건 · 현재 `docs/checks/` 실물 경로 · 관련 `docs/conventions/`.

> **판단 기울기 = 관대.** 아래에 **명백히** 걸릴 때만 탈락, 애매하면 승격한다. 한 줄의 비용은 싸고, 걸러져서 재발한 사고는 비싸다. 목록이 비대해지는 건 나중에 정리로 풀리지만, 삼켜진 교훈은 복구가 안 된다.

| 탈락 기준 | 뜻 |
|---|---|
| 스타일 취향 | 린터·컨벤션 몫. 흉터 목록은 결함 재발 방지용 |
| 지엽성 | 그 파일 한 곳에서만 성립 — 반경이 모듈 이상이어야 한 줄 값어치 |
| 재발 불가 | 1회성 오타·이번 변경 한정 사정 |
| 대조 방해 | 매번 대조할 때 오탐을 부르거나 과잉 방어를 유도하거나 기존 항목과 중복 |

이미 같은 항목이 있으면 **추가가 아니라 기존 항목 다듬기**로 판정한다(있는데 위반됐다 = 그 문장이 안 읽힌 것).
반환: 승격 / 다듬기 / 탈락(전건 사유). 후보가 전부 탈락이면 "이번엔 승격 없음" — 억지 승격 금지.

## 2. 행선지
- **전 모듈에 성립하는가** — 어느 모듈에서도 참인가(언어·프레임워크 함정, 동시성, 입력 검증) → `docs/checks/common.md`
- 근거가 **이 프로젝트의 공용 클래스·인프라·팀 규약**이면 범용이 아니다 → 그 모듈의 `docs/checks/{module}.md`
- 그 외 전부 → `docs/checks/{module}.md` (`{module}` = 최상위 모듈/서비스 디렉토리 이름. 파일이 없으면 첫 항목이니 `${CLAUDE_PLUGIN_ROOT}/templates/docs-tree/checks/_template.md` 로 만든다)
- 불명확하면 **추측하지 말고 묻는다**.

## 3. 기록
해당 카테고리 절에 한 줄로 append한다(맞는 절이 없으면 새 헤더):
```
- [ ] **핵심 요점** — 왜 위험한지 / 어떻게 해야 하는지. (출처: YYYY-MM-DD, {PR·리뷰·직접발견})
```
- **출처는 지우지 않는다.** 이 목록의 줄은 실제 사고 하나당 하나씩 자란 것이라, 출처가 사라지면 다음 사람이 "왜 있는지" 몰라 되돌린다. 항목을 옮길 땐 괄호를 함께 옮기고, 지울 땐 커밋 메시지에 사유를 남긴다.
- **분량 상한(soft) 140줄** — 넘으면 append 전에 멈추고 ⓐ 흡수 가능한 항목 ⓑ `common` 에서 특정 모듈로 강등 가능한 항목을 각각 최대 3개 제시해 정리 여부를 묻는다. 구현 프롬프트에 통째로 들어가므로 길수록 안 읽힌다.
- `common.md` 에서 항목을 **삭제**할 때는, 그것을 주입받던 모든 모듈 파일에 등가 항목이 있음을 `grep` 으로 확인한 뒤에만.

## 4. 확인
추가·다듬은 항목을 보여주고 "이대로 둘까요?" 를 묻는다. 승인 후 `docs/changelog/harness-changelog.md` 에 `[date] [code-check] [{파일}: {요점}] [근거: {출처}]`.

## NEVER
- 심판 없이 바로 append (후보를 만든 세션이 자기 판정을 겸하면 이 스킬의 존재 이유가 사라진다)
- 출처 없는 항목
- 한 번의 발견으로 여러 줄 추가
- 코드가 아닌 규칙(경로·도구·톤)을 여기에 — 그건 `/hns:evolve`
