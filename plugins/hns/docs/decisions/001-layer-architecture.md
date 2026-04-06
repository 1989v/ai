# ADR-001: 6-Layer Architecture

## Status: Accepted (2026-04-06)

## Context
harness-scaffold v0.1.0은 4레이어(Core/SDD/Review/Project-Adaptive). 하네스 엔지니어링 3기둥(Context/Enforcement/Evolution) 중 Evolution이 완전 부재. doc-scaffolding이 별도 플러그인으로 분리되어 init과 기능 중복.

## Decision
Docs, Lifecycle 레이어를 추가하여 6레이어로 확장.

## Consequences
- (+) 3기둥 완전 구현
- (+) doc-scaffolding 흡수로 단일 플러그인 관리
- (-) 커맨드 10→19, 에이전트 7→10, 스킬 10→20+ 으로 증가
