# GC Protocol

## Scan Modes

### Light Scan (이벤트 트리거)
커밋 후 자동 실행. 빠르게 끝나야 함 (30초 이내).
- 변경된 파일 범위에서만 doc drift 체크
- CLAUDE.md에 언급된 모듈/경로가 아직 유효한지 spot check

### Full Scan (수동/스케줄)
프로젝트 전체 순회.
1. **Dead code**: 미사용 import, 빈 파일, 호출 없는 public 함수
2. **Doc drift**: CLAUDE.md/docs 내용 vs 실제 코드 구조 비교
3. **Rule violation**: agent-os/standards/의 규칙 vs 코드 위반 탐지
4. **Stale harness**: 3개월 이상 트리거 안 된 규칙/훅 식별

## Report Format

```markdown
# GC Report — {date}

## Summary
| Category | Found | Auto-fixed | Manual Required |
|----------|-------|------------|-----------------|

## Dead Code
- [ ] {file:line} — {description}

## Doc Drift
- [ ] {doc-path} vs {code-path} — {drift description}

## Rule Violations
- [ ] {rule} — {violation in file:line}

## Stale Harness
- [ ] {rule/hook} — last triggered: {date or never}
```

## Auto-fix Policy
- Dead imports → auto-remove
- Doc path typos → auto-correct
- 나머지 → 사용자 확인 필요
