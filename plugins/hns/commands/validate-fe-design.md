---
description: "FE 디자인 컨벤션 검증 — AI slop 탐지, 타이포/색상/레이아웃/모션/접근성 규칙 준수 확인"
---

# /hns:validate-fe-design

## Purpose
FE 코드가 `docs/conventions/frontend-design.md`에 정의된 디자인 가드레일을 준수하는지 검증한다.
AI 생성 코드의 디자인 완성도를 자동 + 수동으로 측정하고 스코어링한다.

## Usage

```
/hns:validate-fe-design                    # 전체 FE 프로젝트 검증
/hns:validate-fe-design --target admin     # 특정 프로젝트만 검증
/hns:validate-fe-design --auto-only        # 자동 스캔만 (수동 확인 스킵)
/hns:validate-fe-design --fix              # FAIL 항목 자동 수정 시도
```

## Required Inputs
- `docs/conventions/frontend-design.md` 존재
- 하나 이상의 FE 프로젝트 (`**/frontend/package.json` 또는 `**/front/package.json`)

## Expected Outputs
- 검증 리포트 (카테고리별 PASS/WARN/FAIL + 건강도 스코어)

---

## PHASE 1: 대상 식별

1. FE 프로젝트 자동 감지:
   ```
   Glob: **/frontend/package.json, **/front/package.json
   ```
2. `--target {name}` 옵션이 있으면 해당 이름을 포함하는 프로젝트만 선택
3. 각 프로젝트의 `src/` 디렉터리를 검증 루트로 설정
4. 대상 파일 수집: `*.tsx`, `*.jsx`, `*.css`, `*.module.css`, `*.ts` (config/theme), `index.html`

---

## PHASE 2: 자동 스캔

프로토콜 참조: `@references/fe-design-validation-protocol.md`

각 카테고리별로 Grep/Glob 기반 패턴 매칭 실행.

### Category A: AI Slop 탐지

| ID | Check | Grep Pattern | Severity |
|----|-------|-------------|----------|
| A-1 | Side-stripe border | `border-(?:left\|right):\s*[2-9]px` | FAIL |
| A-2 | Gradient text | `background-clip:\s*text` | FAIL |
| A-3 | AI 색상 팔레트 | purple/violet gradient + cyan 조합 | WARN |
| A-4 | Bounce/elastic easing | `bounce\|elastic` in transition/animation context | FAIL |
| A-5 | 순수 검정 배경 | `#000000\|#000[^0-9a-f]\|rgb\(0,\s*0,\s*0\)` background context | WARN |
| A-6 | 과용 폰트 | `font-family:.*(?:Inter\|Roboto\|Open Sans\|Lato\|Montserrat)` | WARN |
| A-7 | Glassmorphism 남용 | `backdrop-filter:\s*blur` 3회 이상 | WARN |
| A-8 | Layout property animation | `transition:.*(?:width\|height\|padding\|margin)` | FAIL |

> exempt 주석 `/* fe-design-exempt: A-1 — {reason} */`이 있으면 SKIP

### Category B: 타이포그래피

| ID | Check | 방법 | Severity |
|----|-------|------|----------|
| B-1 | body < 16px | `font-size:.*(?:1[0-5]px\|0\.[0-8]rem)` body/p context | FAIL |
| B-2 | px 단위 font-size | `font-size:\s*\d+px` | WARN |
| B-3 | line-height < 1.3 | `line-height:\s*(?:1\.[0-2]\|1\.0\|0\.)` | WARN |
| B-5 | heading 건너뜀 | JSX/HTML에서 h1→h3 등 순서 건너뜀 | FAIL |
| B-6 | user-scalable=no | `user-scalable\s*=\s*no` | FAIL |

### Category C: 색상과 대비

| ID | Check | 방법 | Severity |
|----|-------|------|----------|
| C-1 | 순수 회색 남용 | `#(?:333\|666\|999\|ccc\|808080\|a0a0a0)` 등 chroma 0 다수 | WARN |
| C-3 | 색상만으로 정보 전달 | error/success에 아이콘/라벨 없이 색상만 사용 (수동) | FAIL |

### Category D: 레이아웃

| ID | Check | 방법 | Severity |
|----|-------|------|----------|
| D-1 | 임의 z-index | `z-index:\s*(?:999\|9999)` | WARN |

### Category E: 인터랙션과 접근성

| ID | Check | 방법 | Severity |
|----|-------|------|----------|
| E-1 | focus outline 제거 | `outline:\s*(?:none\|0)` :focus context | FAIL |
| E-4 | placeholder as label | `<input` with placeholder but no associated label | FAIL |
| E-6 | img alt 누락 | `<img` without `alt` attribute | FAIL |

### Category G: 모션

| ID | Check | 방법 | Severity |
|----|-------|------|----------|
| G-1 | reduced-motion 미지원 | animation/transition 존재 + `prefers-reduced-motion` 없음 | WARN |

---

## PHASE 3: 수동 확인 (`--auto-only`이면 스킵)

자동 스캔 결과를 기반으로 수동 검토 실행:

1. **컬러 배경 위 텍스트**: 색상 배경 컨테이너 내 회색 계열 텍스트 확인 (C-2)
2. **인터랙티브 상태 완전성**: 주요 버튼/입력 컴포넌트의 8가지 상태 구현 확인 (E-2)
3. **카드 중첩**: Card 컴포넌트 내부에 Card 컴포넌트가 있는지 확인 (D-3)
4. **버튼 계층**: Primary/Secondary/Ghost 구분이 있는지 확인 (E-5)
5. **반응형 호버 의존**: hover에서만 접근 가능한 기능이 있는지 확인 (F-2)
6. **줄 길이 제한**: 텍스트 컨테이너에 max-width 설정 여부 확인 (B-4)
7. **간격 토큰 사용**: 하드코딩 간격 vs 시맨틱 토큰 비율 확인 (D-2)

각 항목을 PASS/WARN/FAIL로 판정하고 증거(`{file}:{line}`)를 기록한다.

---

## PHASE 4: 스코어링

### 점수 계산

```
base = 100
FAIL 1건당 -3점
WARN 1건당 -1점
INFO 0점
score = max(0, base - deductions)
```

### 건강도 등급

| 범위 | 등급 | 의미 |
|------|------|------|
| 90-100 | Excellent | 디자인 완성도 높음 |
| 70-89 | Good | 소수 개선 필요 |
| 50-69 | Acceptable | 주요 패턴 위반 존재 |
| 30-49 | Poor | AI slop 지표 다수 |
| 0-29 | Critical | 전면 재작업 권장 |

---

## PHASE 5: 자동 수정 (`--fix` 옵션)

FAIL 항목 중 자동 수정 가능한 것만 처리:

| 항목 | 자동 수정 | 내용 |
|------|-----------|------|
| A-4 | Yes | bounce/elastic → ease-out-expo |
| A-8 | No | 레이아웃 변경 필요, 수동 |
| B-2 | Yes | px → rem 변환 (base 16px) |
| B-6 | Yes | `user-scalable=no` 제거 |
| E-1 | No | 대체 포커스 스타일 필요, 수동 |
| E-6 | No | 적절한 alt 텍스트 필요, 수동 |

자동 수정 후 재스캔하여 스코어 변화를 보고.

---

## Output Format

```
## FE Design Validation Report — {date}

### Target: {project-name} ({file-count} files scanned)

### Category A: AI Slop 탐지
  ✓ A-1 Side-stripe border — 미발견
  ✗ A-2 Gradient text — src/components/Hero.tsx:42
  ✓ A-4 Bounce/elastic — 미발견

### Category B: 타이포그래피
  ✓ B-1 body 텍스트 크기 — 16px 이상 확인
  ⚠ B-2 px 단위 font-size — src/styles/global.css:15, :28 (2건)
  ✓ B-5 heading 순서 — 정상

### Category C: 색상과 대비
  ⚠ C-1 순수 회색 — src/index.css:8 #808080 사용 (3건)

### Category D: 레이아웃
  ✓ D-1 z-index — 시맨틱 스케일 사용

### Category E: 인터랙션과 접근성
  ✗ E-6 img alt 누락 — src/pages/Home.tsx:55
  ✓ E-1 focus outline — 유지됨

### Category G: 모션
  ⚠ G-1 reduced-motion — animation 사용하나 미디어 쿼리 없음

---
### Score: 87/100 (Good)

| Severity | Count |
|----------|-------|
| ✓ PASS | 14 |
| ⚠ WARN | 4 |
| ✗ FAIL | 2 |

### 권장 조치
1. [FAIL] A-2 Gradient text 제거 → Hero.tsx:42
2. [FAIL] E-6 img alt 추가 → Home.tsx:55
3. [WARN] B-2 px→rem 변환 검토 → global.css
```

---

## 심각도 레벨

- **✓ PASS**: 규칙 준수 확인
- **⚠ WARN**: 품질 저하, 다음 사이클에 수정 권장
- **✗ FAIL**: 명확한 규칙 위반, 릴리스 전 수정 필수

## 오류 발견 시 처리

FAIL/WARN이 발견되면:
1. 사용자에게 상세 보고 (파일 경로, 라인 번호, 위반 코드)
2. 수정 옵션 제안:
   - **코드 수정**: 규칙에 맞게 코드 변경
   - **면제 등록**: 의도적 선택이면 `/* fe-design-exempt: {ID} — {reason} */` 추가
   - **무시**: 일회성 예외로 기록

## Integration

- **Convention source**: `docs/conventions/frontend-design.md`
- **Protocol**: `@references/fe-design-validation-protocol.md`
- **Called by**: hns:start (PHASE 7 Post-Implementation Validation, FE 프로젝트인 경우)
- **Standalone**: `/hns:validate-fe-design`, `/hns:validate-fe-design --target admin`
- **Calls**: 없음 (검증 전용)
