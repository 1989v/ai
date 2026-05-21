# claude-md-analyzer

Analyze layered Claude Code context (`CLAUDE.md` / memory / `settings.json`) to surface which rules **survive (Active)** versus get **overridden** in the current session.

## Why

Claude Code composes context from multiple layers — global (`~/.claude/`), project root (`{repo}/CLAUDE.md`), nested service dirs (`{service}/CLAUDE.md`), per-project user memory, plus settings hierarchy. As CLAUDE.md files grow it becomes hard to answer:

- Which rule actually applies *right now* in this working directory?
- When two layers say opposite things, who won?
- Are some rules effectively dead (stale path / permanently overridden)?

`claude-md-analyzer` answers these by **introspecting the live composed context** and cross-verifying citations against the filesystem.

## Commands

| Command | Purpose | Status |
|---------|---------|--------|
| `/claude-md:analyze` | Main analysis — composed context, conflict resolution, evidence verification | M1 (current) |
| `/claude-md:diff` | Cross-repo layered-context comparison | M4 |

## Quick start

```bash
# default — hybrid view (summary header + Conflict-only) with --warn evidence gating
/claude-md:analyze

# show Active rules too
/claude-md:analyze --all

# strict mode (CI) — drop any rule whose evidence can't be verified
/claude-md:analyze --strict

# JSON export
/claude-md:analyze --json
```

## How it works

1. **Inventory** (`scripts/collect-layers.sh`) enumerates layered files for `$PWD`.
2. **Hash & cache** (`scripts/hash-context.sh` + `cache-manager`) — if context unchanged, return cached result.
3. **Introspect (main)** — Claude examines its own composed system context, classifies rules as `Active` / `Overridden`, cites each with `path:line`.
4. **Evidence verify** (`verify-evidence` + `scripts/verify-source.sh`) — every citation cross-checked against the actual file content.
5. **Render** — hybrid format (header + Conflict-only) by default. `--all` / `--by-topic` / `--tree` / `--unverifiable` for drilling.

## Adapters (Pluggable Collectors)

| Source | Role | Status |
|--------|------|--------|
| `introspect` | Main path — Claude self-reports active/overridden | M1 |
| `fs` | Evidence verifier (with `introspect`) + standalone fallback | M1 |
| `hook` | SessionStart / PreToolUse snapshot for time-series | M3 |

`--source=auto` (default) uses `introspect + fs verify`.

## Roadmap

All milestones M1–M5 landed in `v1.0.0`:

- **M1** ✅ `analyze` main + fs verifier + cache + warn mode + `--all`
- **M2** ✅ `--by-topic` / `--tree` / `--unverifiable` + strict/loose + Dead/Stale heuristics
- **M3** ✅ Hook adapter — `hooks/cma-snapshot.sh` + `hooks/install-hooks.sh`
- **M4** ✅ `/claude-md:diff` cross-repo comparison
- **M5** ✅ marketplace registration, `hns:doctor` redirect, exported module interfaces for `#16 toggler` (see `references/exported-modules.md`)

Future (v2.x):
- Simulation mode (virtual prompt dry-run with cost gating)
- Additional Dead heuristics from hook log time-series
- Embedding-based clustering if introspect proves insufficient

## License

MIT
