---
name: doc-html
description: Use when generating a navigable HTML documentation site from docs/ markdown files - single index.html with sidebar navigation, no external dependencies
---

# Documentation Site Generation

## Overview

프로젝트의 docs/ 디렉터리를 재귀적으로 스캔하여 탐색 가능한 HTML 문서 사이트를 생성한다.
외부 의존성 없이 단일 index.html 파일로 완전한 문서 사이트를 제공한다.

## Process

### 1. docs/ 스캔

프로젝트 루트의 docs/ 디렉터리를 재귀적으로 탐색:
- 모든 `.md` 파일을 수집
- 디렉터리 구조를 트리로 구성
- 파일명과 첫 번째 `#` 헤딩을 페이지 제목으로 사용
- index.md가 있는 경우 해당 디렉터리의 대표 문서로 처리

MSA 멀티 모듈 프로젝트의 경우:
- 루트 docs/ + 각 서비스 모듈의 docs/ 를 모두 스캔
- 사이드바에서 루트 docs와 서비스별 docs를 구분하여 표시

### 2. Markdown 변환

각 마크다운 파일을 HTML로 변환:
- 헤딩 (`#`, `##`, `###`) → `<h1>`, `<h2>`, `<h3>`
- 코드 블록 (` ``` `) → `<pre><code>` (언어 클래스 포함)
- 인라인 코드 (`` ` ``) → `<code>`
- 굵게 (`**text**`) → `<strong>`
- 이탤릭 (`*text*`) → `<em>`
- 링크 (`[text](url)`) → `<a href>`
- 목록 (`-`, `*`, `1.`) → `<ul>`, `<ol>`
- 수평선 (`---`) → `<hr>`
- 인용 (`>`) → `<blockquote>`

### 3. HTML 생성

`site-template.html`을 기반으로 단일 `index.html` 생성:
- `{{projectName}}` → 프로젝트 이름 (디렉터리명 또는 CLAUDE.md에서 추출)
- `{{navigation}}` → 사이드바 디렉터리 트리 HTML
- `{{content}}` → 변환된 문서 내용 (초기 로드: index.md 또는 첫 번째 파일)
- 모든 문서 내용을 JavaScript 데이터로 포함 (SPA 방식)

### 4. 출력

```
{project-root}/docs-site/index.html
```

기존 파일이 있으면 덮어쓰기 전 사용자에게 확인.

## 사이드바 네비게이션 구조

```html
<nav class="sidebar">
  <div class="sidebar-header">
    <h1>{projectName} Docs</h1>
  </div>
  <ul class="nav-tree">
    <li class="nav-file active">
      <a href="#" data-doc="index">Overview</a>
    </li>
    <li class="nav-folder">
      <span class="folder-toggle">▶ architecture</span>
      <ul class="nav-subtree collapsed">
        <li class="nav-file">
          <a href="#" data-doc="architecture/overview">Overview</a>
        </li>
      </ul>
    </li>
    <li class="nav-folder">
      <span class="folder-toggle">▶ adr</span>
      <ul class="nav-subtree collapsed">...</ul>
    </li>
    ...
  </ul>
</nav>
```

폴더 클릭 시 expand/collapse 토글 (JavaScript).
현재 선택된 문서는 `active` 클래스로 하이라이트.

## 코드 블록 구문 강조

외부 라이브러리 없이 기본 구문 강조 제공:
- 언어별 키워드 색상 (kotlin, java, typescript, python, bash, yaml, json)
- 문자열 리터럴 강조
- 주석 강조 (`//`, `#`, `/* */`)
- 숫자 리터럴 강조

## 출력 파일 특성

- **단일 파일**: 모든 문서 내용이 하나의 `index.html`에 포함
- **외부 의존성 없음**: CDN, 외부 JS/CSS 라이브러리 사용 안 함
- **인라인 CSS/JS**: 스타일과 스크립트가 HTML 내부에 포함
- **반응형 레이아웃**: 사이드바 + 메인 콘텐츠 2컬럼 레이아웃
- **SPA 방식**: 페이지 이동 없이 JavaScript로 문서 전환

## Integration

- **Called by:** 없음 (독립 실행)
- **Standalone:** `/harness-scaffold:doc-html`로 직접 호출 가능
- **Calls:** 없음 (최종 생성 스킬)
- **Template:** `templates/site-template.html` 참조
