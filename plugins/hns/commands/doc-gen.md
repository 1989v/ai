---
name: doc-gen
description: "[hns] Generate CLAUDE.md and docs/ tree for the current project"
---

# /hns:doc-gen

## Purpose
프로젝트에 CLAUDE.md와 docs/ 트리를 생성한다.

## Required Inputs
- Access to project root directory

## Expected Outputs
- CLAUDE.md
- docs/ directory tree

---

## Overview

프로젝트 분석 결과와 수집된 커스텀 요구사항을 바탕으로 CLAUDE.md와 docs/ 트리를 생성한다.
docs가 source of truth이며, 별도 config 파일 없이 요구사항은 문서 자체에 반영된다.

## Generated Structure

```
{project-root}/
├── CLAUDE.md                    # AI 작업 지침 (메인 진입점)
└── docs/
    ├── index.md                 # 문서 목차 및 개요
    ├── adr/                     # Architecture Decision Records
    │   └── README.md
    ├── architecture/            # 아키텍처 문서
    │   └── overview.md
    ├── plans/                   # 개발 계획 및 로드맵
    │   └── README.md
    └── policies/                # 비즈니스 정책 및 규칙
        └── README.md
```

## Template Selection

언어/프레임워크 감지에 따라 CLAUDE.md 템플릿을 선택:

### Kotlin/Spring (build.gradle.kts 감지 시)
- 빌드 도구: Gradle (Kotlin DSL)
- 테스트 섹션: Kotest + MockK 기본값 제안
- 패키지 구조: `src/main/kotlin`, `src/test/kotlin`
- Spring Boot 관련 섹션 포함 (프로파일, 설정)

### Node/TypeScript (package.json 감지 시)
- 빌드 도구: npm/yarn/pnpm (lockfile로 판별)
- 테스트 섹션: Jest 또는 Vitest 기본값 제안
- 패키지 구조: `src/`, `tests/`
- TypeScript 설정 섹션 포함

### Python (pyproject.toml 또는 requirements.txt 감지 시)
- 빌드 도구: Poetry/pip (pyproject.toml 유무로 판별)
- 테스트 섹션: pytest 기본값 제안
- 패키지 구조: 프로젝트명 디렉터리 또는 `src/`

### 기타 / 알 수 없음
- 언어 중립적 템플릿 사용
- 빈 섹션으로 생성 후 사용자에게 채우도록 안내

## CLAUDE.md 구성 섹션

생성되는 CLAUDE.md는 다음 섹션을 포함:

```markdown
# {Project Name}

## 프로젝트 개요
{핵심 목적 - 수집된 요구사항 반영}

## 아키텍처
{아키텍처 원칙 - 수집된 요구사항 반영}
docs/architecture/overview.md 참조

## 모듈 구조
{감지된 모듈 목록}

## 개발 규칙

### 빌드 & 실행
{언어별 빌드/실행 명령}

### 테스트
{테스트 프레임워크 및 규칙 - 수집된 요구사항 반영}

### 코드 컨벤션
{언어별 기본 컨벤션}

## API 포맷
{API 응답 포맷 컨벤션 - 수집된 요구사항 반영}

## 문서 구조
docs/ 트리 참조 (docs/index.md)
```

## 커스텀 요구사항 반영

수집된 요구사항은 별도 파일이 아닌 문서에 직접 작성:
- 핵심 목적 → CLAUDE.md 프로젝트 개요 섹션
- 아키텍처 원칙 → CLAUDE.md 아키텍처 섹션 + docs/architecture/overview.md
- 테스트 규칙 → CLAUDE.md 테스트 섹션
- API 포맷 → CLAUDE.md API 포맷 섹션
- 비즈니스 정책 → docs/policies/ 하위에 개별 파일로 생성

## MSA 멀티 모듈 구조

settings.gradle.kts에 여러 서비스 모듈이 감지되면:

```
{project-root}/
├── CLAUDE.md                    # 공통 AI 지침
└── docs/                        # 공통 문서
    ├── index.md
    ├── adr/
    ├── architecture/
    └── plans/

{service-module}/
└── docs/                        # 서비스별 문서
    ├── index.md
    └── policies/                # 서비스별 비즈니스 정책
```

## 기존 파일 충돌 처리

CLAUDE.md 또는 docs/가 이미 존재하는 경우:
1. 사용자에게 충돌 사실을 알림
2. 선택지 제공:
   - **덮어쓰기**: 기존 파일을 새 파일로 교체
   - **병합**: 기존 내용을 보존하고 새 섹션만 추가
   - **건너뛰기**: 해당 파일 생성 생략
3. 파일별로 개별 결정 가능

## Integration

- **Called by:** hns:init (Phase 3)
- **Standalone:** `/hns:doc-gen`으로 직접 호출 가능
- **Calls:** 없음 (최종 생성 스킬)
