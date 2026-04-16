# Ideabank Plugin

날 것의 아이디어를 구조화된 PRD로 발전시키고, 브레인스토밍으로 가다듬은 뒤, 실제 서비스로 구현하는 파이프라인.

## Pipeline

```
tempidea.md에 아이디어 메모
    ↓
/ideabank:init    → ideabank/docs/{id}-{slug}.md (PRD 초안, draft)
    ↓
/ideabank:bs      → 핑퐁 브레인스토밍 (draft → refined → ready)
    ↓
/ideabank:impl    → 서비스 scaffolding + 구현 (ready → implemented)
```

## Quick Start

### 1. 디렉토리 준비

프로젝트 루트에 `ideabank/` 디렉토리를 만든다:

```bash
mkdir -p ideabank/docs
```

### 2. 아이디어 작성

`ideabank/tempidea.md` 파일에 아이디어를 자유롭게 기록한다:

```markdown
## Pending Ideas

1. 실시간 주식 자동매매 봇
   - 퀀트 전략 기반
   - 한국투자증권 API 연동
   - 백테스트 기능

2. 사내 IT 용어 사전 서비스
   - 코드베이스에서 자동 추출
   - 검색 + 시각화
```

형식은 자유. 번호만 매기면 된다.

### 3. 파이프라인 실행

```bash
# 1차 PRD 생성
/ideabank:init 1

# 대화형 브레인스토밍으로 방향 잡기
/ideabank:bs 1

# 준비되면 구현
/ideabank:impl 1
```

## Commands

| Command | Description |
|---------|-------------|
| `/ideabank:init [번호\|all]` | tempidea.md → 1차 PRD 초안 생성 |
| `/ideabank:bs [번호]` | PRD를 대화형으로 브레인스토밍 |
| `/ideabank:impl [번호]` | ready 상태의 PRD를 서비스로 구현 |

## PRD Lifecycle

```
draft → refined → ready → implemented
 (init)   (bs)      (bs)     (impl)
```

| Status | 의미 | 다음 단계 |
|--------|------|----------|
| `draft` | init으로 생성된 초안 | `/ideabank:bs`로 브레인스토밍 |
| `refined` | 1회 이상 브레인스토밍 완료 | `/ideabank:bs`로 추가 보완 또는 ready 전환 |
| `ready` | 구현 가능 수준으로 확정 | `/ideabank:impl`로 구현 시작 |
| `implemented` | 서비스 구현 완료 | Completed Ideas로 이동 |

## Directory Convention

```
{project-root}/
├── ideabank/                    # 아이디어 저장소 (일반 디렉토리 또는 git submodule)
│   ├── tempidea.md              # 날 것의 아이디어 + PRD 현황 표
│   ├── README.md                # (선택) ideabank 소개
│   └── docs/                    # PRD 문서
│       ├── 1-quant-trader.md
│       ├── 2-code-dictionary.md
│       └── ...
├── {service-a}/                 # impl로 생성된 서비스 A
├── {service-b}/                 # impl로 생성된 서비스 B
└── ...
```

### Private Repo로 관리하기

아이디어를 비공개로 관리하려면 `ideabank/`를 private git submodule로 분리할 수 있다:

```bash
# private-repo 플러그인 사용
/private-repo:private-repo ideabank
```

이후에도 동일한 경로(`ideabank/tempidea.md`, `ideabank/docs/`)로 접근 가능.

## PRD Template

`/ideabank:init`이 생성하는 PRD 구조:

```markdown
---
id: 1
title: 서비스 제목
status: draft
created: 2026-01-01
updated: 2026-01-01
service-dir: my-service
---

# 서비스 제목

## 1. 개요
## 2. 핵심 기능
## 3. 사용자 시나리오
## 4. 기술 스택 (예상)
## 5. 서비스 구조 (예상)
## 6. 미결 사항 / 질문
## 7. 원본 아이디어
```

## Integration

- **private-repo plugin**: `/ideabank:impl`에서 private 서비스 분리 시 자동 연동
- **superpowers:writing-plans**: 복잡한 구현 시 상세 실행 계획 수립에 활용

## Installation

```bash
# marketplace에서 설치
claude plugins install ideabank@ai-common

# 또는 로컬 테스트
claude --plugin-dir ./plugins/ideabank
```
