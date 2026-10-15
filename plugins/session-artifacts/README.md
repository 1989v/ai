# session-artifacts

이 세션에서 발행한 claude.ai 아티팩트 링크를 프롬프트 바로 위에 띄우는 Claude Code mod 플러그인.

```
아티팩트 3 · 시장 지도 화면 샘플 (2분 전) https://claude.ai/artifact/…
            · 시장 골목 지도 샘플 (1시간 전) …
            외 2건 · 전체 /session-artifacts
```

## 동작

- `Artifact` 도구의 `publish` 결과에서 URL·제목을 읽어 최근 3건을 프롬프트 위 영역(`AbovePrompt`)에 보여 준다. 같은 URL 을 다시 발행하면 한 줄로 합치고 발행 횟수를 센다.
- `/session-artifacts` 는 이 세션의 전체 목록을 낸다.
- 세션 id 별로 플러그인 저장소에 남겨(최근 30세션) `/resume` 과 컴팩션 뒤에도 목록이 이어진다. 저장본이 없으면 대화 기록의 도구 호출에서 다시 모은다.

## 한계

- Mods 에는 화면 맨 위 고정 영역이 없다. 그래서 입력창 위에 둔다.
- 다른 도구(Claude Docs 커넥터 등)로 만든 문서는 `Artifact` 호출이 아니라 잡히지 않는다.

## 설치

```bash
claude plugins install session-artifacts@ai-common
```

로컬 시험: `claude --plugin-dir ./plugins/session-artifacts`

## 테스트

```bash
claude plugin test ./plugins/session-artifacts
```
