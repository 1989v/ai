# What is Harness Engineering?

## Origin
Mitchell Hashimoto (2026-02): AI 에이전트가 같은 실수를 반복하는 문제를 해결하기 위해 명명.

> 에이전트가 실수를 할 때마다 그 실수가 다시는 반복되지 않도록 엔지니어링하는 것

## The Horse Metaphor
- AI 모델 = 야생말 (힘은 있지만 방향 없음)
- 하네스 = 마구 (고삐, 안장, 끈)
- 마구를 채워도 말이 느려지지 않음 → 오히려 올바른 방향으로 집중

## Model ≠ Harness
모델이 아닌 것이 모두 하네스:
- CLAUDE.md, AGENTS.md
- MCP servers
- Skills, Commands
- Hooks
- docs/, agent-os/

## Harness vs Prompt

| | Prompt | Harness |
|---|---|---|
| 방식 | "이거 하지 마" 부탁 | 실수 불가능한 구조 설계 |
| 성격 | 부탁 | 강제 |
| 비유 | 안전모 쓰라고 말하기 | 안전모 없으면 출입문 안 열림 |

## References
- Mitchell Hashimoto's agents.md approach
- OpenAI: 3 engineers, 5 months, zero code written
- LangChain: 30위 → 5위 (model unchanged, harness improved)
