# AI Common Plugins

다른 서비스에 공통으로 활용할 Claude Code 플러그인 모노레포.

## 플러그인 목록

| 플러그인 | Prefix | 설명 |
|---------|--------|------|
| **hns** | `/hns:` | AI 하네스 엔지니어링 — SDD 파이프라인, 5차원 리뷰, Lifecycle(GC/evolve/diet/audit), 문서 생성 |
| **ai-debugger** | `/ai-debugger:` | API 디버깅 에이전트 — IO 캡처, curl 생성, 로그 분석 |
| **private-repo** | `/private-repo:` | git submodule로 디렉토리별 public/private 가시성 제어 |
| **content-analyzer** | `/content-analyzer:` | URL 콘텐츠 분석 (YouTube, LinkedIn, web post, Git repo) |

---

## 설치 방법

### 방법 1: CLI로 설치 (권장)

```bash
# marketplace 등록 (최초 1회)
claude marketplace add https://github.com/1989v/ai.git --name ai-common

# 플러그인 설치
claude plugins install hns@ai-common
claude plugins install ai-debugger@ai-common
claude plugins install private-repo@ai-common
claude plugins install content-analyzer@ai-common

# 세션 내 리로드
/reload-plugins
```

### 방법 2: settings.json 직접 편집

대상 프로젝트의 `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "hns@ai-common": true,
    "ai-debugger@ai-common": true,
    "private-repo@ai-common": true,
    "content-analyzer@ai-common": true
  }
}
```

---

## hns (Harness Scaffold)

AI 하네스 엔지니어링 완전체 플러그인. 19개 커맨드.

```
/hns:init              하네스 스캐폴딩 (auto-scan → doc-gen → hooks → routing)
/hns:new-feature       신규 기능 파이프라인 (shape → write → review → tasks)
/hns:shape-spec        요구사항 수집 + 스펙 폴더 초기화
/hns:write-spec        spec.md 작성
/hns:spec-review       5차원 스펙 리뷰 (arch/domain/impl/test/usecase)
/hns:create-tasks      spec → task group 분해
/hns:implement-tasks   task group 실행 (Ralph Loop)
/hns:orchestrate-tasks 순차/병렬 오케스트레이션
/hns:interview-capture 구현 전 게이트 인터뷰
/hns:drift-check       구현-스펙 불일치 감지
/hns:verify            표준 → 린트 → 빌드 → 테스트
/hns:verify-crosscheck 6레이어 교차 일관성 검증
/hns:doc-gen           CLAUDE.md + docs/ 생성
/hns:doc-validate      docs ↔ 코드 일치 검증
/hns:doc-html          docs/ → HTML 사이트 생성
/hns:harness-gc        가비지 컬렉션 (dead code, doc drift, stale rules)
/hns:harness-evolve    실패 패턴 → 규칙 인코딩
/hns:harness-diet      불필요한 규칙 제거 (Bitter Lesson)
/hns:harness-audit     외부 벤치마크 비교
```

상세: [plugins/hns/README.md](plugins/hns/README.md)

---

## 플러그인 개발 가이드

새 플러그인/커맨드/스킬을 만들 때: [docs/plugin-development-guide.md](docs/plugin-development-guide.md)

핵심 규칙:
- `commands/*.md`는 frontmatter에 **`name` 필드를 넣지 않는다** (prefix가 안 붙음)
- 새 플러그인은 `.claude-plugin/marketplace.json`에 반드시 등록
- version을 올리지 않으면 기존 사용자 캐시가 갱신 안 됨

---

## 레포 구조

```
ai/
├── .claude-plugin/marketplace.json    # marketplace 인덱스
├── plugins/
│   ├── hns/                           # 하네스 엔지니어링 (19 commands, 12 skills, 10 agents)
│   ├── ai-debugger/                   # API 디버깅 (2 commands, 6 skills, 1 agent)
│   ├── private-repo/                  # Private repo 분리 (1 command, 1 skill)
│   └── content-analyzer/              # 콘텐츠 분석 (1 command, 3 skills, 1 agent)
├── docs/
│   ├── plugin-development-guide.md    # 플러그인 개발 가이드
│   ├── specs/                         # 설계 스펙
│   └── study/                         # 학습 자료
└── README.md
```
