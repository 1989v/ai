# Claude Code 고급 기능 레퍼런스

> Skills, Sub-Agent, Hooks, 병렬 실행, 자동화 등 Claude Code의 확장 메커니즘을 주제별로 정리한 노트.

---

## 목차

1. [핵심 개념 관계도](#1-핵심-개념-관계도)
2. [Skills (스킬)](#2-skills-스킬)
3. [Sub-Agent (서브에이전트)](#3-sub-agent-서브에이전트)
4. [Hooks (훅)](#4-hooks-훅)
5. [병렬 실행](#5-병렬-실행)
6. [자동화 워크플로우](#6-자동화-워크플로우)
7. [CLAUDE.md 효과적 작성법](#7-claudemd-효과적-작성법)
8. [Agent SDK](#8-agent-sdk)
9. [실전 통합 패턴](#9-실전-통합-패턴)

---

## 1. 핵심 개념 관계도

Claude Code의 확장 메커니즘은 4가지로 나뉜다. 각각의 역할이 다르므로 혼동하지 말 것.

| 개념 | 역할 | 실행 주체 | 트리거 |
|------|------|----------|--------|
| **Skill** | 지식/절차/가이드 문서 | Claude가 읽음 | 자동 감지 (description 기반) |
| **Sub-Agent** | 독립 컨텍스트의 전문 AI | Claude가 위임 | 자동 위임 또는 명시적 호출 |
| **Hook** | 이벤트 기반 자동 실행 셸 명령 | OS가 실행 | 라이프사이클 이벤트 (PreToolUse 등) |
| **Command** | 수동 트리거 프롬프트 | 사용자가 호출 | `/command-name` 입력 |

### 행동 주체 정리

```
행동 주체는 Claude와 Sub-Agent뿐이다.

- Claude     → Skills 읽기 ✅ | Scripts 실행 ✅ | Sub-Agent 호출 ✅
- Sub-Agent  → Skills 읽기 ✅ | Scripts 실행 ✅ | Sub-Agent 호출 ❌
- Hook       → Skills 읽기 ❌ | Scripts 실행 ✅ (자동) | Sub-Agent 호출 ❌
```

---

## 2. Skills (스킬)

### 개념

Skill = Claude에게 제공되는 **지식/절차 가이드 문서**. 레시피북처럼 "참고만" 되는 자료다. 실행 주체가 아니라 **읽히기만** 한다.

### 파일 구조

```
.claude/skills/
└── my-skill/
    ├── SKILL.md          # 메인 정의 (필수)
    ├── PATTERNS.md       # 참조 자료 (선택)
    └── scripts/          # 헬퍼 스크립트 (선택)
        └── validate.sh
```

### SKILL.md 작성법

```yaml
---
name: api-conventions
description: "API 엔드포인트 구현 시 팀 컨벤션 적용. REST API 관련 작업에 자동 활성화"
---

## API 응답 형식

모든 API 응답은 다음 구조를 따른다:
- 성공: `{ "data": ..., "meta": { "page": 1 } }`
- 실패: `{ "error": { "code": "NOT_FOUND", "message": "..." } }`

## 네이밍 규칙

- URL: kebab-case (`/user-profiles`)
- 필드: camelCase (`userName`)
- 상수: UPPER_SNAKE_CASE (`MAX_RETRY_COUNT`)
```

### Skill vs Command 선택 기준

| 질문 | Skill | Command |
|------|-------|---------|
| 자동으로 활성화? | O | X (수동 `/` 입력) |
| 항상 적용되어야 하는 규칙? | O | X |
| 특정 시점에만 필요? | X | O |
| 워크플로우 시작점? | X | O |

### 핵심 포인트

- `description`이 자동 감지의 핵심이다. 명확하고 구체적으로 작성할 것
- Skill은 **컨텍스트에 주입**되므로 간결하게 유지 (토큰 절약)
- 여러 Skill을 조합하여 복합 워크플로우 구성 가능

---

## 3. Sub-Agent (서브에이전트)

### 개념

메인 대화와 **별도의 컨텍스트 윈도우**에서 실행되는 전문 AI. 핵심 이점은 "컨텍스트 오염 방지"다.

### 파일 구조 및 위치

```
.claude/agents/my-agent.md       # 프로젝트 범위 (우선순위 2)
~/.claude/agents/my-agent.md     # 사용자 범위 - 모든 프로젝트 (우선순위 3)
플러그인의 agents/ 디렉토리          # 플러그인 범위 (우선순위 4)
```

### 기본 작성법

```yaml
---
name: code-reviewer
description: "코드 리뷰 전문가. 코드 변경 후 즉시 사용. 품질, 보안, 유지보수성 검토"
tools: Read, Grep, Glob, Bash     # 읽기 전용으로 제한
model: sonnet                      # 모델 선택 (sonnet/opus/haiku/inherit)
permissionMode: default            # 권한 모드
---

당신은 시니어 코드 리뷰어입니다.

리뷰 체크리스트:
- Critical: 보안 취약점, 데이터 유출 위험
- Warning: 성능 이슈, 코드 중복
- Suggestion: 가독성 개선, 네이밍
```

### 내장 Sub-Agent 3종

| 이름 | 모델 | 도구 | 용도 |
|------|------|------|------|
| **Explore** | Haiku (빠름) | 읽기 전용 | 코드베이스 검색/탐색 |
| **Plan** | 상속 | 읽기 전용 | 계획 수립을 위한 연구 |
| **General-purpose** | 상속 | 모든 도구 | 복합 다단계 작업 |

### 모델 선택 가이드

```
haiku   → 간단한 검색, 파일 탐색 (빠르고 저렴)
sonnet  → 코드 분석, 리뷰, 중간 복잡도 작업
opus    → 아키텍처 설계, 복잡한 추론
inherit → 메인 대화와 동일 모델
```

### 도구 제한 패턴

```yaml
# 읽기 전용 (리뷰, 탐색용)
tools: Read, Grep, Glob, Bash

# 편집 가능 (구현용)
tools: Read, Edit, Write, Bash, Grep, Glob

# 특정 도구 제외
disallowedTools: Write, Edit

# Sub-Agent 생성 제한
tools: Agent(worker, researcher), Read, Bash
```

### 호출 방법 3가지

```bash
# 1. 자연어 (Claude가 판단)
"code-reviewer 서브에이전트로 인증 모듈 리뷰해줘"

# 2. @-mention (강제 호출)
@"code-reviewer (agent)" 인증 변경사항 확인해줘

# 3. 세션 전체를 해당 에이전트로 실행
claude --agent code-reviewer
```

### 지속적 메모리 (Persistent Memory)

```yaml
---
name: code-reviewer
description: 코드 리뷰 전문가
memory: project      # user / project / local 중 선택
---
```

| 범위 | 저장 위치 | 용도 |
|------|----------|------|
| `user` | `~/.claude/agent-memory/<name>/` | 모든 프로젝트 공통 학습 |
| `project` | `.claude/agent-memory/<name>/` | 프로젝트 특화 (git 공유 가능) |
| `local` | `.claude/agent-memory-local/<name>/` | 프로젝트 특화 (git 제외) |

---

## 4. Hooks (훅)

### 개념

특정 이벤트 발생 시 **Claude의 판단 없이 무조건 실행**되는 셸 명령. 린팅, 포맷팅, 보안 검사처럼 매번 반드시 실행되어야 하는 작업에 사용한다.

### 이벤트 종류

| 이벤트 | 트리거 시점 | 대표 활용 |
|--------|-----------|----------|
| `PreToolUse` | 도구 실행 **전** | 위험 명령 차단, 파일 백업 |
| `PostToolUse` | 도구 실행 **후** | 자동 포맷팅, 린트 실행 |
| `UserPromptSubmit` | 사용자 입력 시 | 입력 검증 |
| `Notification` | 알림 발생 시 | Slack/이메일 알림 |
| `Stop` | 에이전트 종료 시 | 최종 검증, 리포트 생성 |
| `SubagentStart` | 서브에이전트 시작 시 | DB 연결 설정 |
| `SubagentStop` | 서브에이전트 종료 시 | 정리 작업 |
| `SessionStart` | 세션 시작 시 | 초기화 |

### 설정 위치

`.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$CLAUDE_FILE_PATH\""
          }
        ]
      }
    ]
  }
}
```

### 실전 레시피

#### 1) 파일 편집 후 자동 포맷팅 + 린트

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$CLAUDE_FILE_PATH\" && npx eslint --fix \"$CLAUDE_FILE_PATH\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

#### 2) 위험한 명령어 차단 (보안 가드레일)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_COMMAND\" | grep -qE 'rm -rf|DROP TABLE|DELETE FROM'; then echo 'BLOCKED' && exit 1; fi"
          }
        ]
      }
    ]
  }
}
```

#### 3) 파일 편집 전 자동 백업

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "cp \"$CLAUDE_FILE_PATH\" \"$CLAUDE_FILE_PATH.bak\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

#### 4) 변경 로깅

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$(date): $CLAUDE_FILE_PATH modified\" >> .claude/change.log"
          }
        ]
      }
    ]
  }
}
```

#### 5) 관련 테스트 자동 실행

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_FILE_PATH\" == *.ts ]]; then npx jest --findRelatedTests \"$CLAUDE_FILE_PATH\" --passWithNoTests; fi"
          }
        ]
      }
    ]
  }
}
```

### Hook 종료 코드

| 코드 | 의미 |
|------|------|
| `0` | 성공, 계속 진행 |
| `1` | 실패, 하지만 계속 진행 |
| `2` | **차단** — 해당 도구 실행을 막음 (PreToolUse에서 핵심) |

---

## 5. 병렬 실행

### Sub-Agent 병렬 실행

독립적인 작업들을 여러 Sub-Agent에 동시 분배:

```
> 인증, 데이터베이스, API 모듈을 병렬로 분석해줘

작동:
  Sub-Agent 1 → 인증 모듈 분석
  Sub-Agent 2 → 데이터베이스 레이어 분석
  Sub-Agent 3 → API 엔드포인트 분석
  → Claude가 결과 종합
```

### Background 실행

```bash
# 백그라운드로 장시간 작업
claude --background "테스트 커버리지를 80% 이상으로 올려줘"

# 상태 확인
claude --list-backgrounds

# 결과 확인
claude --resume <session-id>
```

### Foreground vs Background

| 항목 | Foreground | Background |
|------|-----------|------------|
| 메인 대화 차단 | O | X |
| 권한 프롬프트 전달 | O | X (사전 승인 필요) |
| 사용자 질의 가능 | O | X |
| 전환 | Ctrl+B로 백그라운드 전환 | - |

### Git Worktree 활용

격리된 환경에서 병렬 작업:

```yaml
---
name: feature-builder
description: 기능 구현 전문가
isolation: worktree     # 임시 git worktree에서 실행
---
```

```bash
claude "워크트리를 만들어서 feature-auth 브랜치에서 인증 모듈을 리팩터링해줘"
```

---

## 6. 자동화 워크플로우

### CI/CD 통합 (GitHub Actions)

```yaml
name: Claude Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Claude Code 리뷰
        run: |
          npx @anthropic-ai/claude-code -p \
            "이 PR의 변경사항을 리뷰하고 코멘트를 남겨줘" \
            --yes --output-format json
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### MCP 서버 통합

Sub-Agent에 MCP 서버를 범위 지정하여 외부 도구 연결:

```yaml
---
name: browser-tester
description: Playwright로 실제 브라우저 테스트
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  - github     # 이미 설정된 서버 참조
---
```

### 자동화 계층 구조

```
1. CLAUDE.md      → 프로젝트 기초 지식 (항상 로드)
2. Skills         → 도메인 전문성 (자동 감지)
3. Hooks          → 강제 자동화 (이벤트 기반)
4. Commands       → 명시적 워크플로우 (수동 트리거)
5. Sub-Agents     → 병렬/격리 작업 (위임)
6. MCP Servers    → 외부 도구 연결 (어댑터)
```

---

## 7. CLAUDE.md 효과적 작성법

### 계층 구조

| 위치 | 범위 | 용도 |
|------|------|------|
| `~/.claude/CLAUDE.md` | 전역 | 모든 프로젝트 공통 규칙 |
| `./CLAUDE.md` | 프로젝트 | 아키텍처, 기술 스택 |
| `./src/CLAUDE.md` | 디렉토리별 | 모듈 특화 규칙 |
| `.claude/CLAUDE.md` | 개인 | 개인 설정 (git 제외) |

### 작성 원칙

1. **간결하게** — 광범위한 문서가 아니라 빠른 참고자료
2. **명확한 규칙** — "~하지 말 것" 형태의 금지 패턴 포함
3. **기술 스택 명시** — 프레임워크, 언어, 주요 라이브러리
4. **디렉토리 구조** — 프로젝트 구조 한눈에 파악

### 예시

```markdown
# 프로젝트 개요
Kotlin + Spring Boot 기반 MSA 서비스

# 기술 스택
- Language: Kotlin 1.9
- Framework: Spring Boot 3.2
- DB: PostgreSQL + Redis
- Build: Gradle (Kotlin DSL)

# 코딩 컨벤션
- 함수명: camelCase
- 패키지: domain, application, infrastructure 3계층
- DTO 네이밍: XxxRequest, XxxResponse

# 금지 패턴
- @Autowired 필드 주입 금지 (생성자 주입만)
- var 사용 최소화 (val 우선)
- 하드코딩 문자열 금지 (상수 또는 enum)

# 실행 명령어
- 빌드: `./gradlew build`
- 테스트: `./gradlew test`
- 로컬 실행: `./gradlew bootRun`
```

---

## 8. Agent SDK

프로그래밍 방식으로 Claude Code를 사용하여 커스텀 AI 에이전트를 구축하는 개발 키트.

### 기본 사용법

```typescript
import { AgentSDK } from '@anthropic-ai/claude-code-sdk'

const agent = new AgentSDK({
  model: 'claude-sonnet-4-20250514',
  permissions: {
    fileRead: true,
    fileWrite: true,
    commandExec: ['npm test', 'npm run lint'],
  },
})

const session = await agent.createSession()
const result = await session.send('src/ 디렉토리의 테스트 커버리지를 분석해줘')
```

### 이벤트 처리

```typescript
session.on('toolUse', (event) => {
  console.log(`도구 사용: ${event.tool} - ${event.description}`)
})

session.on('fileChange', (event) => {
  console.log(`파일 변경: ${event.path} - ${event.type}`)
})

session.on('error', (event) => {
  console.error(`에러: ${event.message}`)
})
```

### 권한 모델

```typescript
const agent = new AgentSDK({
  permissions: {
    fileRead: true,
    fileWrite: true,
    fileGlob: ['src/**/*.ts', 'tests/**/*.ts'],  // 허용 패턴
    fileExclude: ['*.env', 'secrets/**'],          // 제외 패턴
    commandExec: ['npm test', 'npm run lint'],     // 허용 명령어
    networkAccess: false,
    mcpServers: ['filesystem', 'database'],
  },
})
```

### 활용 사례

- **코드 리뷰 봇**: PR 자동 리뷰
- **자동 문서화**: JSDoc/TSDoc 자동 생성
- **마이그레이션 에이전트**: DB 스키마 변경 자동화
- **보안 스캐너**: 취약점 자동 검사

---

## 9. 실전 통합 패턴

### 패턴 1: 탐색 → 계획 → 구현 → 검증

```
1단계 [Explore Sub-Agent] → 코드베이스 구조 파악
2단계 [Plan Mode]          → 구현 계획 수립
3단계 [General Sub-Agent]  → 코드 구현
4단계 [Hook: PostToolUse]  → 자동 린트/포맷
5단계 [Code-Reviewer]      → 자동 코드 리뷰
```

### 패턴 2: 대규모 리팩터링 병렬 처리

```
메인 Claude
├── Sub-Agent 1: 컴포넌트 A 리팩터링
├── Sub-Agent 2: 컴포넌트 B 리팩터링
├── Sub-Agent 3: 컴포넌트 C 리팩터링
└── 결과 종합 및 통합 테스트
```

### 패턴 3: Sub-Agent 체인

```
Code-Reviewer Sub-Agent
  → 성능 이슈 발견
    → Optimizer Sub-Agent로 수정
      → Test-Runner Sub-Agent로 검증
```

### 패턴 4: Hook + Skill 조합

```
[Hook: PostToolUse]  파일 수정 감지
  → 자동 포맷팅 실행
  → 자동 린트 실행
[Skill: test-patterns] Claude가 테스트 패턴 참조
  → 관련 테스트 자동 작성
```

### 언제 무엇을 쓸 것인가?

| 상황 | 추천 |
|------|------|
| 항상 적용되어야 하는 규칙 | CLAUDE.md 또는 Skill |
| 매번 반드시 실행되어야 하는 작업 | Hook |
| 특정 시점에 수동으로 실행 | Command |
| 대량 출력이 예상되는 작업 | Sub-Agent (컨텍스트 격리) |
| 병렬 처리가 가능한 독립 작업 | 복수 Sub-Agent |
| 외부 도구와 연결 | MCP Server |
| 프로그래밍 방식 자동화 | Agent SDK |

---

## 참고 자료

### 공식 문서
- [Sub-Agents](https://code.claude.com/docs/ko/sub-agents)
- [Skills](https://code.claude.com/docs/ko/skills)
- [Hooks](https://code.claude.com/docs/ko/hooks)
- [Plugins](https://code.claude.com/docs/ko/plugins)

### 블로그 / 아티클
- [Claude Code 완전 가이드 (youngju.dev)](https://www.youngju.dev/blog/culture/2026-03-22-claude-code-agentic-coding-guide-2025)
- [Understanding Claude Code Full Stack (alexop.dev)](https://alexop.dev/posts/understanding-claude-code-full-stack/)
- [Claude Code Customization Guide (alexop.dev)](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/)

### 영상
- [클로드코드 완벽 가이드 심화편 — 실밸개발자](https://www.youtube.com/watch?v=8H3NwQL-Aew)
- [클로드 활용법 — 김효율의 AI 개발단](https://youtu.be/vLbzl5u5iwM)
