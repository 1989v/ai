# Benchmark: Claude Agentic Best Practices (2026-04-06)

**Source**: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#agentic-systems

## Summary

Anthropic 공식 Claude prompting best practices 중 Agentic systems 섹션 분석.
Claude 4.6 모델의 에이전틱 시스템 구축 권장사항을 현재 HNS 하네스와 비교.

---

## Already Reflected (채택 불필요)

| 권장사항 | HNS 현재 상태 |
|---------|-------------|
| 병렬 도구 호출 최적화 | subagent-driven-development 스킬 |
| 자율성-안전성 균형 (destructive action 확인) | agent-behavior/confirmation.md Level 1-3 |
| 과도한 엔지니어링 방지 | CLAUDE.md에 명시 |
| 증거 기반 탐색 (investigate before answering) | review-protocol file:line 증거 필수 |
| Self-correction 체인 | spec-review + Ralph Loop |

## Adopted (채택 항목)

### 1. Compaction State 저장 강화

- **근거**: "save progress and state to memory before context window refreshes"
- **현재**: 체크리스트만 존재, 자동 state 파일 저장 패턴 미명시
- **변경**: compaction 스킬에 progress state 저장 단계 명시

### 2. Multi-Context Window 프로토콜

- **근거**: "Use a different prompt for the very first context window" + "future context windows to iterate on a todo-list"
- **현재**: implement-tasks에 암묵적이나 명시적 구분 없음
- **변경**: implement-tasks에 first-window vs continuation-window 프로토콜 추가

### 3. Structured State + Unstructured Notes 분리

- **근거**: "Use structured formats for state data" + "Use unstructured text for progress notes"
- **현재**: open-questions.yml은 있으나 테스트 상태 추적 파일 없음
- **변경**: Ralph Loop에서 test-status 기록 패턴 추가

### 4. Git Checkpoint 전략

- **근거**: "Git provides a log of what's been done and checkpoints that can be restored"
- **현재**: git commit은 하지만 의도적 checkpoint 전략 없음
- **변경**: implementation 스킬에 task group 완료마다 commit 명시

### 5. Subagent 과용 가드레일

- **근거**: "may spawn subagents when a direct grep is faster and sufficient"
- **현재**: dispatching-parallel-agents 스킬에 과용 방지 없음
- **변경**: 가드레일 추가 — 단일 파일, 순차 작업, grep 충분 시 직접 수행

### 6. Over-prompting 톤 다운

- **근거**: "CRITICAL: You MUST use → Use this tool when..." 톤 다운 권장
- **현재**: 일부 스킬에서 강한 어조 사용
- **변경**: audit 레퍼런스에 기록, 점진적 적용

## Not Adopted (미채택)

| 권장사항 | 미채택 사유 |
|---------|----------|
| Adaptive thinking / effort 파라미터 | API 레벨 설정, 하네스 스킬과 무관 |
| Frontend aesthetics | 백엔드 MSA 프로젝트, 해당 없음 |
| Prefill migration | Claude Code 환경에서 해당 없음 |
| tests.json 형식 강제 | 기존 tasks.md 체크박스 + status.md로 충분 |
