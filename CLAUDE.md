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
| hns | 19 | 하네스 엔지니어링 |
| ai-debugger | 2 | API 디버깅 |
| private-repo | 1 | Private repo 분리 |
| content-analyzer | 1 | 콘텐츠 분석 |
