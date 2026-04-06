# ADR-002: GC Three Execution Modes

## Status: Accepted (2026-04-06)

## Context
GC는 하네스 3기둥 중 Evolution의 핵심. 수동만 지원하면 실행 빈도가 낮고, 자동만 지원하면 과도한 개입.

## Decision
수동(/hns:harness-gc) + 이벤트(hook) + 스케줄(cron) 3모드 지원.

## Consequences
- (+) 프로젝트 성격에 맞는 모드 선택 가능
- (-) 3가지 트리거 경로 관리 필요
