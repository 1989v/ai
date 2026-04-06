---
description: "[hns] 6-layer cross-consistency verification: docs ↔ code ↔ specs ↔ tasks"
---

# /hns:verify-crosscheck

## Purpose
프로젝트의 문서, 스펙, 태스크, 코드 간 교차 일관성을 6개 레이어에서 검증.

## Required Inputs
- docs/ directory
- agent-os/ directory (if exists)
- docs/specs/{feature}/ (if checking specific feature)

## Expected Outputs
- CROSSCHECK_REPORT.md in spec folder or project root

---

## Layer 1: SOT Internal Consistency

docs/ 내 문서들 간 모순 체크:
- docs/index.md에 나열된 문서가 실제로 존재하는지
- docs 내 상호 참조 링크가 유효한지
- CLAUDE.md와 docs/architecture/overview.md 간 모듈 목록 일치

## Layer 2: docs ↔ agent-os Sync

- agent-os/standards/의 규칙이 CLAUDE.md에도 반영되어 있는지
- agent-os/product/tech-stack.md와 CLAUDE.md 빌드 명령 일치
- agent-os/config.yml 설정과 실제 파일 구조 일치

## Layer 3: Product ↔ Specs

- agent-os/product/mission.md의 목표가 spec에 반영되어 있는지
- 스펙이 미션과 무관한 범위를 포함하지 않는지

## Layer 4: Standards ↔ Specs

- agent-os/standards/의 코딩 규칙이 spec의 기술 결정과 충돌하지 않는지
- spec에서 표준을 위반하는 결정이 있으면 ADR 존재 여부 확인

## Layer 5: Specs ↔ Tasks

- spec.md의 모든 SR(Specific Requirement)에 대응하는 task가 있는지
- tasks.md에 spec에 없는 과잉 task가 없는지
- AC → task 매핑 완전성

## Layer 6: Tasks ↔ Code

- tasks.md에서 완료 표시된 task의 실제 구현 존재 여부
- 미완료 task에 대응하는 코드가 이미 존재하지 않는지
- 코드 변경이 task에 매핑되지 않는 경우 탐지

## Output

```markdown
# Crosscheck Report — {date}

| Layer | Status | Issues |
|-------|--------|--------|
| 1. SOT Internal | PASS | 0 |
| 2. docs ↔ agent-os | WARN | 1 |
| 3. Product ↔ Specs | PASS | 0 |
| 4. Standards ↔ Specs | PASS | 0 |
| 5. Specs ↔ Tasks | FAIL | 2 |
| 6. Tasks ↔ Code | PASS | 0 |

Overall: FAIL

## Details
### Layer 2: docs ↔ agent-os
- ⚠ tech-stack.md lists Java 25 but CLAUDE.md says Java 21

### Layer 5: Specs ↔ Tasks
- ✗ SR-003 has no corresponding task
- ✗ Task Group 4 has no spec reference
```
