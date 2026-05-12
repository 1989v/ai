# Hierarchical Delegation Protocol

Context Routing의 **Level 0.5** — 모노레포·multi-service 레포에서 cwd 기준 nearest-ancestor `CLAUDE.md` + `docs/` 를 자동 누적 로드.

## Why

revfactory `harness` 6 팀 아키텍처 패턴 중 **계층적 위임**(Hierarchical Delegation)을 hns의 일급 패턴으로 표면화.
기존 PHASE 0이 root만 보던 한계를 해소 — 서비스마다 `CLAUDE.md`+`docs/`를 두는 모노레포에서 spec/review/tasks 단계가 서비스 로컬 규칙을 자동 흡수.

## Algorithm

```
walk = [cwd, cwd/.., cwd/../.., ..., repo_root]
loaded = []
for dir in walk:
  if (dir / "CLAUDE.md").exists():
    loaded.append({path: dir/CLAUDE.md, depth: distance_from_cwd})
  if (dir / "docs" / "index.yml").exists():
    loaded.append({path: dir/docs/index.yml, depth: distance_from_cwd})

# precedence: nearest wins on conflict, root is base.
apply(loaded, order=ascending_depth)
```

## Precedence Rules

| Source | Role | On Conflict |
|---|---|---|
| root `CLAUDE.md` | base policy | sub가 override |
| sub `CLAUDE.md` (cwd에 가까울수록 높은 우선순위) | local override / extension | nearest wins |
| root `docs/index.yml` | global keyword routing | sub와 병합 (sub keyword가 추가됨) |
| sub `docs/index.yml` | local routing extension | append to global |

## When Active

- `/hns:start` PHASE 0
- `/hns:create-tasks` (tasks 생성 시 sub-service convention 흡수)
- `/hns:spec-review` 5 reviewer (sub의 architecture/domain rule을 reviewer 컨텍스트에 주입)

## When Skipped

- 단일 모듈 프로젝트 (walk 결과 root `CLAUDE.md` 하나만 발견) — 기존 동작과 동일, regression 없음
- `--no-hier` 플래그 (필요 시 추가 — 현재 미구현)

## Examples

### msa 레포 (multi-service)
```
/IdeaProjects/msa/order/app/src/...   ← cwd
walk:
  - order/app/src/  (no CLAUDE.md)
  - order/app/      (no CLAUDE.md)
  - order/          → order/CLAUDE.md ✓ (서비스 로컬: 결제 연동·상태 전이)
  - /msa/           → CLAUDE.md ✓ (root: 전체 아키텍처·컨벤션)
loaded order: order/CLAUDE.md (closer) > msa/CLAUDE.md (root)
```

### 단일 모듈 프로젝트
```
/IdeaProjects/myapp/src/feature/...   ← cwd
walk: src/feature → src → myapp → CLAUDE.md ✓
loaded: 1개 (root only) — Level 0.5는 사실상 no-op
```

## Verify

- 임의 서비스(예: `order/`) 안에서 `/hns:start` 실행 → 컨텍스트 로그에 그 서비스의 `CLAUDE.md` 가 포함되는지 확인
- root만 있는 프로젝트에서 동작 변경 없음
