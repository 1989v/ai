# doc-scaffolding Plugin Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AI 작업 환경을 표준화된 컨벤션으로 스캐폴딩하는 Claude Code 플러그인 구현

**Architecture:** Claude Code 플러그인 구조 (`.claude-plugin/plugin.json` + `skills/` + `agents/` + `templates/`). 스킬은 마크다운 기반 프롬프트, 템플릿은 Mustache/텍스트 기반.

**Tech Stack:** Claude Code Plugin System, Markdown, HTML/CSS/JS (doc-site)

**Spec:** `docs/superpowers/specs/2026-03-16-ai-common-plugins-design.md` Section 3

---

## Chunk 1: 레포 구조 + 플러그인 메타데이터

### Task 1: 레포 디렉터리 스캐폴딩

**Files:**
- Create: `plugins/doc-scaffolding/.claude-plugin/plugin.json`
- Create: `plugins/ai-debugger/.claude-plugin/plugin.json`
- Create: `shared/lib/.gitkeep`
- Create: `shared/templates/.gitkeep`
- Create: `.gitignore`

- [ ] **Step 1: 루트 .gitignore 생성**

```gitignore
.DS_Store
.idea/
*.swp
node_modules/
```

- [ ] **Step 2: doc-scaffolding plugin.json 생성**

```json
{
  "name": "doc-scaffolding",
  "description": "AI workspace scaffolding: generates CLAUDE.md and standardized docs tree for any project",
  "version": "0.1.0",
  "author": { "name": "gideok-kwon" },
  "license": "MIT",
  "keywords": ["scaffolding", "docs", "claude-md", "ai-workspace"]
}
```

Path: `plugins/doc-scaffolding/.claude-plugin/plugin.json`

- [ ] **Step 3: ai-debugger plugin.json 생성 (레포 공통 스캐폴딩의 일부)**

> Note: ai-debugger의 스킬/에이전트 구현은 별도 플랜(`2026-03-16-ai-debugger.md`)에서 진행. 여기서는 레포 디렉터리 구조만 생성.

```json
{
  "name": "ai-debugger",
  "description": "API debugging agent with full IO capture, log analysis, and codebase exploration",
  "version": "0.1.0",
  "author": { "name": "gideok-kwon" },
  "license": "MIT",
  "keywords": ["debugging", "api", "io-interceptor", "log-analysis"]
}
```

Path: `plugins/ai-debugger/.claude-plugin/plugin.json`

- [ ] **Step 4: shared 디렉터리 생성**

> Note: v1에서 shared/lib의 프로젝트 분석 로직은 각 스킬의 SKILL.md 프롬프트 내에 기술. 향후 공통 로직이 커지면 실행 가능한 스크립트로 분리.

```bash
mkdir -p shared/lib shared/templates
touch shared/lib/.gitkeep shared/templates/.gitkeep
```

- [ ] **Step 5: 커밋**

```bash
git add .gitignore plugins/ shared/
git commit -m "feat: scaffold repo structure with plugin metadata"
```

---

### Task 2: doc-scaffolding 템플릿 — CLAUDE.md

**Files:**
- Create: `plugins/doc-scaffolding/templates/claude-md/default.md`
- Create: `plugins/doc-scaffolding/templates/claude-md/spring-kotlin.md`

- [ ] **Step 1: 기본 CLAUDE.md 템플릿 작성**

범용 프로젝트용 기본 템플릿. 스킬이 프로젝트 분석 결과를 기반으로 섹션을 채운다.

```markdown
# {{projectName}} AI Working Agreement

## 1. Project Intent

{{projectDescription}}

## 2. Architecture Principles

{{architecturePrinciples}}

## 3. Module & Build Rules

{{moduleRules}}

## 4. Package Naming Convention

{{packageConvention}}

## 5. Test Rules

{{testRules}}

## 6. API Response Format

{{apiFormat}}
```

Path: `plugins/doc-scaffolding/templates/claude-md/default.md`

- [ ] **Step 2: Spring Boot + Kotlin 특화 템플릿 작성**

MSA 프로젝트의 CLAUDE.md를 참조하여, Spring Boot + Kotlin + Clean Architecture에 최적화된 템플릿 작성. Clean Architecture 레이어, Kotest/MockK 테스트 규칙, Gradle 멀티모듈 규칙 등 포함.

Path: `plugins/doc-scaffolding/templates/claude-md/spring-kotlin.md`

- [ ] **Step 3: 커밋**

```bash
git add plugins/doc-scaffolding/templates/
git commit -m "feat: add CLAUDE.md templates (default + spring-kotlin)"
```

---

### Task 3: doc-scaffolding 템플릿 — docs 트리

**Files:**
- Create: `plugins/doc-scaffolding/templates/docs-tree/adr/_template.md`
- Create: `plugins/doc-scaffolding/templates/docs-tree/architecture/overview.md`
- Create: `plugins/doc-scaffolding/templates/docs-tree/policies/.gitkeep`
- Create: `plugins/doc-scaffolding/templates/docs-tree/plans/.gitkeep`
- Create: `plugins/doc-scaffolding/templates/docs-tree/index.md`

- [ ] **Step 1: ADR 템플릿 작성**

```markdown
# ADR-{{number}}: {{title}}

## Status

Proposed | Accepted | Deprecated | Superseded by ADR-XXX

## Context

{{context}}

## Decision

{{decision}}

## Consequences

### Positive
- {{positive}}

### Negative
- {{negative}}
```

- [ ] **Step 2: architecture/overview.md 템플릿 작성**

프로젝트 아키텍처 개요 문서 템플릿. 기술 스택, 레이어 구조, 주요 의존성 등.

- [ ] **Step 3: docs/index.md 템플릿 작성**

```markdown
# {{projectName}} Documentation

## Structure

- `adr/` — Architecture Decision Records
- `architecture/` — Architecture documentation
- `plans/` — Implementation plans
- `policies/` — Business domain policies
```

- [ ] **Step 4: 커밋**

```bash
git add plugins/doc-scaffolding/templates/docs-tree/
git commit -m "feat: add docs tree templates (adr, architecture, index)"
```

---

## Chunk 2: doc-scaffolding 스킬 구현

### Task 4: scaffold 스킬 (메인 엔트리)

**Files:**
- Create: `plugins/doc-scaffolding/skills/scaffold/SKILL.md`

- [ ] **Step 1: scaffold SKILL.md 작성**

```markdown
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
수집한 요구사항은 생성되는 문서에 직접 반영된다.

### 4. 검증

doc-scaffolding:doc-validate 스킬을 호출하여 생성된 문서가 실제 코드 구조와 일치하는지 검증.

### 5. (선택) HTML 사이트 생성

사용자에게 HTML 문서 사이트 생성 여부를 물어보고, 원하면 doc-scaffolding:doc-site 호출.

## MSA 멀티 모듈 감지

settings.gradle.kts에 여러 include가 있거나, 서비스 디렉터리 패턴(`*/src/main`)이 감지되면:
- 루트에 공통 docs/ 생성
- 각 서비스 모듈에 개별 docs/ 생성 (policies/ 포함)

## Integration

- **Calls:** doc-scaffolding:doc-gen, doc-scaffolding:doc-validate, doc-scaffolding:doc-site
- **Standalone:** 이 스킬은 `/scaffold`로 직접 호출
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/doc-scaffolding/skills/scaffold/
git commit -m "feat: add scaffold skill - main entry point for AI workspace setup"
```

---

### Task 5: doc-gen 스킬

**Files:**
- Create: `plugins/doc-scaffolding/skills/doc-gen/SKILL.md`

- [ ] **Step 1: doc-gen SKILL.md 작성**

```markdown
---
name: doc-gen
description: Use when generating CLAUDE.md and docs/ tree for a project - creates AI-friendly documentation structure based on project analysis and user requirements
---

# Document Tree Generator

## Overview

프로젝트에 CLAUDE.md와 표준 docs/ 트리를 생성한다. 프로젝트 분석 결과와 사용자 요구사항을 문서에 직접 반영한다.

## 생성 구조

```
{project}/
├── CLAUDE.md
└── docs/
    ├── adr/
    │   └── _template.md
    ├── architecture/
    │   └── overview.md
    ├── plans/
    ├── policies/
    └── index.md
```

## CLAUDE.md 생성 규칙

1. 프로젝트의 언어/프레임워크에 맞는 템플릿을 선택
   - Kotlin/Spring → `templates/claude-md/spring-kotlin.md`
   - 기타 → `templates/claude-md/default.md`
2. 프로젝트 분석 결과로 각 섹션 채우기:
   - 모듈 구조 → Module & Build Rules
   - 패키지 경로 → Package Naming Convention
   - 테스트 프레임워크 감지 → Test Rules
3. 사용자가 전달한 커스텀 요구사항을 해당 섹션에 직접 기록

## docs/ 생성 규칙

1. `templates/docs-tree/`의 구조를 복사
2. `index.md`에 프로젝트명과 구조 설명 기록
3. `architecture/overview.md`에 감지된 아키텍처 정보 기록
4. `policies/`에 사용자가 전달한 비즈니스 정책 기록

## MSA 멀티 모듈 생성 규칙

settings.gradle.kts에서 서비스 모듈을 감지한 경우:
1. **루트 docs/**: adr/, architecture/, plans/ (프로젝트 공통)
2. **각 서비스 모듈 docs/**: policies/ 중심 (도메인별 비즈니스 규칙)

예시 (MSA 커머스):
```
{project}/
├── CLAUDE.md
├── docs/                       # 공통
│   ├── adr/
│   ├── architecture/
│   └── plans/
├── product/docs/               # product 도메인
│   ├── policies/
│   └── index.md
├── order/docs/                 # order 도메인
│   ├── policies/
│   └── index.md
└── search/docs/                # search 도메인
    ├── policies/
    └── index.md
```

## 기존 파일 충돌 처리

- CLAUDE.md가 이미 존재하면: 사용자에게 덮어쓸지, 병합할지 질문
- docs/ 내 기존 파일: 보존하고 누락된 것만 추가

## Integration

- **Called by:** doc-scaffolding:scaffold
- **Standalone:** `/doc-gen`으로 직접 호출 가능
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/doc-scaffolding/skills/doc-gen/
git commit -m "feat: add doc-gen skill - generates CLAUDE.md and docs tree"
```

---

### Task 6: doc-validate 스킬

**Files:**
- Create: `plugins/doc-scaffolding/skills/doc-validate/SKILL.md`

- [ ] **Step 1: doc-validate SKILL.md 작성**

```markdown
---
name: doc-validate
description: Use when verifying that documentation matches actual codebase - validates docs against code structure, not the other way around
---

# Document Validator

## Overview

docs를 기준으로 코드베이스를 검증한다. 문서가 source of truth이다.

## 검증 방향: docs → code

문서에 기술된 내용이 실제 코드와 일치하는지 확인한다.
코드가 문서를 따르는지 검증하는 것이지, 코드에서 문서를 생성하는 것이 아니다.

## 검증 항목

### 1. CLAUDE.md 검증
- Module & Build Rules에 기술된 모듈이 실제 존재하는가
- Package Naming Convention이 실제 패키지 구조와 일치하는가
- Test Rules에 명시된 프레임워크가 실제 의존성에 포함되어 있는가

### 2. docs/architecture/ 검증
- overview.md에 기술된 레이어 구조가 실제 패키지에 존재하는가
- 서비스 간 통신 방식이 실제 코드와 일치하는가

### 3. docs/policies/ 검증
- 비즈니스 규칙이 코드에 반영되어 있는가 (best effort — 완전 자동화 불가, 주요 패턴 체크)

### 4. 참조 무결성
- 문서에 언급된 파일 경로가 실제 존재하는가
- 문서에 언급된 패키지/클래스명이 실제 존재하는가

## 출력 형식

```
=== Doc Validation Report ===

✅ CLAUDE.md: Module structure matches (5/5 modules found)
✅ CLAUDE.md: Package convention matches
⚠️  CLAUDE.md: Test framework mismatch - docs say "Kotest" but found "JUnit" in dependencies
❌ docs/architecture/overview.md: References "payment" service but directory not found
✅ docs/policies/: 3 policy files verified

Summary: 3 passed, 1 warning, 1 error
```

## Integration

- **Called by:** doc-scaffolding:scaffold (생성 후 자동 검증)
- **Standalone:** `/doc-validate`로 수동 실행 (변경 시 반복 검증)
- **향후 자동 트리거**: Claude Code hook (`post-edit`)으로 docs/ 또는 src/ 변경 시 자동 실행 (v1에서는 수동만 지원)
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/doc-scaffolding/skills/doc-validate/
git commit -m "feat: add doc-validate skill - validates docs against codebase"
```

---

### Task 7: doc-site 스킬

**Files:**
- Create: `plugins/doc-scaffolding/skills/doc-site/SKILL.md`
- Create: `plugins/doc-scaffolding/skills/doc-site/site-template.html`

- [ ] **Step 1: doc-site SKILL.md 작성**

```markdown
---
name: doc-site
description: Use when converting docs/ markdown files into a navigable HTML site with directory tree sidebar - generates static HTML with no external dependencies
---

# Documentation Site Generator

## Overview

docs/ 디렉터리의 마크다운 파일을 디렉터리 네비게이션이 포함된 정적 HTML 사이트로 변환한다.

## 생성 방식

1. docs/ 디렉터리를 재귀 스캔하여 마크다운 파일 목록 수집
2. 각 마크다운을 HTML로 변환
3. 디렉터리 구조를 좌측 사이드바 트리 네비게이션으로 생성
4. 단일 `docs-site/index.html` 또는 `docs-site/` 디렉터리에 정적 파일 출력

## 기술 제약

- **외부 의존성 없음**: npm, pip 등 설치 불필요
- **인라인 CSS/JS**: 단일 HTML로 동작 가능
- **마크다운 → HTML**: 스킬이 직접 변환 (코드 블록, 테이블, 링크 지원)

## HTML 구조

site-template.html을 참조하여 다음 구조로 생성:
- 좌측 사이드바: 디렉터리 트리 (폴더 접기/펼치기)
- 메인 영역: 선택된 문서의 HTML 렌더링
- 상단: 프로젝트명 + 검색 (optional)

## 출력 경로

`{project}/docs-site/index.html` (기본)
- .gitignore에 `docs-site/` 추가 권장

## Integration

- **Called by:** doc-scaffolding:scaffold (선택적)
- **Standalone:** `/doc-site`로 직접 호출
```

- [ ] **Step 2: site-template.html 작성**

단일 HTML 파일 템플릿. 좌측 사이드바 + 메인 콘텐츠 영역. CSS는 인라인, JS는 트리 네비게이션과 마크다운 렌더링 처리. `{{navigation}}`, `{{content}}`, `{{projectName}}` 플레이스홀더 포함.

- [ ] **Step 3: 커밋**

```bash
git add plugins/doc-scaffolding/skills/doc-site/
git commit -m "feat: add doc-site skill - generates navigable HTML from docs/"
```

---

## Chunk 3: 오케스트레이터 에이전트 + 검증

### Task 8: scaffolding-agent 오케스트레이터

**Files:**
- Create: `plugins/doc-scaffolding/agents/scaffolding-agent.md`

- [ ] **Step 1: scaffolding-agent.md 작성**

```markdown
---
name: scaffolding-agent
description: |
  Use this agent to orchestrate AI workspace scaffolding.
  Analyzes project structure, collects custom requirements from user,
  generates CLAUDE.md + docs tree, validates against codebase,
  and optionally generates HTML documentation site.
model: inherit
---

# Scaffolding Agent

당신은 AI 워크스페이스 스캐폴딩 에이전트입니다.
프로젝트에 표준화된 AI 작업 환경을 구축합니다.

## 실행 순서

### 1. 프로젝트 분석

프로젝트 루트에서 다음을 분석하세요:
- 빌드 파일 (build.gradle.kts, package.json, pyproject.toml 등)으로 언어/프레임워크 감지
- 모듈 구조 (settings.gradle.kts의 include, 워크스페이스 설정 등) 감지
- 기존 CLAUDE.md, docs/ 존재 여부 확인

### 2. 커스텀 요구사항 수집

사용자에게 한 번에 하나씩 질문:
1. 프로젝트의 핵심 목적
2. 아키텍처 원칙
3. 테스트 규칙
4. API 포맷 컨벤션
5. 비즈니스 정책

### 3. 문서 생성

doc-scaffolding:doc-gen 스킬의 지침에 따라 CLAUDE.md + docs/ 트리를 생성하세요.
수집한 요구사항은 별도 config가 아닌 문서 자체에 반영합니다.

### 4. 검증

doc-scaffolding:doc-validate 스킬의 지침에 따라 생성된 문서를 검증하세요.
문제가 발견되면 사용자에게 보고하고 수정합니다.

### 5. (선택) HTML 사이트

사용자에게 HTML 문서 사이트 생성 여부를 물어보세요.
원하면 doc-scaffolding:doc-site 스킬을 따라 생성합니다.

## MSA 멀티 모듈 처리

settings.gradle.kts에 서비스 모듈이 여러 개 포함된 경우:
- 루트에 공통 docs/ (adr, architecture, plans)
- 각 서비스 모듈에 개별 docs/ (policies 중심)
```

- [ ] **Step 2: 커밋**

```bash
git add plugins/doc-scaffolding/agents/
git commit -m "feat: add scaffolding-agent orchestrator"
```

---

### Task 9: MSA 프로젝트 대상 검증

**Files:**
- 없음 (수동 검증)

- [ ] **Step 1: doc-scaffolding 플러그인을 MSA 프로젝트에 등록**

`/Users/gideok-kwon/IdeaProjects/msa/.claude/settings.json`에 플러그인 경로 추가:

```json
{
  "plugins": [
    "/Users/gideok-kwon/IdeaProjects/ai/plugins/doc-scaffolding"
  ]
}
```

- [ ] **Step 2: MSA 프로젝트에서 `/scaffold` 호출하여 동작 확인**

검증 항목:
- 프로젝트 분석이 Kotlin/Spring Boot, 멀티모듈을 올바르게 감지하는지
- 커스텀 요구사항 질문이 적절한지
- 생성된 CLAUDE.md가 기존 것과 유사한 품질인지
- doc-validate가 올바르게 검증하는지

- [ ] **Step 3: 발견된 문제 수정 후 커밋**

```bash
git add plugins/doc-scaffolding/
git commit -m "fix: address issues found during MSA project validation"
```
