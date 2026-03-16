---
name: scaffold
description: Use when setting up AI workspace for a new or existing project - analyzes project structure, collects custom requirements, generates CLAUDE.md and docs tree
---

# AI Workspace Scaffolding

## Overview

프로젝트에 표준화된 AI 작업 환경을 스캐폴딩한다. 프로젝트를 분석하고, 사용자의 커스텀 요구사항을 수집하여, CLAUDE.md와 docs/ 트리를 생성한다.

## Process

### 1. 프로젝트 분석

프로젝트 루트에서 다음을 감지:
- **언어/프레임워크**: build.gradle.kts → Kotlin/Spring, package.json → Node/TS, pyproject.toml → Python
- **모듈 구조**: settings.gradle.kts의 include 목록, 또는 monorepo 워크스페이스
- **기존 문서**: CLAUDE.md, docs/ 존재 여부

### 2. 커스텀 요구사항 수집

사용자에게 순차적으로 질문:
1. 프로젝트의 핵심 목적은? (한 문장)
2. 아키텍처 원칙이 있는가? (예: Clean Architecture, Hexagonal 등)
3. 테스트 프레임워크/규칙은? (예: Kotest + MockK, Jest, pytest 등)
4. API 응답 포맷 컨벤션이 있는가?
5. 추가로 문서화할 비즈니스 정책이 있는가?

### 3. 문서 생성

doc-scaffolding:doc-gen 스킬을 호출하여 CLAUDE.md + docs/ 트리 생성.
수집한 요구사항은 생성되는 문서에 직접 반영된다 (별도 config 파일 없음, docs가 source of truth).

### 4. 검증

doc-scaffolding:doc-validate 스킬을 호출하여 생성된 문서가 실제 코드 구조와 일치하는지 검증.

### 5. (선택) HTML 사이트 생성

사용자에게 HTML 문서 사이트 생성 여부를 물어보고, 원하면 doc-scaffolding:doc-site 호출.

## MSA 멀티 모듈 감지

settings.gradle.kts에 여러 include가 있거나, 서비스 디렉터리 패턴(`*/src/main`)이 감지되면:
- 루트에 공통 docs/ 생성 (adr, architecture, plans)
- 각 서비스 모듈에 개별 docs/ 생성 (policies 중심)

## Integration

- **Calls:** doc-scaffolding:doc-gen, doc-scaffolding:doc-validate, doc-scaffolding:doc-site
- **Standalone:** 이 스킬은 `/scaffold`로 직접 호출
