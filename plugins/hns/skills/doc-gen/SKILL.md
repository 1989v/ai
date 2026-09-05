---
name: doc-gen
description: Use to generate or fill gaps in a project's CLAUDE.md and docs/ tree from the detected stack and a few questions — default fills only missing files, --full regenerates.
disable-model-invocation: true
argument-hint: "[--full]"
---

# /hns:doc-gen

메인 컨텍스트에서 실행한다(질문이 필요하다). 기본은 **빈 곳만 채운다**: 없는 파일 → 생성, 내용 있는 파일 → 건너뜀, placeholder(`TODO` `TBD` 80% 이상)만 있는 파일 → 생성. `--full` 이면 파일별로 덮어쓰기/병합/건너뜀을 묻는다.

## 1. 분석
빌드 파일로 언어/프레임워크·모듈·테스트 프레임워크·빌드/테스트 명령을 뽑는다(`hns:init` 1 단계와 같은 규칙). 멀티 모듈(`settings.gradle.kts` 에 서비스 여러 개)이면 루트 `docs/`(adr·architecture·plans) + 서비스별 `docs/`(policies).

## 2. 질문 (없는 정보만, 한 번에 하나)
핵심 목적 · 아키텍처 원칙 · 테스트 규칙 · API 포맷 · 비즈니스 정책.

## 3. 생성
```
CLAUDE.md                         프로젝트 개요 · 아키텍처(→ docs/architecture/overview.md) · 모듈 · 빌드/테스트 명령 · 컨벤션 포인터 · /hns:start
docs/index.md                     목차
docs/architecture/overview.md     스택 · 레이어 · 빌드/테스트 명령
docs/adr/README.md · docs/plans/README.md · docs/policies/*.md(정책은 개별 파일)
```
템플릿은 스택별(`templates/claude-md/spring-kotlin.md` 등, 없으면 `default.md`). 수집한 답은 별도 설정 파일이 아니라 문서 본문에 쓴다.

## 4. 품질 게이트
REJECT: 다른 문서와 80% 이상 중복 · 산문 없이 불릿만 · 의미 있는 내용 3줄 미만. ACCEPT: 프로젝트 특화 서술 + 코드/명령/경로 참조 1개 이상. 거부된 문서는 `[DRAFT]` 접두사로 두고 보완을 안내한다.

## 5. 검증
`hns:validate --docs`.
