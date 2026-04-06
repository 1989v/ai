# Prompting Tone Guide

Claude 4.6+ 모델은 이전 모델보다 지시 따르기 능력이 높아졌으므로,
과도한 강조 표현이 오히려 overtriggering을 유발할 수 있다.

## Principle

강한 어조는 줄이고, 조건부 명확성을 높인다.

## Before → After

| Before (over-prompting) | After (calibrated) |
|------------------------|-------------------|
| `CRITICAL: You MUST use this tool when...` | `Use this tool when...` |
| `EXTREMELY IMPORTANT: NEVER skip...` | `Do not skip...` |
| `ABSOLUTELY MUST invoke...` | `Invoke when applicable.` |
| `This is not negotiable.` | (제거 — 지시 자체로 충분) |
| `If you think there is even a 1% chance...` | `If a skill might apply, invoke it first.` |

## When Strong Tone IS Appropriate

- Safety-critical 제약 (data loss, security)
- Iron Laws (Ralph Loop 3회 실패 시 STOP 등)
- 사용자 승인 게이트 (L3 변경)

## Application

- 신규 스킬/커맨드 작성 시 이 가이드 참고
- 기존 스킬은 점진적으로 톤 조정 (harness-diet 사이클에서)
- 톤 다운 후 동작 변화 관찰 → 문제 시 원복

## Source

[Claude Prompting Best Practices — Agentic Systems](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#agentic-systems):
> "Where you might have said 'CRITICAL: You MUST use this tool when...', you can use more normal prompting like 'Use this tool when...'"
