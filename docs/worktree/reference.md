# devkit.worktree

One activity branch (`plan-<slug>`, `dev-<slug>`) per task activity, with its own Git worktree when it needs one, integrated and removed by one command. Semantics: [Task Worktrees Overview](overview.md).

## Usage

```bash
uv run devkit worktree start dev-login          # in the base checkout: create ../<repo>-wt-dev-login on branch dev-login
cd ../<repo>-wt-dev-login                        # work and commit there
uv run devkit worktree finish dev-login          # in the base, after the pull request merged
uv run devkit worktree finish dev-login --merge  # or merge locally (refused under [worktree] pull_request = "required")
uv run devkit worktree finish dev-login --discard  # close: drop the unmerged branch and its worktree
uv run devkit worktree start dev-login --no-worktree   # or: the branch in this checkout, no separate directory
uv run devkit worktree start dev-login --existing-branch origin/dev-login --unit docs/specs/login  # continue it
uv run devkit worktree status                    # leftovers: unmerged or dirty worktrees, stray branches
uv run devkit worktree stale                     # plan-*/dev-* branches idle longer than [worktree] stale_after
```

Every command takes `-w/--workspace-root` (any directory in the checkout; default the current directory), `--format text|json` and the shared output options.

## Output

```text
[WORKTREE_STARTED: dev-login path=/src/app-wt-dev-login base=/src/app created=yes existing=no unit=- setup="uv sync" synced=yes]
[NEXT_CMD: cd /src/app-wt-dev-login]
[BRANCH_STARTED: dev-login checkout=/src/app from=main]
[WORKTREE_FINISHED: dev-login path=/src/app-wt-dev-login merged=yes push=pushed removed=yes branch_deleted=yes discarded=no]
[WORKTREE: /src/app branch=main head=1a2b3c4 role=base merged=- dirty=no prunable=no]
[WORKTREE: /src/app-wt-dev-login branch=dev-login head=5d6e7f8 role=linked merged=no dirty=yes prunable=no]
[BRANCH: spike head=9a8b7c6 merged=no]
[SUMMARY: base=/src/app base_branch=main worktrees=1 unmerged=1 dirty=1 branches=1]
[STALE_BRANCH: plan-cache unit=docs/proposals/PROP-cache last_activity=2026-09-20T08:00:00Z pr=draft refs=local,origin]
[SUMMARY: checked=yes branches=4 stale=1 stale_after=14d]
```

`existing` is `yes` for `--existing-branch`, whose `unit` is the given unit. `synced` is `yes` when `devkit sync --locked` restored the project's managed files in the new worktree, `no` when it failed and `-` when it did not run (no receipt, or a worktree `--existing-branch` reused). `push` is `pushed`, `rejected` (the upstream moved on), `failed`, `no-upstream`, or `-` without `--merge`. `removed` is `yes` also when a rerun found the worktree already gone, and `-` (JSON `null`) when the branch never had one (a `--no-worktree` branch, whose `path` is the checkout it was started in, or a branch made by hand). `discarded` is `yes` for `--discard`. `stale` prints `checked=no` and nothing else when `gh` is missing or logged out; `pr` is `none`, `draft`, `open`, `blocked`, `merged`, `closed` or `unknown`. JSON keys: `start`: `branch`, `slug`, `path`, `base`, `created`, `existing`, `unit`, `setup`, `synced`, `notices`; `start --no-worktree`: `branch`, `slug`, `checkout`, `from`, `notices`; `finish`: `branch`, `slug`, `path`, `merged`, `push`, `removed`, `branch_deleted`, `discarded`, `notices`, plus `errors` when a refusal stopped it after a change; `status`: `base`, `base_branch`, `worktrees` (`path`, `branch`, `head`, `role`, `merged`, `dirty`, `prunable`), `branches` (`name`, `head`); `stale`: `checked`, `stale_after`, `branches` (the activity branches examined), `stale` (`branch`, `unit`, `last_activity`, `pr`, `pr_url`, `refs`), `notices`.

## Configuration

`[worktree]` in `.devkit/config.toml`: `pull_request` (`"auto"` or `"required"`, default `"auto"`), `delete_branch` (default `true`), `setup` (a shell command, default none), `stale_after` (`"<N>d"` or `"<N>w"`, default `"14d"`). See [Overview, section 5](overview.md#5-configuration).

## Extension points

| Group | Called | Signature | Effect |
| --- | --- | --- | --- |
| `devkit.post_finish` | after a successful `finish` | `extension(base, result)` | returned strings and advisories become notices; never fails the finish |
| `devkit.finish_guard` | `finish --merge`, before the first change | `extension(base, branch, merge_base, tip)` | returned reasons refuse (`WORKTREE_BLOCKED`); a failure refuses (`WORKTREE_GUARD_FAILED`) |
| `devkit.attach_check` | `start --existing-branch`, before the first change | `extension(root, branch, unit, tip)` | returned reasons refuse (`WORKTREE_ATTACH_REFUSED`); a failure refuses (`WORKTREE_ATTACH_CHECK_FAILED`) |

`devkit.worktree` itself registers the `devkit.hygiene` extension `worktree-stale` ([Overview, section 6](overview.md#6-stale-branches)).

## Error codes

`0` success, also for `status` and `stale` whatever they list; `2` a refusal or an error. Warnings exit `0` (`1` under `--strict`).

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `WORKTREE_NESTED` | `ERROR` (`BLOCKED`) | `NestedError` | `start` inside a linked worktree. |
| `WORKTREE_RUN_FROM_BASE` | `ERROR` (`BLOCKED`) | `RunFromBaseError` | `finish` inside a linked worktree. |
| `WORKTREE_PR_POLICY` | `ERROR` (`BLOCKED`) | `PullRequestPolicyError` | `finish --merge` under `pull_request = "required"`. |
| `WORKTREE_UNSUPPORTED_LAYOUT` | `ERROR` (`BLOCKED`) | `UnsupportedLayoutError` | A Git directory outside its work tree. |
| `WORKTREE_BASE_ON_BRANCH` | `ERROR` (`AUTO`) | `BaseOnBranchError` | `finish` or `finish --discard` while the base checkout is on the `--no-worktree` branch it finishes; `[FIX]` switches it back to the recorded `devkitBase`, then rerun. Nothing changed. |
| `WORKTREE_CONFLICT` | `ERROR` (`INTERACTION`) | `ConflictError` | `start`: the branch's path is a worktree on another branch or a missing directory (`[FIX]` `git worktree prune`), or exists and is not a worktree (also when another process created it while `start` ran; it is left alone). `start --existing-branch` also: the base checkout is on the branch with uncommitted changes, or without a recorded `devkitBase` to switch back to. `finish`: the worktree is detached or on another branch, or the base checkout is on a branch `start --no-worktree` did not create; `--merge` of a `--no-worktree` branch from a checkout on another branch than its `devkitBase`; the branch moved after the guard checked it (rerun once the run committing to it ends). `--discard`: as `finish`. |
| `WORKTREE_BRANCH_EXISTS` | `ERROR` (`INTERACTION`) | `BranchExistsError` | A new branch exists locally or on a remote, already has its worktree at its path (only `--existing-branch` reuses it), or is checked out elsewhere, also when another process created it while `start` ran (nothing is removed); the `[FIX]` names `--existing-branch`. `start --existing-branch`: the branch is checked out in a worktree at another path. |
| `WORKTREE_BRANCH_OUT_OF_SYNC` | `ERROR` (`INTERACTION`) | `BranchOutOfSyncError` | `start --existing-branch`: the local branch is behind or has diverged from its remote-tracking branch; never merged or reset. The `[FIX]` fast-forwards a branch that is only behind. Nothing changed. |
| `WORKTREE_BRANCH_AHEAD` | `NOTICE` | `BranchAheadNotice` | `start --existing-branch`: the local branch has commits its remote-tracking branch lacks; it is attached as it is, and the `[FIX]` pushes it when the work is to be shared. |
| `WORKTREE_UNIT_INVALID` | `ERROR` (`INPUT_ERROR`) | `UnitInvalidError` | `start --existing-branch`: `--unit` is empty, absolute, leaves the project, or is not a directory of the branch's tree. |
| `WORKTREE_ATTACH_REFUSED` | `ERROR` (`INTERACTION`) | `AttachRefusedError` | A `devkit.attach_check` extension found that the branch and the unit do not belong together; each reason is a detail. Nothing changed. |
| `WORKTREE_ATTACH_CHECK_FAILED` | `ERROR` (`MAINTENANCE`) | `AttachCheckFailedError` | A `devkit.attach_check` extension raised or returned something other than a list of strings; the attach is refused. |
| `WORKTREE_BLOCKED` | `ERROR` (`INTERACTION`) | `BlockedError` | A `devkit.finish_guard` extension refused `finish --merge` (an unresolved problem or an unanswered question in the branch's units); each reason is a detail. Nothing changed. |
| `WORKTREE_GUARD_FAILED` | `ERROR` (`MAINTENANCE`) | `GuardFailedError` | A `devkit.finish_guard` extension raised or returned something other than a list of strings; `finish --merge` is refused. Nothing changed. |
| `WORKTREE_NOT_FOUND` | `ERROR` (`INTERACTION`) | `NotFoundError` | No worktree has the branch's path or branch, and (for `finish`) the branch does not exist or lacks the `branch.<branch>.devkitWorktree` marker `start` records. A merged branch without the marker (also one `start` created before devkit recorded the marker: such branches are not resumed automatically) is never deleted: `[FIX]` is `git branch -d <branch>` once the user agrees. Nothing changed, whatever `delete_branch` says: no `before_remove`, merge or push runs for such a branch. A completed finish removes the marker (with the branch, or unset when `delete_branch = false`), so its rerun is this too. `start --existing-branch`: the branch exists neither locally nor as a fetched remote-tracking ref, or a named remote's ref was never fetched while a local branch exists (`[FIX]` fetches). `finish --discard`: the branch does not exist. |
| `WORKTREE_LOCKED` | `ERROR` (`INTERACTION`) | `LockedError` | `finish` found the worktree locked; `[FIX]` unlocks it. Nothing changed. |
| `WORKTREE_BASE_DETACHED` | `ERROR` (`INTERACTION`) | `BaseDetachedError` | `--merge` with the base on a detached HEAD, or `start --no-worktree` on one. Nothing changed. |
| `WORKTREE_BASE_DIRTY` | `ERROR` (`INTERACTION`) | `BaseDirtyError` | `--merge` with uncommitted changes in the base. |
| `WORKTREE_BASE_BEHIND` | `ERROR` (`INTERACTION`) | `BaseBehindError` | `--merge`: the fetched upstream of the base branch has commits the base lacks; `[FIX]` is `git pull --ff-only`. Nothing changed. |
| `WORKTREE_BRANCH_UNPUSHED` | `ERROR` (`INTERACTION`) | `BranchUnpushedError` | The branch's upstream lacks its commits, so `git branch -d` would refuse it; `[FIX]` pushes it. Nothing changed. |
| `WORKTREE_MERGE_NOT_FF` | `ERROR` (`INTERACTION`) | `MergeNotFastForwardError` | The base cannot be fast-forwarded onto the branch. |
| `WORKTREE_UNMERGED` | `ERROR` (`INTERACTION`) | `UnmergedError` | Without `--merge`, the branch (with a worktree, or a marked one without) is not merged into the base HEAD. |
| `WORKTREE_DIRTY` | `ERROR` (`INTERACTION`) | `DirtyError` | The worktree has uncommitted or untracked changes. |
| `WORKTREE_ADD_FAILED` | `ERROR` (`INTERACTION`) | `AddFailedError` | `start`: `git worktree add` failed or timed out (1800 seconds), or recording the branch's marker failed; what it created was removed, or is listed as `left:` details with the removing commands as `[FIX]` (a branch that no longer points at the base HEAD it was created from is never deleted, only listed). Git runs in a session of its own, so a timeout also kills its hooks and filters. |
| `WORKTREE_REMOVE_FAILED` | `ERROR` (`INTERACTION`) | `RemoveFailedError` | `git worktree remove` failed for another reason or timed out (1800 seconds; `[FIX]` removes the partly deleted worktree); carries the partial result, a rerun resumes. |
| `WORKTREE_BRANCH_DELETE_FAILED` | `ERROR` (`INTERACTION`) | `BranchDeleteFailedError` | `git branch -d` failed after the removal; carries the partial result, a rerun deletes the branch. |
| `WORKTREE_CONFIG_INVALID` | `ERROR` (`INPUT_ERROR`) | `WorktreeConfigError` | A malformed `[worktree]` table. |
| `WORKTREE_PUSH_REJECTED` | `WARNING` | `PushRejectedWarning` | The upstream moved on and rejected the push of the merged base; `[FIX]` integrates it (`git pull --rebase`), then pushes. |
| `POST_FINISH_EXTENSION_FAILED` | `WARNING` | `PostFinishExtensionFailedNotice` | A `devkit.post_finish` extension raised an exception other than an advisory, or returned something other than a list; the finish succeeded. |
| `POST_FINISH_NOTICE` | `NOTICE` | `PostFinishNotice` | A line a `devkit.post_finish` extension returned (`brief`). |
| `WORKTREE_PUSH_FAILED` | `WARNING` | `PushFailedWarning` | The merged base branch did not reach its upstream for another reason; `[FIX]` is the push. |
| `WORKTREE_REMOTE_UNCHECKED` | `WARNING` | `RemoteUncheckedWarning` | `start` could not ask a remote whether it has the new branch; its remote-tracking ref from the last fetch stood in. |
| `WORKTREE_STALE_BRANCH` | `WARNING` | `StaleBranchWarning` | `stale` and hygiene runs: an activity branch idle longer than `stale_after`; details name its unit, refs and pull request, the `[FIX]` how to resume it and, once the user decides, discard it. |
| `WORKTREE_STALE_SKIPPED` | `NOTICE` | `StaleSkippedNotice` | `gh` is missing or `gh auth status` failed; no branch was judged. |
| `WORKTREE_STALE_PR_UNKNOWN` | `NOTICE` | `StalePullRequestsUnknownNotice` | `gh pr list` failed; branches were judged by their last commit alone. |
| `WORKTREE_SETUP_FAILED` | `WARNING` | `SetupFailedWarning` | The `setup` command failed or timed out; `[FIX]` reruns it. |
| `WORKTREE_SYNC_FAILED` | `WARNING` | `SyncFailedWarning` | `devkit sync --locked` failed or timed out in the new worktree. The message names the sync's own error code and message; `[TARGET]`, `[DETAIL]` and `[FIX]` are that error's (its fix prefixed with the worktree path), or the rerun command when the output was not an error object. |
| `ARGUMENT_INVALID` | `ERROR` (`INPUT_ERROR`) | `devkit.core.ArgumentError` | A name that is not an activity branch (`plan-<slug>`, `dev-<slug>`); `--existing-branch` that is neither the branch nor `<remote>/<branch>`, or names a branch several remotes have; `--existing-branch` without `--unit` or the reverse; `--no-worktree` with either. |
| `GIT_FAILED` | `ERROR` | `devkit.core.GitError` | Not in a Git work tree, or another Git command failed. |

## Library

```python
from devkit.worktree import attach, finish, locate, read_worktree_config, stale_branches, start, start_branch, status

position = locate(Path.cwd())
config = read_worktree_config(project_root)
started = start(position, "dev-login", setup=config.setup, project=Path("."))  # StartResult(path, created, synced, notices, ...)
branch = start_branch(position, "dev-login")                          # BranchStartResult(checkout, started_from, ...)
attached = attach(position, "dev-login", source="origin/dev-login", unit="docs/specs/login",
                  setup=config.setup, project=Path("."), check=lambda root, branch, unit, tip: ...)
done = finish(position, "dev-login", merge=False, pull_request=config.pull_request,
              delete_branch=config.delete_branch, before_remove=lambda result: ...,
              guard=lambda merge_base, tip: ...)                       # guard runs with merge=True only
report = status(position)                                             # StatusResult(worktrees, branches)
stale = stale_branches(position, config.stale_after)                  # StaleResult(checked, stale, notices, ...)
```

`attach`'s `check` and `finish`'s `guard` refuse by raising; the CLI passes the `devkit.attach_check` and `devkit.finish_guard` extensions (`run_attach_checks`, `run_finish_guards` in `devkit.worktree.extensions`). A refusal raised after `finish` changed something has the partial `FinishResult` as `error.result`, also an `AdvisoryError` that `before_remove` raises (unless it defines a `result` of its own); rerunning `finish` resumes, also when only the merged branch is left and carries the `branch.<branch>.devkitWorktree` marker `start` records ([Overview, section 3](overview.md#3-finish)).
