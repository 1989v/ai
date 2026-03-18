# AI Common Plugins

다른 서비스에 공통으로 활용할 Claude Code 플러그인 모노레포.

## 플러그인 목록

| 플러그인 | 설명 | 주요 스킬 |
|---------|------|----------|
| **doc-scaffolding** | AI 워크스페이스 스캐폴딩 | `/scaffold`, `/doc-gen`, `/doc-validate`, `/doc-site` |
| **ai-debugger** | API 디버깅 에이전트 | `/io-setup`, `/curl-gen` + debug-agent |

---

## 설치 방법

### 방법 1: CLI로 마켓플레이스 등록 (권장)

대상 프로젝트에서 Claude Code 실행 후:

```
/plugin marketplace add /path/to/ai
```

이후 플러그인 설치:

```
/plugin install doc-scaffolding@ai-common
/plugin install ai-debugger@ai-common
```

### 방법 2: settings.json 직접 편집

대상 프로젝트의 `.claude/settings.json` (팀 공유) 또는 `.claude/settings.local.json` (개인용):

```json
{
  "extraKnownMarketplaces": {
    "ai-common": {
      "source": {
        "source": "directory",
        "path": "/path/to/ai"
      }
    }
  },
  "enabledPlugins": {
    "doc-scaffolding@ai-common": true,
    "ai-debugger@ai-common": true
  }
}
```

### 방법 3: GitHub 원격 레포 (배포 후)

```json
{
  "extraKnownMarketplaces": {
    "ai-common": {
      "source": {
        "source": "github",
        "repo": "1989v/ai"
      }
    }
  }
}
```

---

## 사용법

### doc-scaffolding

프로젝트에 AI 작업 환경을 구축:

```
/scaffold
```

1. 프로젝트 분석 (언어, 프레임워크, 모듈 구조 자동 감지)
2. 커스텀 요구사항 수집
3. CLAUDE.md + docs/ 트리 생성
4. 생성된 문서를 코드베이스 기준으로 검증
5. (선택) HTML 문서 사이트 생성

개별 스킬도 단독 사용 가능:

```
/doc-gen          # CLAUDE.md + docs 트리만 생성
/doc-validate     # 기존 문서를 코드 기준으로 검증
/doc-site         # docs/를 HTML 사이트로 변환
```

### ai-debugger

#### 1단계: IO 인터셉터 설치 (최초 1회)

```
/io-setup
```

대상 서비스에 통합 AOP 기반 IO 캡처를 주입:
- `@Profile("debug-trace")` — 프로필 미활성 시 오버헤드 0
- Spring Data Repository 자동 캡처
- `@IOTraceable` 어노테이션으로 WebClient, Kafka 등 명시적 캡처

#### 2단계: 디버깅

이슈 상황을 자연어로 전달하면 debug-agent가 자동 분석:

```
"주문 API에서 500 에러가 나요"
"결제 API 응답이 3초 이상 걸려요"
"상품 검색 결과가 비어있어요"
```

debug-agent 동작 순서:
1. curl 명령 생성 + 실행 (X-Trace-Id 자동 추가)
2. 코드베이스 + docs/ 분석 (코드 우선)
3. 필요 시 IO 로그 조회 (Redis 2단계 쿼리)
4. 구조화된 답변 생성

#### 디버그 모드 활성화

```bash
# 서비스 실행 시 프로필 추가
SPRING_PROFILES_ACTIVE=debug-trace ./gradlew :order:app:bootRun
```

---

## 레포 구조

```
ai/
├── plugins/
│   ├── doc-scaffolding/              # AI 워크스페이스 스캐폴딩
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/
│   │   │   ├── scaffold/SKILL.md
│   │   │   ├── doc-gen/SKILL.md
│   │   │   ├── doc-validate/SKILL.md
│   │   │   └── doc-site/SKILL.md
│   │   ├── agents/scaffolding-agent.md
│   │   └── templates/
│   │
│   └── ai-debugger/                  # API 디버그 에이전트
│       ├── .claude-plugin/plugin.json
│       ├── skills/
│       │   ├── io-interceptor/SKILL.md
│       │   ├── curl-gen/SKILL.md
│       │   ├── log-query/SKILL.md
│       │   ├── code-explore/SKILL.md
│       │   ├── data-analyze/SKILL.md
│       │   └── answer-gen/SKILL.md
│       ├── agents/debug-agent.md
│       └── templates/interceptors/
│
├── shared/
└── docs/
    ├── superpowers/specs/            # 설계 스펙
    └── superpowers/plans/            # 구현 플랜
```

## 기술 스택 지원

| | Kotlin/Spring | Python/FastAPI | TypeScript/Express |
|---|:---:|:---:|:---:|
| doc-scaffolding | v1 | v1 | v1 |
| ai-debugger IO 캡처 | v1 | 향후 | 향후 |
