# FE Design Validation Protocol

FE 코드가 `docs/conventions/frontend-design.md`에 정의된 디자인 가드레일을 준수하는지 검증하는 프로토콜.

## 검증 대상 식별

### 대상 디렉터리 자동 감지

1. 프로젝트 루트에서 FE 프로젝트 탐지:
   ```
   Glob: **/frontend/package.json, **/front/package.json
   ```
2. 각 FE 프로젝트의 `src/` 디렉터리를 검증 대상으로 등록
3. `--target {path}` 옵션이 있으면 해당 경로만 검증

### 검증 파일 타입

- `*.tsx`, `*.jsx` — 컴포넌트 구조, 접근성, 인터랙션 상태
- `*.css`, `*.module.css` — 스타일 규칙, 안티패턴
- `*.ts` (Tailwind config, theme) — 디자인 토큰, 스케일
- `index.html` — viewport meta, 폰트 로딩

---

## 검증 카테고리

### Category A: AI Slop 탐지 (자동)

CSS/TSX/JSX 파일을 패턴 매칭으로 스캔.

| Check | Pattern | Severity |
|-------|---------|----------|
| A-1: Side-stripe border | `border-left: [2-9]px\|border-right: [2-9]px` (카드 컨텍스트) | FAIL |
| A-2: Gradient text | `background-clip:\s*text` + gradient | FAIL |
| A-3: AI 색상 팔레트 | purple/violet 계열 gradient + cyan 조합 | WARN |
| A-4: Bounce/elastic easing | `bounce\|elastic` in transition/animation | FAIL |
| A-5: 순수 검정 배경 | `background.*#000000\|background.*#000[^0-9a-f]\|rgb\(0,\s*0,\s*0\)` | WARN |
| A-6: 과용 폰트 | `font-family:.*Inter\|Roboto\|Open Sans\|Lato\|Montserrat` (명시적 선택 근거 없으면) | WARN |
| A-7: Glassmorphism 남용 | `backdrop-filter:\s*blur` 3회 이상 | WARN |
| A-8: Layout property animation | `transition:.*(?:width\|height\|padding\|margin)\|animation:.*(?:width\|height\|padding\|margin)` | FAIL |

### Category B: 타이포그래피 (자동 + 수동)

| Check | 방법 | Severity |
|-------|------|----------|
| B-1: body 텍스트 < 16px | Grep `font-size:.*(?:1[0-5]px\|0\.[0-8]rem)` in body/p context | FAIL |
| B-2: px 단위 font-size | Grep `font-size:.*\d+px` (rem이 아닌 것) | WARN |
| B-3: line-height < 1.3 | Grep `line-height:\s*(?:1\.[0-2]\|1\.0\|0\.)` body text context | WARN |
| B-4: 줄 길이 제한 없음 | 텍스트 컨테이너에 `max-width` 미설정 (수동 확인) | WARN |
| B-5: heading 레벨 건너뜀 | HTML/JSX에서 h1→h3 등 순서 건너뜀 | FAIL |
| B-6: user-scalable=no | `user-scalable=no` in meta viewport | FAIL |

### Category C: 색상과 대비 (자동 + 수동)

| Check | 방법 | Severity |
|-------|------|----------|
| C-1: 순수 회색 남용 | `color:.*#[0-9a-f]{3,6}` 중 chroma 0인 회색 다수 | WARN |
| C-2: 컬러 배경 위 회색 텍스트 | 수동 확인 — 색상 배경 컨테이너 내 gray/slate 텍스트 | WARN |
| C-3: 색상만으로 정보 전달 | 수동 확인 — error/success 상태에 색상만 사용 | FAIL |
| C-4: 다크모드 순수 검정 | dark theme에 `#000` 사용 | WARN |

### Category D: 레이아웃과 공간 (자동 + 수동)

| Check | 방법 | Severity |
|-------|------|----------|
| D-1: 임의 z-index | Grep `z-index:\s*(?:999\|9999\|99999)` | WARN |
| D-2: 임의 간격값 | 디자인 토큰 외 하드코딩 간격 다수 (수동 확인) | WARN |
| D-3: 중첩 카드 | JSX에서 Card 컴포넌트 내부에 Card 컴포넌트 (수동 확인) | WARN |
| D-4: margin 대신 gap 미사용 | Flex/Grid 컨텍스트에서 margin으로 간격 처리 (수동 확인) | INFO |

### Category E: 인터랙션과 접근성 (수동)

| Check | 방법 | Severity |
|-------|------|----------|
| E-1: focus outline 제거 | Grep `outline:\s*none\|outline:\s*0` (:focus 컨텍스트) | FAIL |
| E-2: 인터랙티브 상태 누락 | 버튼/입력 컴포넌트에 8가지 상태 중 누락 (수동 확인) | WARN |
| E-3: 터치 타겟 < 44px | 인터랙티브 요소의 최소 크기 확인 (수동 확인) | WARN |
| E-4: placeholder as label | input에 placeholder만 있고 label 없음 | FAIL |
| E-5: 모든 버튼이 Primary | 수동 확인 — 버튼 계층 구조 부재 | WARN |
| E-6: img alt 누락 | Grep `<img` without alt attribute | FAIL |

### Category F: 반응형 (수동)

| Check | 방법 | Severity |
|-------|------|----------|
| F-1: 모바일 퍼스트 미적용 | `max-width` 미디어 쿼리 우세 (수동 확인) | WARN |
| F-2: 호버 의존 기능 | hover에서만 접근 가능한 기능 존재 (수동 확인) | WARN |
| F-3: safe-area 미대응 | PWA에서 `env(safe-area-inset-*)` 미사용 | INFO |

### Category G: 모션 (자동)

| Check | 방법 | Severity |
|-------|------|----------|
| G-1: prefers-reduced-motion 미지원 | animation/transition 사용하면서 `prefers-reduced-motion` 미디어 쿼리 없음 | WARN |
| G-2: 제네릭 ease | `transition:.*ease[^-]` (ease-out-expo 등이 아닌 단순 ease) | INFO |

---

## 스코어링

### 심각도 가중치

| Severity | 점수 차감 | 설명 |
|----------|-----------|------|
| FAIL | -3 | 명확한 규칙 위반, 릴리스 전 수정 필수 |
| WARN | -1 | 품질 저하, 다음 사이클에 수정 |
| INFO | 0 | 개선 제안, 선택적 |

### 건강도 계산

```
base_score = 100
score = base_score - sum(deductions)
score = max(0, score)
```

| 범위 | 등급 | 의미 |
|------|------|------|
| 90-100 | Excellent | 디자인 완성도 높음 |
| 70-89 | Good | 소수 개선 필요 |
| 50-69 | Acceptable | 주요 패턴 위반 존재 |
| 30-49 | Poor | AI slop 지표 다수 |
| 0-29 | Critical | 전면 재작업 권장 |

---

## 검증 절차

### Phase 1: 자동 스캔

1. 대상 FE 프로젝트 식별
2. Category A (AI Slop) 전체 Grep 스캔
3. Category B (타이포그래피) 자동 체크 실행
4. Category C-D 자동 체크 실행
5. Category E (접근성) 자동 체크 실행 (img alt, outline:none 등)
6. Category G (모션) 자동 체크 실행

### Phase 2: 수동 확인

자동 스캔 결과를 바탕으로 수동 확인 항목 실행:
1. 컬러 배경 위 텍스트 대비 확인
2. 인터랙티브 요소 상태 완전성 확인
3. 레이아웃 카드 중첩 확인
4. 반응형 호버 의존 확인

### Phase 3: 리포트 생성

리포트 포맷은 커맨드 문서(validate-fe-design.md)의 Output Format 참조.

---

## 증거 요구사항

- 모든 finding은 `{file}:{line}` 참조 필수
- 증거 없는 finding은 무효
- FAIL: 파일 경로 + 라인 번호 + 위반 코드 스니펫
- WARN: 파일 경로 + 라인 번호 + 설명
- INFO: 파일 경로 + 설명

---

## 면제(Exemption) 처리

특정 패턴이 의도적 선택인 경우:
1. 해당 파일에 `/* fe-design-exempt: {rule-id} — {reason} */` 주석 추가
2. 검증 시 exempt 주석이 있으면 해당 체크 SKIP 처리
3. exempt 사유가 부적절하면 WARN으로 보고
