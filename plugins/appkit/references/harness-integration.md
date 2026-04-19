# appkit × hns 통합 가이드

appkit 은 `hns` (하네스 엔지니어링) 플러그인과 **옵셔널하게** 통합된다.
hns 가 설치돼 있으면 더 풍부한 문서 골격을 만들어내고, 없으면 scaffold 만 진행한다.

## 통합 방식

```
/appkit:init --with-harness
```

이 flag 가 붙으면 추가로 생성:

- `CLAUDE.md` — 하네스 규칙 stub (hns:init 에서 채우도록 placeholder)
- `agent-os/` 디렉토리 기본 골격
  - `agent-os/product/mission.md`
  - `agent-os/product/tech-stack.md`
  - `agent-os/standards/` (빈 디렉토리)
- `docs/adr/` — ADR 템플릿 1장
- `docs/specs/` — spec 템플릿 디렉토리
- `docs/plans/` — 플랜 템플릿 디렉토리

## 플로우

```
/appkit:init --with-harness
  ↓
appkit 이 hns 설치 체크 (check if /hns 명령 있는지)
  ↓ (있음)
scaffold + 하네스 골격 생성
  ↓
/hns:init 호출 안내 (사용자가 직접 실행)
  ↓
hns 가 채움 / 확장
```

## 명시적 의존 아님

appkit 의 동작은 hns 설치 여부와 **독립적**:
- hns 미설치 + `--with-harness` → 경고 출력, flag 무시
- hns 미설치 + flag 없음 → 정상 scaffold
- hns 설치 + flag 있음 → 풍부한 골격
- hns 설치 + flag 없음 → 기본 scaffold (hns 무시)

## 왜 분리했나

- **배포 단순**: appkit 만 설치해도 단독 동작 (hns 없이)
- **도메인 명확**: appkit = 앱 출시 / hns = 피처 개발
- **사용자 선택**: 둘 다 필요한 경우에만 함께 설치

## 향후 통합 지점 (로드맵)

- `/appkit:check` 가 하네스 규칙 준수도 측정 (hns 설치 시)
- `/appkit:release` 가 hns 의 doc-gen 연동 → 릴리스 노트 자동 생성
- `/appkit:seo` 가 hns 의 프로젝트 메타데이터 읽어 topics 자동 제안

이 통합은 v0.2+ 에서 선택적으로 추가.
