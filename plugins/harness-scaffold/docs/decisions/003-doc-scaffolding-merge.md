# ADR-003: doc-scaffolding Merge into harness-scaffold

## Status: Accepted (2026-04-06)

## Context
doc-scaffolding과 harness-scaffold의 init이 CLAUDE.md 생성 기능 중복. 두 플러그인을 동시에 관리하는 비용.

## Decision
doc-scaffolding의 doc-gen, doc-validate, doc-site(→doc-html)를 harness-scaffold의 Docs 레이어로 흡수. doc-scaffolding:scaffold는 제거하고 init이 역할 대체.

## Consequences
- (+) 단일 플러그인으로 전체 하네스 관리
- (+) init → doc-gen 자연스러운 흐름
- (-) doc-scaffolding 플러그인 폐기 필요 (migration)
