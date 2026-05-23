# AI Common Plugins

Claude Code 플러그인 모노레포.

## Build

플러그인은 마크다운 기반이라 빌드 없음. 변경 후 commit + push로 배포.

## Plugin Development Rules

플러그인 개발/수정 시 반드시 [docs/plugin-development-guide.md](docs/plugin-development-guide.md)를 따른다.

### 핵심 규칙 요약

1. **commands/ = 사용자 호출, skills/ = 백그라운드** — 혼동 금지
2. **command frontmatter에 `name` 필드 금지** — 있으면 plugin prefix가 안 붙음
3. **marketplace.json 등록 필수** — 없으면 `claude plugins install` 실패
4. **version bump 필수** — 안 올리면 캐시 갱신 안 됨
5. **description 250자 이내** — 초과 시 자동완성에서 잘림

### Plugin 구조

```
plugins/{name}/
├── .claude-plugin/plugin.json    # 매니페스트 (commands[] 배열 포함)
├── commands/{cmd}.md             # 사용자 호출 커맨드 (name 없이 description만)
├── skills/{skill}/SKILL.md       # 백그라운드 스킬 (user-invocable: false)
├── agents/{agent}.md             # 서브에이전트
├── references/                   # 참조 프로토콜
└── templates/                    # 생성 템플릿
```

### 테스트

```bash
claude --plugin-dir ./plugins/{name}     # 로컬 테스트
/reload-plugins                           # 세션 내 리로드
```

## Active Plugins

| Plugin | Commands | Description |
|--------|----------|-------------|
| hns | 13 | 하네스 엔지니어링 (SDD 파이프라인, 6-차원 리뷰, 유비쿼터스 사전 `/hns:glossary`, ADR) |
| ai-debugger | 2 | API 디버깅 |
| private-repo | 1 | Private repo 분리 |
| content-analyzer | 1 | 콘텐츠 분석 |
| study | 3 | 스터디 파이프라인 (init → bs → exec) |
| ideabank | 3 | 아이디어 → PRD → 구현 파이프라인 (init → bs → impl) |
| portfolio | 1 | git commit history 기반 개발자 포트폴리오 생성·incremental 보완 (`/portfolio:build`) |
| claude-md-analyzer | 3 | 레이어별 CLAUDE.md/메모리/settings 합성 분석 (`/claude-md:analyze` 활성/덮어쓴 룰 가시화, `/claude-md:diff` 레포 간 비교, `/claude-md:simulate` 가상 프롬프트 dry-run) |
| skill-quality-eval | 4 + 1 skill | 스킬 품질 동적 평가 + closed-loop refinement (fork + `--json-schema` + 스냅샷 + N-repeat + semantic judge + suggester). `/skill-eval:baseline` 사람 1회 컨펌 → `/skill-eval:run` 자동 N회 측정 + accuracy/stability + 회귀 시 suggester 가 SKILL.md 수정 제안 → `/skill-eval:compare` / `/skill-eval:promote`. 라우터 스킬 `skill-quality-eval:skill-quality-eval` 자연어 트리거 ("스킬 평가", "정답셋 만들어", "회귀 측정"). v0.2.1 (2026-05-23), dogfooding = `hns:glossary` |
