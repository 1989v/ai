---
name: diet
description: Use to shrink the harness after a model upgrade or when CLAUDE.md, skills, agents, or hooks have grown — measures real usage from session transcripts and proposes removals.
disable-model-invocation: true
---

# /hns:diet

철학: `docs/philosophy/bitter-lesson.md`. 기준: `references/diet-criteria.md`. **사용 증거 없이 제거하지 않고, 승인 없이 제거하지 않는다.**

## 1. 측정
```bash
P=~/.claude/projects/$(pwd | sed 's#/#-#g')          # 프로젝트 세션 기록 디렉토리
ls "$P"/*.jsonl | wc -l                                 # 세션 수 (보존 기간 안)
grep -oh '"name":"Skill","input":{"skill":"[^"]*"' "$P"/*.jsonl | sed 's/.*"skill":"//;s/"$//' | sort | uniq -c | sort -rn   # 스킬 호출
grep -oh '"subagent_type":"[^"]*"' "$P"/*.jsonl | sort | uniq -c | sort -rn                                                # 에이전트
grep -l '"/hns:' "$P"/*.jsonl | wc -l                                                                                       # 사용자가 직접 친 세션
wc -l CLAUDE.md .claude/rules/*.md 2>/dev/null
```
플랫폼 진단도 붙인다: `/skill-doctor`(미사용 스킬 + 컨텍스트 비용), `/doctor`(CLAUDE.md 트림 제안), `/context`(실제 로드된 메모리 파일).

## 2. CLAUDE.md
200줄 초과분은 분류한다 — **always**(빌드 명령·핵심 원칙·포인터)만 남기고, **on-demand** 는 `.claude/rules/` `paths:` 또는 스킬로, **derivable**(모듈 목록·최근 변경)은 삭제, **duplicate** 는 포인터로. `/doctor` 트림 제안과 대조한다.

## 3. 규칙·스킬·에이전트·훅 후보
| 기준 | 신호 |
|---|---|
| 미사용 | 보존 기간 전체에서 호출 0, `/skill-doctor` 미사용 |
| 플랫폼 중복 | 플랫폼이 내장한 기능(경로 규칙·워크트리·컴팩션·메모리)을 다시 구현 |
| 모델 중복 | 규칙 없이도 모델이 올바르게 하는 것(샘플 3회로 확인) |
| 상위 규칙 포함 | 다른 규칙이 같은 범위 |
| 스택 무관 | 현재 프로젝트 기술과 무관 |

## 4. 제안 → 승인 → 실행 → 기록
후보마다 현재 역할·근거·제거 시 영향을 표로 제시한다. 승인된 것만 제거/아카이브하고 `docs/changelog/harness-changelog.md` 에 `[date] [diet] [removed: X] [reason]` 을 남긴다. 문제가 생기면 `/hns:evolve` 로 복원.

## 보호 항목
CLAUDE.md(압축만), `hns:agent-behavior`, `references/harness-philosophy.md`, 훅 스크립트(수준을 낮출 수는 있다).
