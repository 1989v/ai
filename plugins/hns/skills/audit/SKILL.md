---
name: audit
description: Use to compare the current harness against an external benchmark (repo, post, or web search) and get an adopt / not-adopt report.
disable-model-invocation: true
argument-hint: "[url | repo path | auto]"
---

# /hns:audit

## Purpose
외부 소스와 비교하여 하네스 개선 기회를 식별한다.

## Required Inputs
- External source (URL, repo path, or "auto" for web search)

## Expected Outputs
- docs/benchmarks/YYYY-MM-DD-{source}.md

---

## Process
1. **Source**: 외부 소스 지정 (URL, repo path, or "자동 검색")
   - 레포: 해당 프로젝트의 CLAUDE.md/AGENTS.md/.claude/ 구조 분석
   - 포스트: 하네스 엔지니어링 관련 내용 추출
   - 자동: 최신 하네스 엔지니어링 트렌드 웹 검색

2. **Compare**: 현재 hns 구조와 비교
   - 있는데 우리에겐 없는 패턴
   - 우리에겐 있는데 다른 곳엔 없는 패턴 (과잉?)
   - 구조적 차이점

3. **Report**: `docs/benchmarks/YYYY-MM-DD-{source-name}.md` 생성
   - 비교 요약
   - 채택 권장 항목
   - 미채택 사유

4. **Adopt**: 사용자가 채택 결정 → `evolve`로 반영

## Execution

1. Ask user for source (or use "auto" for web search)
2. Delegate to `hns:harness-auditor` agent (source + current plugin/project harness paths); it analyzes the source's harness structure
3. Compare with current hns (plugin + project harness)
4. Generate benchmark report
5. User decides adoption → delegate to `/hns:evolve`

## NEVER
- 자동으로 외부 패턴 적용 (항상 사용자 결정)
- 비교 없이 "좋아 보이니까" 추가
- 실사용 증거(세션 기록 호출 수) 없이 "우리에게 필요하다" 판정
