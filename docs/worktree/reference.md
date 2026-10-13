# devkit.worktree

One Git worktree per task, integrated and removed by one command. Semantics: [Task Worktrees Overview](overview.md).

## Usage

```bash
uv run devkit worktree start fix-login          # in the base checkout: create ../<repo>-wt-fix-login on branch fix-login
cd ../<repo>-wt-fix-login                        # work and commit there
uv run devkit worktree finish fix-login          # in the base, after the pull request merged
uv run devkit worktree finish fix-login --merge  # or merge locally (refused under [worktree] pull_request = true)
uv run devkit worktree status                    # leftovers: unmerged or dirty worktrees, stray branches
```

Every command takes `-w/--workspace-root` (any directory in the checkout; default the current directory), `--format text|json` and the shared output options.

## Output

```text
[WORKTREE_STARTED: fix-login path=/src/app-wt-fix-login branch=fix-login base=/src/app created=yes setup="uv sync" synced=yes]
[NEXT_CMD: cd /src/app-wt-fix-login]
[WORKTREE_FINISHED: fix-login path=/src/app-wt-fix-login merged=yes push=pushed removed=yes branch_deleted=yes]
[WORKTREE: /src/app branch=main head=1a2b3c4 role=base merged=- dirty=no prunable=no]
[WORKTREE: /src/app-wt-fix-login branch=fix-login head=5d6e7f8 role=linked merged=no dirty=yes prunable=no]
[BRANCH: spike head=9a8b7c6 merged=no]
[SUMMARY: base=/src/app base_branch=main worktrees=1 unmerged=1 dirty=1 branches=1]
```

`synced` is `yes` when `devkit sync --locked` restored the project's managed files in the new worktree, `no` when it failed and `-` when it did not run (no receipt, or a reused worktree). `push` is `pushed`, `rejected` (the upstream moved on), `failed`, `no-upstream`, or `-` without `--merge`. `removed` is `yes` also when a rerun found the worktree already gone. JSON keys: `start`: `slug`, `path`, `branch`, `base`, `created`, `setup`, `synced`, `notices`; `finish`: `slug`, `path`, `branch`, `merged`, `push`, `removed`, `branch_deleted`, `notices`, plus `errors` when a refusal stopped it after a change; `status`: `base`, `base_branch`, `worktrees` (`path`, `branch`, `head`, `role`, `merged`, `dirty`, `prunable`), `branches` (`name`, `head`).

## Configuration

`[worktree]` in `.devkit/config.toml`: `pull_request` (default `false`), `delete_branch` (default `true`), `setup` (a shell command, default none). See [Overview, section 5](overview.md#5-configuration).

## Error codes

`0` success, also for `status` whatever it lists; `2` a refusal or an error. Warnings exit `0` (`1` under `--strict`).

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `WORKTREE_NESTED` | `ERROR` (`BLOCKED`) | `NestedError` | `start` inside a linked worktree. |
| `WORKTREE_RUN_FROM_BASE` | `ERROR` (`BLOCKED`) | `RunFromBaseError` | `finish` inside a linked worktree. |
| `WORKTREE_PR_POLICY` | `ERROR` (`BLOCKED`) | `PullRequestPolicyError` | `finish --merge` under `pull_request = true`. |
| `WORKTREE_UNSUPPORTED_LAYOUT` | `ERROR` (`BLOCKED`) | `UnsupportedLayoutError` | A Git directory outside its work tree. |
| `WORKTREE_CONFLICT` | `ERROR` (`INTERACTION`) | `ConflictError` | `start`: the slug's path is a worktree on another branch, has uncommitted changes or a missing directory (`[FIX]` `git worktree prune`), or exists and is not a worktree. `finish`: the worktree is detached or on another branch, or the slug's branch is the base checkout's. |
| `WORKTREE_BRANCH_EXISTS` | `ERROR` (`INTERACTION`) | `BranchExistsError` | The slug's branch exists or is checked out elsewhere. |
| `WORKTREE_NOT_FOUND` | `ERROR` (`INTERACTION`) | `NotFoundError` | No worktree has the slug's path or branch, and (for `finish`) no branch of the slug is merged into the base HEAD. |
| `WORKTREE_LOCKED` | `ERROR` (`INTERACTION`) | `LockedError` | `finish` found the worktree locked; `[FIX]` unlocks it. Nothing changed. |
| `WORKTREE_BASE_DETACHED` | `ERROR` (`INTERACTION`) | `BaseDetachedError` | `--merge` with the base on a detached HEAD. Nothing changed. |
| `WORKTREE_BASE_DIRTY` | `ERROR` (`INTERACTION`) | `BaseDirtyError` | `--merge` with uncommitted changes in the base. |
| `WORKTREE_BASE_BEHIND` | `ERROR` (`INTERACTION`) | `BaseBehindError` | `--merge`: the fetched upstream of the base branch has commits the base lacks; `[FIX]` is `git pull --ff-only`. Nothing changed. |
| `WORKTREE_BRANCH_UNPUSHED` | `ERROR` (`INTERACTION`) | `BranchUnpushedError` | The branch's upstream lacks its commits, so `git branch -d` would refuse it; `[FIX]` pushes it. Nothing changed. |
| `WORKTREE_MERGE_NOT_FF` | `ERROR` (`INTERACTION`) | `MergeNotFastForwardError` | The base cannot be fast-forwarded onto the branch. |
| `WORKTREE_UNMERGED` | `ERROR` (`INTERACTION`) | `UnmergedError` | Without `--merge`, the branch is not merged into the base HEAD. |
| `WORKTREE_DIRTY` | `ERROR` (`INTERACTION`) | `DirtyError` | The worktree has uncommitted or untracked changes. |
| `WORKTREE_REMOVE_FAILED` | `ERROR` (`INTERACTION`) | `RemoveFailedError` | `git worktree remove` failed for another reason; carries the partial result, a rerun resumes. |
| `WORKTREE_BRANCH_DELETE_FAILED` | `ERROR` (`INTERACTION`) | `BranchDeleteFailedError` | `git branch -d` failed after the removal; carries the partial result, a rerun deletes the branch. |
| `WORKTREE_CONFIG_INVALID` | `ERROR` (`INPUT_ERROR`) | `WorktreeConfigError` | A malformed `[worktree]` table. |
| `WORKTREE_PUSH_REJECTED` | `WARNING` | `PushRejectedWarning` | The upstream moved on and rejected the push of the merged base; `[FIX]` integrates it (`git pull --rebase`), then pushes. |
| `POST_FINISH_EXTENSION_FAILED` | `WARNING` | `PostFinishExtensionFailedNotice` | A `devkit.post_finish` extension raised or returned something other than a list; the finish succeeded. |
| `POST_FINISH_NOTICE` | `NOTICE` | `PostFinishNotice` | A line a `devkit.post_finish` extension returned (`brief`). |
| `WORKTREE_PUSH_FAILED` | `WARNING` | `PushFailedWarning` | The merged base branch did not reach its upstream for another reason; `[FIX]` is the push. |
| `WORKTREE_SETUP_FAILED` | `WARNING` | `SetupFailedWarning` | The `setup` command failed or timed out; `[FIX]` reruns it. |
| `WORKTREE_SYNC_FAILED` | `WARNING` | `SyncFailedWarning` | `devkit sync --locked` failed or timed out in the new worktree. The message names the sync's own error code and message; `[TARGET]`, `[DETAIL]` and `[FIX]` are that error's (its fix prefixed with the worktree path), or the rerun command when the output was not an error object. |
| `ARGUMENT_INVALID` | `ERROR` (`INPUT_ERROR`) | `devkit.core.ArgumentError` | An invalid slug. |
| `GIT_FAILED` | `ERROR` | `devkit.core.GitError` | Not in a Git work tree, or another Git command failed. |

## Library

```python
from devkit.worktree import finish, locate, read_worktree_config, start, status

position = locate(Path.cwd())
config = read_worktree_config(project_root)
started = start(position, "fix-login", setup=config.setup, project=Path("."))  # StartResult(path, created, synced, notices, ...)
done = finish(position, "fix-login", merge=False, pull_request=config.pull_request,
              delete_branch=config.delete_branch, before_remove=lambda result: ...)
report = status(position)                                             # StatusResult(worktrees, branches)
```

A refusal raised after `finish` changed something has the partial `FinishResult` as `error.result`; rerunning `finish` resumes, also when only the merged branch is left ([Overview, section 3](overview.md#3-finish)).
