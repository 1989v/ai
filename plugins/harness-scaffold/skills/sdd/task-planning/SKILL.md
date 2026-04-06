---
name: task-planning
description: Use when breaking down specs into task groups - defines grouping strategy, dependencies, and test limits
---

# Task Planning Rules

## Grouping Strategy
- Group by skill/layer (DB Layer, API Layer, Frontend, Test Review)
- Each group starts with test writing (2-8 focused tests)
- Each group ends with verification sub-task
- Strategic ordering: foundation first, dependent layers after

## Required Metadata per Group
```yaml
dependencies: [None | Task Group N]
phase: [phase-identifier]
required_skills: [skill-list for implementation]
```

## Test Limits (Focused Testing Philosophy)
- Each task group: 2-8 focused tests maximum
- Tests cover only critical behaviors, not exhaustive
- Test review group: max 10 additional tests for gap filling
- Total per feature: ~16-34 tests
- Verification runs ONLY newly written tests, not entire suite

## Output Quality Contract
- Target: <= 600 lines
- Explicit verification sub-tasks per group with concrete commands
- Completion gate: "Mark complete only after verification passes"
- Execution metadata: phase + required_skills per group
- Acceptance criteria per group

## Execution Order Section
Include recommended implementation sequence based on dependencies.

## NEVER
- Create group without dependencies field
- Create group without verification sub-task
- Pursue exhaustive test coverage
- Skip acceptance criteria
