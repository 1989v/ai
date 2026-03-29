# Worktree Protocol

Use this protocol when worktree isolation is enabled in /hnsf:implement-tasks or /hnsf:orchestrate-tasks.

## 1) Resolve Project Root

Find nearest directory containing `.claude/scripts/parallel-work.sh`.
Walk up from current dir to workspace root.

If not found, stop with:
```
PROJECT ROOT NOT FOUND

Could not locate .claude/scripts/parallel-work.sh from:
  [current working directory]

To fix:
- Run /hnsf:init first to set up parallel execution
- Or run this command from inside the project directory
- Or answer "no" to worktree isolation
```

## 2) Worktree Lifecycle per Task Group

1. Determine base branch: `git branch --show-current`
2. Normalize task group slug: "Core DTO Changes" → "core-dto-changes"
3. Create worktree:
   ```bash
   .claude/scripts/parallel-work.sh create [task-group-slug] [base-branch]
   ```
4. Store `worktree_path` and `branch_name` for delegation
5. Delegate implementation in worktree directory
6. After completion, merge and clean up:
   ```bash
   cd [PROJECT_ROOT]
   git merge --no-ff [branch-name]
   .claude/scripts/parallel-work.sh remove [task-group-slug]
   ```

## 3) Conflict Handling

- Merge conflicts → **stop and report**. Do not auto-resolve.
- Report conflicting files and ask user for resolution strategy.

## 4) Parallel Execution Protocol

For /hnsf:orchestrate-tasks with `execution: parallel`:

1. Build dependency phases from `dependencies` field in orchestration.yml
2. Execute dependency-free groups first
3. For each parallel group in current phase:
   - Create worktree per group
   - Spawn background task with full context
   - Store task id
4. Collect all results and verify completion
5. Merge branches in dependency order
6. Run integration tests if applicable
7. Remove worktrees
8. Update status.md
