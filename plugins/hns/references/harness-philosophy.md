# Harness Philosophy Reference

이 문서는 harness-scaffold의 모든 커맨드/스킬이 따르는 근본 원칙을 요약.
상세 내용은 `docs/philosophy/` 참조.

## Core Principles

1. **구조 > 부탁**: 프롬프트로 부탁하지 말고, 구조적으로 강제
2. **성공은 조용히, 실패만 시끄럽게**: onSuccess: silent, onFailure: feedback/block
3. **점진적 진화**: 한번에 완벽하게가 아니라 실패마다 한 줄씩 추가
4. **모델↑ → 하네스↓**: 불필요해진 규칙은 제거 (Bitter Lesson)
5. **지도 > 설명서**: CLAUDE.md는 60줄 이하, 나머지는 필요할 때 로딩

## Context Routing Contract

```
Level 0: CLAUDE.md (항상)
Level 1: command requires (커맨드별)
Level 2: index.yml keyword match (자동, max 3, threshold 2+)
```
