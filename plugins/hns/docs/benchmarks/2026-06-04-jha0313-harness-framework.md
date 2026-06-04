# Benchmark: jha0313/harness_framework (2026-06-04)

**Sources**
- 영상: [메타 시니어 엔지니어가 알려주는 하네스 세팅 | 빈 프로젝트에서 하네스 직접 만들기](https://youtu.be/AQOvNx87Urs)
- 레포: https://github.com/jha0313/harness_framework (Python 100%, 6 commits, ⭐226)
- 튜토리얼: https://raspy-roll-970.notion.site/340f7725c9d98176b68bd31c823c7540 (fetch 차단 — 레포 코드로 대체 분석)

---

## 1. 외부 소스 정체

"빈 프로젝트에서 직접 만드는 **미니멀 하네스**"의 레퍼런스 구현. 전체가 **마크다운 5개 + Python 1개**.

```
CLAUDE.md                      # 60줄급 컨텍스트 (기술스택/CRITICAL 규칙/명령어)
.claude/commands/harness.md    # step 설계 + 파일생성 + 실행 워크플로우 정의
.claude/commands/review.md     # 5항목 체크리스트 리뷰
.claude/settings.json          # Stop 훅(lint+build+test) + PreToolUse 훅(위험명령 차단)
docs/{PRD,ARCHITECTURE,ADR,UI_GUIDE}.md   # 가드레일 템플릿
scripts/execute.py             # ★ 멀티세션 step 오케스트레이터 (핵심)
```

### 핵심 메커니즘 — `execute.py`

이 레포의 정체성은 사실상 `execute.py` 하나다. **step 단위 헤드리스 멀티세션 드라이버**:

| 기능 | 구현 |
|------|------|
| **프로세스 격리** | step마다 `claude -p --dangerously-skip-permissions --output-format json` 별도 프로세스 spawn → step별 완전 fresh 컨텍스트 |
| **상태 머신** | `phases/index.json`(top) + `phases/{task}/index.json`(step별 `pending/completed/error/blocked`) |
| **가드레일 주입** | 매 step 프롬프트에 CLAUDE.md + docs/*.md 전문 자동 삽입 |
| **컨텍스트 누적** | 완료 step의 `summary` 한 줄을 다음 step 프롬프트에 전달 |
| **자가 교정** | 실패 시 최대 3회 재시도, 직전 `error_message`를 다음 프롬프트에 피드백 |
| **2단계 커밋** | `feat(code)` + `chore(metadata)` 분리 |
| **타임스탬프** | started/completed/failed/blocked_at 자동 기록 |
| **브랜치 자동화** | `feat-{task}` 생성/checkout |
| **휴먼 게이트** | `blocked`(API키·인증·수동설정) 만나면 즉시 중단 후 사람 대기 |

### step 설계 원칙 (harness.md)
Scope 최소화(step당 1레이어) · 자기완결성(외부 참조 금지) · 사전 준비 강제(읽을 파일 명시) · **시그니처 수준 지시**(인터페이스만, 구현은 에이전트 재량) · **AC = 실행 가능 커맨드** · 구체적 금지("X 하지 마라, 이유 Y").

---

## 2. 비교: 우리에게 없는 패턴 (harness_framework 우위)

### ★ HIGH — 헤드리스 멀티세션 실행 드라이버 (가장 큰 갭)
- **그쪽**: `execute.py`가 step마다 **새 프로세스(`claude -p`)** 를 띄워 컨텍스트를 물리적으로 리셋하고, 요약을 앞으로 전달하며, 실패를 피드백하고, step별 커밋하고, JSON으로 재개 가능하게 한다. **비대화형 = CI/야간 무인 실행 가능.**
- **HNS**: `implement-tasks`/`orchestrate-tasks`는 **한 세션 안에서 subagent 위임** 또는 worktree 병렬뿐. Ralph Loop(BUILD→TEST→FIX max3)는 **개념·세션 내부**에만 존재하고 *실행 드라이버*가 없다. "First/Continuation Window" 구분은 있으나 **사람이 수동으로 새 세션을 켜야** 성립한다.
- **의미**: 2026-04-06 벤치마크에서 이미 "multi-context-window 프로토콜 / structured state / git checkpoint"를 *개념적으로* 채택했는데, harness_framework는 그걸 하나로 묶은 **실행 가능한 드라이버**의 완성형을 보여준다. ← 이게 차세대 업그레이드 후보 1번.

### ★ MED — 머신리더블 상태 머신 (재개성)
- **그쪽**: `index.json` 명시적 status 전이 + 자동 타임스탬프 → `error`/`blocked` 고치고 `pending`으로 되돌려 재실행하는 **결정론적 resume**.
- **HNS**: `status.md`/`progress.md`(비정형) + tasks.md 체크박스 + open-questions.yml. resume이 서술형("progress.md 읽고 재개")이라 드라이버가 강제하지 못한다.

### LOW — 이미 있거나 사소
| 항목 | 상태 |
|------|------|
| AI-slop FE 안티패턴 표(blur/gradient-text/purple/rounded-2xl 등) | HNS `validate-fe-design` + fe-design-validation-protocol에 존재 — 구체성만 cross-check |
| 시그니처 수준 step 지시 | HNS task-planning이 이미 인터페이스 중심 |
| 위험명령 PreToolUse 차단 | HNS hooks/enforcement에 존재 |
| Stop 훅 lint+build+test | HNS 3-tier hooks에 존재 |

---

## 3. 비교: 우리에게만 있는 패턴 (HNS 압도)

harness_framework는 **MVP 실행기**일 뿐 아래는 전무하다:

- **6차원 스펙 리뷰** (architecture/domain/implementation/security/test/usecase) + skillset
- **Lifecycle**: GC / evolve / diet / **audit** / **doctor**(5-layer 헬스체크) / **glossary**(유비쿼터스 사전)
- **계층적 위임** (모노레포 nearest-ancestor CLAUDE.md 누적)
- **3-tier 훅** (reminder/feedback/enforcement) — 그쪽은 enforcement 1단계 고정
- doc-gen · drift-check · 철학 문서 · ADR · changelog
- worktree 기반 병렬 실행

→ harness_framework는 HNS의 상위집합이 **아니다**. **단일 축(실행 드라이버)** 에서만 더 날카롭다. 기획·리뷰·라이프사이클 성숙도는 HNS가 압도적.

---

## 4. 결론: 개선/리펙터/차세대 필요여부

| 판단 | 결론 |
|------|------|
| 전면 리펙터 | **불필요.** 6-layer 아키텍처 건전하고 범위가 훨씬 넓다. |
| 차세대 업그레이드 | **1건 권장 (HIGH).** 헤드리스 step-runner — HNS의 *개념적* Ralph Loop를 *자동·재개가능·CI실행가능* 루프로 승격. |
| 부수 채택 | structured JSON 상태 머신(runner 백엔드), FE-slop 표 구체성 cross-check. |

**핵심 통찰**: 영상의 테제("빈 프로젝트에서 미니멀 하네스 직접 만들기")는 HNS의 `diet` 철학(모델↑→하네스↓)과 같은 방향이다. harness_framework는 *적게 만들되 실행은 자동화한다*. HNS는 *많이 만들었지만 실행은 수동이다*. 둘을 합치면: **HNS의 풍부한 기획/리뷰 + harness_framework의 자동 실행 드라이버.**

---

## 5. 채택 결과 (2026-06-04 적용, ADR-004)

> 최초 권장안은 `execute.py`를 그대로 포팅한 외부 python step-runner였으나, 검토 중 **python 드라이버의 유일한 고유 가치가 "무인/CI 실행"** 임이 드러났다. 현재 워크플로(대화형)에 해당 없음 + step별 독립 컨텍스트는 Claude Code subagent로 이미 가능 → **외부 드라이버 제거, 세션 내 Step 모드로 실현.**

### A. (적용) Step 모드 — 세션 내 step별 독립 컨텍스트 실행
- `references/step-execution-protocol.md` — Task-Group(기본) vs Step 모드 정의. Step 모드: tasks.md → self-contained `steps/step{N}.md` → step마다 새 subagent(독립 컨텍스트) 순차 실행 + 자가교정(max 3) + step별 커밋.
- `hns:start` PHASE 5 승인 게이트에서 구현 방식 [1]/[2] 질의 → 모드 2는 `orchestrate-tasks` Step mode 위임.
- `templates/steps/{index.json, step-template.md}` 배포.
- **python 미채택**: `execute.py` 직접 포팅 제거. 무인 실행 외 가치는 세션 내 subagent로 대체.

### B. (적용) `steps/index.json` JSON 상태 머신
- `status.md`(서술) 옆 `steps/index.json`(머신리더블, pending/completed/error/blocked + 타임스탬프 + summary) 병행 → 결정론적 resume.

### C. (적용) `validate-fe-design` 안티패턴 표 보강 (A-9~A-12)
- "Powered by AI" 배지 / 네온 글로우 애니메이션 / 균일 rounded-2xl / 배경 gradient orb 추가. (blur·gradient-text·purple는 기존 A-7/A-2/A-3에 이미 존재.)

### 미채택
| 항목 | 사유 |
|------|------|
| 외부 python step-runner (`execute.py` 포팅) | 무인 실행 외 가치는 세션 내 subagent로 대체 가능. 미완·미사용 기능을 남기지 않음 |
| `--dangerously-skip-permissions` 기본화 | HNS 안전철학(confirmation Level)과 충돌 |
| 5개 파일로 축소 | HNS의 6차원 리뷰/라이프사이클은 핵심 가치, 감량 대상 아님 |
| Next.js 전제 템플릿 | HNS는 언어/스택 중립 — spring-kotlin 등 멀티 템플릿 유지 |
