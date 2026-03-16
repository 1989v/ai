# AI Common Plugins Design Spec

## 1. Overview

다른 서비스에 공통으로 활용할 AI 작업 에이전트/스킬을 Claude Code 플러그인으로 제공하는 레포.
두 개의 독립 플러그인(`doc-scaffolding`, `ai-debugger`)을 하나의 모노레포에서 관리한다.

### 대상 기술 스택

- 주력: Spring Boot (Kotlin)
- 지원: Python (FastAPI), TypeScript (Express/Node)

### 배포 방식

Claude Code 플러그인. 대상 프로젝트의 `.claude/settings.json`에서 플러그인 경로로 등록.

```json
{
  "plugins": [
    "/path/to/ai/plugins/doc-scaffolding",
    "/path/to/ai/plugins/ai-debugger"
  ]
}
```

---

## 2. Repository Structure

```
ai/
├── plugins/
│   ├── doc-scaffolding/              # Feature 0: AI 워크스페이스 스캐폴딩
│   │   ├── plugin.json
│   │   ├── skills/
│   │   │   ├── scaffold/             # 메인 스캐폴딩 (커스텀 요구사항 수집 포함)
│   │   │   ├── doc-gen/              # CLAUDE.md + docs 트리 생성
│   │   │   ├── doc-site/             # HTML 정적 사이트 생성
│   │   │   └── doc-validate/         # 문서 검증
│   │   ├── agents/
│   │   │   └── scaffolding-agent.md  # 오케스트레이터
│   │   └── templates/
│   │       ├── claude-md/            # CLAUDE.md 템플릿
│   │       └── docs-tree/            # docs 구조 템플릿
│   │
│   └── ai-debugger/                  # Feature 1: API 디버그 에이전트
│       ├── plugin.json
│       ├── skills/
│       │   ├── curl-gen/             # 자연어 → curl 명령 생성
│       │   ├── io-interceptor/       # IO 인터셉터 코드 주입
│       │   ├── log-query/            # IO 로그 조회
│       │   ├── code-explore/         # 코드베이스 탐색
│       │   ├── data-analyze/         # IO 데이터 분석
│       │   └── answer-gen/           # 답변 생성
│       ├── agents/
│       │   └── debug-agent.md        # 오케스트레이터
│       └── templates/
│           └── interceptors/         # 언어별 IO 인터셉터 템플릿
│
├── shared/                           # 플러그인 간 공통 리소스
│   ├── lib/                          # 공유 유틸 (언어 감지, 프로젝트 분석 등)
│   └── templates/                    # 공통 템플릿
│
└── docs/                             # 이 레포 자체 문서
    ├── adr/
    ├── architecture/
    ├── plans/
    ├── policies/
    └── superpowers/specs/            # 설계 문서
```

---

## 3. Feature 0: doc-scaffolding

### 3.1 목적

표준화된 AI 작업 환경을 프로젝트에 스캐폴딩. CLAUDE.md 및 docs 하위에 AI 친화적 문서 트리를 생성하고, 코드베이스와의 정합성을 검증한다.

### 3.2 스킬 구성

| 스킬 | 트리거 | 역할 |
|------|--------|------|
| `scaffold` | `/scaffold` 명시 호출 | 메인 엔트리. 프로젝트 분석 + 커스텀 요구사항 수집 후 하위 스킬 오케스트레이션 |
| `doc-gen` | scaffold에서 호출 또는 단독 `/doc-gen` | CLAUDE.md + docs/ 트리 생성 |
| `doc-site` | 명시 호출 `/doc-site` | docs/ 마크다운을 디렉터리 네비게이션 포함 HTML 정적 사이트로 변환 |
| `doc-validate` | scaffold에서 호출 또는 단독 `/doc-validate` | 생성된 문서가 코드베이스/요구사항에 부합하는지 검증 |

### 3.3 요구사항과 문서의 관계

사용자의 커스텀 요구사항은 scaffold 과정에서 **docs 문서 자체에 반영**된다.
별도 config 파일 없이, docs가 유일한 진실의 원천(source of truth).

- scaffold 시 수집한 요구사항 → CLAUDE.md, docs/architecture/, docs/policies/ 등에 직접 기록
- `doc-validate`는 **docs 기준으로 코드베이스를 검증** (docs → code 방향)

### 3.4 오케스트레이터: scaffolding-agent

```
[사용자 호출] → scaffolding-agent
    ├── 1. 프로젝트 분석 (언어, 프레임워크, 모듈 구조 감지)
    ├── 2. 사용자에게 커스텀 요구사항 질문 (0-1)
    ├── 3. doc-gen 스킬 호출 → 요구사항을 반영하여 CLAUDE.md + docs 트리 생성 (0-2)
    ├── 4. doc-validate 스킬 호출 → docs 기준으로 코드 검증 (0-4)
    └── 5. (선택) doc-site 스킬 호출 → HTML 생성 (0-3)
```

### 3.5 변경 시 검증 트리거

v1에서는 `/doc-validate` 수동 호출로 검증. 자동 트리거 방식은 향후 확장:
- Claude Code hook (`post-edit` 이벤트)으로 docs/ 또는 src/ 변경 시 자동 실행
- CI/CD 파이프라인 연동 (Out of Scope v1)

### 3.6 생성되는 표준 문서 구조

```
{project}/
├── CLAUDE.md                        # AI 작업 규약 (프로젝트 맞춤형)
└── docs/
    ├── adr/                         # Architecture Decision Records
    │   └── _template.md
    ├── architecture/                # 아키텍처 문서
    │   └── overview.md
    ├── plans/                       # 구현 계획
    ├── policies/                    # 비즈니스 도메인 정책
    └── index.md                     # 문서 인덱스
```

MSA 멀티 모듈 레포의 경우, 각 서비스 모듈 안에 동일 구조가 생성된다.
모놀리스/단일 서비스 레포면 루트에 이 구조 하나. scaffold가 모듈 구조를 자동 감지하여 판단.

### 3.7 doc-site: HTML 생성 방식

- docs/ 디렉터리 스캔 → 마크다운 → HTML 변환
- 좌측 사이드바에 디렉터리 트리 네비게이션
- 단일 `index.html` + 인라인 CSS/JS로 외부 의존성 없이 생성 (또는 `docs-site/` 디렉터리에 정적 파일)
- 별도 빌드 도구 불필요 — 스킬이 직접 생성

### 3.8 doc-validate: 검증 방향 (docs → code)

docs를 기준으로 코드베이스를 검증한다:

- CLAUDE.md에 명시된 규칙이 실제 코드 구조와 일치하는지
- docs/architecture/에 기술된 모듈/레이어 구조가 실제 코드에 존재하는지
- docs/policies/에 기술된 비즈니스 규칙이 코드에 반영되어 있는지
- 문서에 언급된 패키지 경로, 설정 파일 등이 유효한지

---

## 4. Feature 1: ai-debugger

### 4.1 목적

API 요청에 대해 실제 데이터와 코드베이스를 기반으로 이슈를 디버깅하고 해결하는 에이전트.
운영 환경 수준의 full IO 캡처를 통해 실질적 이슈 분석이 가능해야 한다.

### 4.2 스킬 구성

| 스킬 | 트리거 | 역할 |
|------|--------|------|
| `curl-gen` | `/curl-gen` 또는 debug-agent에서 호출 | 자연어 + API 명세 기반 curl 명령 생성. 요청 파라미터 수집 |
| `io-interceptor` | `/io-setup` 또는 debug-agent에서 호출 | 대상 서비스에 IO 인터셉터 코드 주입. 서비스 코드 컨벤션 준수 |
| `log-query` | debug-agent에서 호출 | 적재된 IO 로그를 Redis/ELK/NoSQL에서 선택적 조회 |
| `code-explore` | debug-agent에서 호출 | 코드베이스 + docs/ 문서를 함께 참조하여 관련 로직 탐색 |
| `data-analyze` | debug-agent에서 호출 | 수집된 IO 데이터 기반 패턴 분석 |
| `answer-gen` | debug-agent에서 호출 | 분석 결과를 종합하여 사용자 답변 생성 |

### 4.3 오케스트레이터: debug-agent

```
[사용자 질의] → debug-agent
    │
    ├── 1. 질의 파싱 — 대상 API, 증상, 컨텍스트 파악
    │
    ├── 2. IO 인터셉터 확인
    │   ├── 이미 주입됨 → 스킵
    │   └── 미설치 → io-interceptor 스킬로 주입 제안
    │
    ├── 3. curl-gen — 문제 재현용 요청 생성 + 실행
    │
    ├── 4. code-explore — 코드베이스 + docs/ 문서를 함께 참조하여 관련 로직 탐색
    │   ├── docs/policies, docs/architecture 등에서 비즈니스 규칙/설계 의도 확인
    │   ├── 원인 발견 → 6으로
    │   └── 코드만으로 불충분 → 5로
    │
    ├── 5. log-query + data-analyze — 필요한 구간의 IO 로그만 선택적 조회 + 분석
    │
    └── 6. answer-gen — 종합 답변 생성
        ├── 원인 분석
        ├── 관련 코드 위치
        ├── IO 로그 근거 (조회한 경우)
        └── 해결 방안
```

**핵심 원칙: 코드 분석이 우선, IO 로그는 보조 근거로 필요할 때만 조회. 컨텍스트 비용 최소화.**

### 4.4 io-interceptor: 활성화 전략

#### 성능 영향 제거: 온디맨드 활성화

평상시에는 인터셉터가 동작하지 않고, 디버깅이 필요할 때만 명시적으로 활성화:

- **Spring**: `@Profile("debug-trace")` 기반. 프로필 미활성 시 빈 자체가 등록되지 않아 오버헤드 완전 0
- **비Spring (Python, TS)**: 헤더 기반 (`X-Debug-Trace: true`). 요청 단위 선택적 캡처

#### 언어별 주입 전략

| 캡처 대상 | Kotlin/Spring | Python/FastAPI | TypeScript/Express |
|-----------|---------------|----------------|-------------------|
| HTTP req/res | Servlet Filter | Middleware | Middleware |
| DB 쿼리 | AOP `@Around` (Hibernate) | SQLAlchemy Event | Prisma Middleware |
| 외부 API | WebClient `ExchangeFilterFunction` | httpx Hook | Axios Interceptor |
| Kafka | ProducerInterceptor / ConsumerInterceptor | aiokafka Hook | kafkajs Hook |
| Redis | Lettuce `CommandListener` | redis-py Monitor | ioredis Monitor |

> P6Spy 사용 금지 — 논블러킹 환경에서 올바르게 동작하지 않는 버그 존재

#### 코루틴/논블러킹 구간: 완료 시점 스냅샷

suspend/async IO는 **결과가 물리화(materialize)되는 시점에 스냅샷**을 1회 기록:

| 구간 | 스냅샷 시점 | 방식 |
|------|------------|------|
| WebClient | 응답 수신 완료 | `ExchangeFilterFunction` response 콜백 |
| DB (JPA) | 쿼리 완료 (blocking) | AOP `proceed()` 반환 시점 |
| Kafka produce | send ACK 수신 | `ProducerInterceptor.onAcknowledgement` |
| Redis | 커맨드 응답 | `CommandListener.commandCompleted` |

#### 순서 보장: sequence 채번 + 완료 시점 기록

```
호출 진입 시: sequence 채번 (AtomicLong, 코드 순서 보존) + invokedAt 기록
완료 시점: request + response 데이터를 포함한 전체 스냅샷을 1회 저장
```

- `sequence`: 호출 시점에 채번하여 코드 실행 순서 보존
- 데이터 쓰기: 완료 시점에 1회만 발생 → suspend 중간에 불필요한 쓰기 없음
- `invokedAt` ~ `completedAt` 간격으로 병목 구간 식별 가능

### 4.5 IO 로그 표준 스키마

```json
{
  "schemaVersion": 1,
  "traceId": "abc-123",
  "sequence": 1,
  "invokedAt": "2026-03-16T10:00:00.100Z",
  "completedAt": "2026-03-16T10:00:00.250Z",
  "service": "order",
  "type": "HTTP|DB|EXTERNAL_API|KAFKA|REDIS",
  "direction": "INBOUND|OUTBOUND",
  "request": {},
  "response": {},
  "duration": 150,
  "error": null
}
```

### 4.6 로그 저장/조회

#### Redis 저장 구조: Hash Bucket per IO Object

각 IO 이벤트를 Redis Hash로 저장. **해시 키 자체에 코드 위치/메서드명/IO 객체명을 포함**하여, 값을 조회하지 않고도 키 스캔만으로 분석 필요 여부를 판단할 수 있게 한다.

```
# Hash Key 네이밍 규칙
io:{traceId}:{type}:{method}:{line}

# 예시
io:abc-123:HTTP:OrderController.createOrder:45
io:abc-123:DB:OrderRepository.save:128
io:abc-123:EXTERNAL_API:PaymentClient.charge:67
io:abc-123:KAFKA:OrderEventProducer.send:89
io:abc-123:REDIS:CartCacheAdapter.get:34
```

```
# Hash 필드 구조 (HGETALL로 필요 시에만 상세 조회)
HSET io:abc-123:DB:OrderRepository.save:128
  timestamp    "2026-03-16T10:00:00.150Z"
  service      "order"
  direction    "OUTBOUND"
  request      '{"sql":"INSERT INTO orders...","params":[...]}'
  response     '{"rowsAffected":1}'
  duration     "12"
  error        ""
```

#### traceId별 키 인덱스

`SCAN`의 O(N) 비용을 회피하기 위해, traceId별 Set으로 해시 키를 인덱싱:

```
# traceId별 키 인덱스 (Set)
SADD io:index:abc-123
  "io:abc-123:HTTP:OrderController.createOrder:45"
  "io:abc-123:DB:OrderRepository.save:128"
  "io:abc-123:EXTERNAL_API:PaymentClient.charge:67"
```

#### 분석 시 2단계 조회 전략

1. **키 조회 (저비용)**: `SMEMBERS io:index:{traceId}` → 해시 키 목록에서 메서드명, 코드 라인, IO 타입으로 관련 구간 필터링
2. **값 조회 (필요 시만)**: 필터링된 키에 대해서만 `HGETALL` → 상세 데이터 획득

이를 통해 컨텍스트 비용을 최소화하면서 필요한 IO 로그만 정밀 조회.

#### 코드 위치 캡처 전략

해시 키에 포함되는 메서드명/라인 정보의 언어별 캡처 방식:
- **Kotlin/JVM**: 인터셉터 등록 지점의 클래스명+메서드명 활용 (런타임 스택트레이스 대신 정적 매핑)
- **Python**: `__qualname__` + decorator 기반 정적 매핑
- **TypeScript**: 미들웨어 등록 시 라우트 핸들러명 활용

성능 오버헤드를 피하기 위해 런타임 스택 인스펙션이 아닌, **인터셉터 등록 시점의 정적 메타데이터**를 사용.

#### TTL 및 용량 관리

- 기본 TTL: 24시간 (환경별 설정 가능)
- Hash 키와 인덱스 Set에 동일 TTL 적용
- 설정 파일에서 TTL, 최대 traceId 수 등 오버라이드 가능

#### 저장소 인터페이스

```
LogStore {
  store(event: IOEvent): void          # IO 이벤트 저장
  listKeys(traceId: string): string[]  # traceId의 키 목록 (키 스캔)
  getDetail(key: string): IOEvent      # 특정 키의 상세 데이터
}
```

- **Redis 구현체** (기본): Hash + Set 인덱스 + TTL
- **ELK 구현체**: Index per service, traceId 필드 필터로 키 스캔 대체
- 대상 서비스 설정에 따라 저장소 자동 감지

### 4.7 curl-gen: API 요청 생성

- 사용자의 자연어 설명을 파싱하여 대상 API 식별
- 프로젝트의 API 명세 (Controller/Router 코드, OpenAPI spec 등)를 참조
- 필요한 요청 파라미터를 사용자에게 질문하여 수집
- 인증 정보는 환경변수 또는 사용자 입력으로 수집 (로그에는 마스킹 처리)
- 완성된 curl 명령을 생성하고 사용자 확인 후 실행

---

## 5. Shared Resources

```
shared/
├── lib/
│   ├── project-analyzer/            # 프로젝트 언어/프레임워크/모듈 구조 감지
│   └── template-engine/             # 템플릿 렌더링 공통 로직
└── templates/
    └── common/                      # 양쪽 플러그인에서 사용하는 공통 템플릿
```

---

## 6. Design Decisions

| 결정 | 근거 |
|------|------|
| 디렉터리 기반 플러그인 분리 | 관심사 분리 + 선택적 설치 가능 + 단일 레포 관리 편의 |
| IO 로그는 코드 분석 보조로만 조회 | 컨텍스트 비용 최소화 |
| 표준 IO 스키마 정의 | 언어/프레임워크 무관하게 동일한 분석 파이프라인 적용 |
| doc-site는 외부 의존성 없이 생성 | 설치 부담 제거, 어디서든 바로 열 수 있는 HTML |
| doc-validate는 scaffold 내 호출 + 단독 호출 모두 지원 | 초기 생성 시 + 변경 시 반복 검증 가능 |

---

## 7. Out of Scope (v1)

- CI/CD 연동 (doc-validate를 PR hook으로 실행 등)
- 실시간 로그 스트리밍/모니터링
- 멀티 서비스 간 분산 트레이싱 통합 (traceId 전파는 지원하되, 시각화는 미포함)
- 프로덕션 환경 직접 접속 (로컬/스테이징 환경 기준)

## 8. TODO (향후 검토)

- **디버그 모드 HTML 뷰어**: 스냅샷된 IO 데이터를 한 화면에서 열람 가능한 HTML 페이지 제공. traceId 기준으로 sequence 순서대로 IO 흐름을 시각화하고, 각 스냅샷의 req/res 상세를 펼쳐볼 수 있는 형태
