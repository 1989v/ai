# {{project_name}} AI Working Agreement

## 1. Project Intent

<!-- Describe what this service/platform builds and its key quality attributes. -->

{{project_intent}}

The architecture must support:
- Horizontal scalability
- High availability
- Service isolation
- Kubernetes-ready deployment


## 2. Architecture Principles

This project strictly follows Clean Architecture.

- Dependency direction must always point inward: `domain ← application ← infrastructure / presentation`.
- Domain layer must not depend on any framework (no Spring, no JPA annotations).
- Application layer depends only on port interfaces, never on infrastructure implementations.
- Infrastructure implements outbound ports defined in the application layer.
- Direct dependency from Application to Infrastructure is prohibited.
- Service-to-service database sharing is prohibited.

Reference: /docs/architecture/overview.md


## 3. Architectural Constraints

- Each service owns its database; cross-service DB access is forbidden.
- Internal DB access is blocking (JPA/Spring Data).
- External API calls use WebClient (non-blocking).
- Coroutine usage is limited to external IO operations.
- Event-driven communication uses Kafka.
- WebFlux full adoption is prohibited.
- Redis must be designed with cluster scalability in mind.


## 4. Architecture Governance

- Any architectural or structural change requires an ADR under `/docs/adr/`.
- Implementation code must not be generated before ADR approval.
- Existing ADRs must be reviewed before proposing new decisions.
- If a conflict with existing ADRs is detected, pause and request clarification.
- ADR numbering must be sequential (ADR-0001, ADR-0002, …).
- Superseded ADRs must explicitly reference replacement ADRs.


## 5. AI Execution Rules

Before generating implementation:

- Validate alignment with Architecture Principles (section 2).
- Validate consistency with existing ADRs.
- Validate consistency with relevant docs under `/docs/`.
- If ambiguity or conflict exists, pause and request clarification.
- Avoid generating code before module/package structure is finalized.


## 6. Module & Build Rules

<!-- Adjust module list to match this project's actual services. -->

- Common/shared modules produce `jar` only (no `bootJar`).
- Service modules depend on common via `implementation(project(":common"))`.
- All versions are centrally managed in `gradle/libs.versions.toml` (Version Catalog).
- Java {{java_version}} LTS toolchain applied uniformly: `JavaLanguageVersion.of({{java_version}})`.
- QueryDSL Q-classes are generated under `build/generated/source/kapt/` (git-ignored).
- Build commands: `./gradlew :{module}:build` (single module), `./gradlew build` (all).

### Module Naming Convention (Nested Submodule)

Each service is split into `{service}:domain` / `{service}:app` nested Gradle submodules.

| Gradle path | Filesystem path | Role |
|-------------|----------------|------|
| `:{service}:domain` | `{service}/domain/` | Pure domain (no Spring/JPA) |
| `:{service}:app` | `{service}/app/` | Spring Boot app (Application + Infrastructure + Presentation) |

<!-- Add service-specific rows as needed. -->

- **domain module rule**: adding Spring/JPA annotations causes a compile error (no dependency).
- **app module**: depends on domain via `implementation(project(":{service}:domain"))`.
- **bootJar naming**: `tasks.bootJar { archiveBaseName.set("{service}") }`.


## 7. Package Naming Convention

Base package: `com.{{company}}.{{service}}`

Clean Architecture layer packages:

```
com.{{company}}.{{service}}/
├── domain/                          ← {service}:domain Gradle submodule
│   └── {entity}/
│       ├── model/        # Aggregate, Entity, Value Object
│       ├── policy/       # Domain Policy, Specification
│       ├── event/        # Domain Event
│       └── exception/    # Domain Exception
├── application/                     ← {service}:app Gradle submodule
│   └── {entity}/
│       ├── usecase/      # UseCase interface (Inbound Port)
│       ├── service/      # UseCase implementation
│       ├── port/         # Outbound Port interface
│       └── dto/          # Command, Result, Query
├── infrastructure/                  ← {service}:app Gradle submodule
│   ├── persistence/
│   │   └── {entity}/
│   │       ├── entity/     # JPA Entity
│   │       ├── repository/ # Spring Data Repository + QueryDSL
│   │       └── adapter/    # RepositoryPort implementation
│   ├── client/             # WebClient-based external API Adapter
│   ├── messaging/          # Kafka Producer/Consumer Adapter
│   └── config/             # Technical config (DataSource, Redis, Kafka, …)
└── presentation/                    ← {service}:app Gradle submodule
    └── {entity}/
        ├── controller/   # RestController
        └── dto/          # Request DTO, Response DTO
```

- Cross-domain direct references are forbidden (use API calls instead).
- `domain` packages must not use Spring/JPA annotations.
- Domain layer code must reside in the `{service}/domain/` Gradle submodule.


## 8. Test Rules

- Test framework: **Kotest BehaviorSpec** (BDD style)
- Test doubles: **MockK** (Mockito is forbidden)
- Domain tests: no mocks — pure unit tests only
- Application tests: outbound ports are mocked with MockK
- Test file location: `src/test/kotlin/{package}/...`
- Test file naming: implementation name + `Test` suffix (e.g. `ProductServiceTest.kt`)

### Kotest BehaviorSpec Example

```kotlin
class ProductServiceTest : BehaviorSpec({
    given("a valid product creation request") {
        `when`("a valid name and price are provided") {
            then("a product in ACTIVE status should be created") {
                val product = Product.create("Sample", Money(1000.toBigDecimal()), 10)
                product.status shouldBe ProductStatus.ACTIVE
            }
        }
    }
})
```


## 9. Kafka Topic Convention

Format: `{domain}.{entity}.{event}`

| Topic | Published by | Consumed by |
|-------|-------------|-------------|
| `{{domain}}.{{entity}}.created` | {{producer_service}} | {{consumer_service}} |
| `{{domain}}.{{entity}}.updated` | {{producer_service}} | {{consumer_service}} |

<!-- Add project-specific topics. -->

- Consumer Group ID format: `{service}-{purpose}` (e.g. `search-indexer`)
- DLQ strategy: document in an ADR before implementation.


## 10. API Response Format

All HTTP responses are wrapped with `ApiResponse<T>` (provided by the `common` module).

**Success response:**
```json
{
  "success": true,
  "data": { "..." },
  "error": null
}
```

**Error response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  }
}
```

- Controllers use `ApiResponse.success(data)` or `ApiResponse.error(errorCode)`.
- `GlobalExceptionHandler` handles final error translation (provided by `common` module).
- HTTP status codes must be semantically correct (200/201/400/401/403/404/500).


## 11. Docker & Local Dev Rules

- Start infrastructure only: `docker compose -f docker/docker-compose.infra.yml up -d`
- Start all services: `docker compose -f docker/docker-compose.yml up -d`
- Each service can run independently (requires only its own DB and a service registry).
- `.env` lives at `docker/.env` (git-ignored; `.env.example` must be kept up to date).
- Environment injection: `SPRING_PROFILES_ACTIVE=docker` activates Docker-specific config.
