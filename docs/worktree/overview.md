# Task Worktrees: Overview

`devkit.worktree` gives each task its own Git worktree and turns the end of the task into one deterministic command. A task named by a slug runs in `<parent of base>/<base name>-wt-<slug>` on branch `<slug>`; `finish` integrates the branch into the base checkout, removes the worktree and deletes the branch. Every step refuses instead of forcing, and rerunning the same command resumes where it stopped. Quick reference: [reference.md](reference.md).

The module is SDD-agnostic: it does not decide which tasks use a worktree, and it knows no document layout. A methodology layer (devkit-spec) decides when a task gets a worktree, adds its own cleanup through a `devkit.post_finish` extension (or the library's `before_remove` callback), and keeps any scope registry of its own.

## 1. Checkouts and Paths

- **Base checkout**: the work tree whose `.git` directory is the repository's common Git directory. `start` and `finish` run there; `status` runs from any checkout. A bare repository, or a Git directory outside its work tree (`--separate-git-dir`, submodules), is `WORKTREE_UNSUPPORTED_LAYOUT`.
- **Task worktree**: `<parent of base>/<base name>-wt-<slug>` on branch `<slug>`, created from the base HEAD. The rule is fixed so every session and agent computes the same path.
- **Marker**: every branch `start` creates carries `branch.<slug>.devkitWorktree = <worktree path>` in the repository's common Git configuration (`.git/config`, shared by all worktrees). It tells a task branch from an ordinary branch that happens to share the slug's name (`release`), and only gates `finish` on a slug that has no worktree ([section 3](#3-finish)). It lasts until `finish` completes: `git branch -d` removes it with the branch (Git drops the branch's `branch.<name>` configuration section), and with `delete_branch = false` `finish` unsets it once the worktree is removed (step 4).
- **Slug**: lowercase letters, digits, `-` and `_`, starting with a letter or digit, 64 characters at most; anything else is `ARGUMENT_INVALID`. A caller turns its own names (a proposal id, a ticket) into a slug before calling.

## 2. start

1. Refuse inside a linked worktree (`WORKTREE_NESTED`): worktrees are not nested.
2. If the slug's path is already a worktree on the slug's branch and clean, reuse it (`created=no`). On another branch, or with uncommitted changes, it is `WORKTREE_CONFLICT`; so is a registered worktree whose directory was deleted (`prunable`), with `git worktree prune` as its `[FIX]`.
3. A branch named after the slug that is checked out elsewhere, or that already exists, is `WORKTREE_BRANCH_EXISTS`; a path that exists but is not a worktree is `WORKTREE_CONFLICT`.
4. Otherwise `git worktree add -b <slug> <path>` from the base HEAD, within 1800 seconds (a large checkout, LFS or slow hooks take long), then `git config --local branch.<slug>.devkitWorktree <path>`, the marker ([section 1](#1-checkouts-and-paths)). Uncommitted changes in the base stay in the base. `git worktree add` and `git worktree remove` run in a session of their own, so a timeout kills the `post-checkout` hook and checkout filters (Git LFS) with Git rather than leaving them writing into a path the cleanup removes. When either step fails or times out (a failing `post-checkout` hook fails it too), `start` removes what it created, the registered worktree (with `--force --force`: Git locks a worktree while it checks it out) and the branch (with `git branch -d`, and only while it still points at the base HEAD it was created from; a branch a hook committed to is left), and raises `WORKTREE_ADD_FAILED` with Git's reason, so the rerun starts afresh; whatever it could not remove is listed as `left:` details, with the commands that remove it as the `[FIX]`. When another process creates the branch or the path between the checks of step 3 and Git, Git refuses with "already exists" and `start` removes nothing of it: a branch is `WORKTREE_BRANCH_EXISTS`; a path is `WORKTREE_CONFLICT`, once the branch Git created before refusing is removed.
5. A new worktree is a fresh checkout without the base's ignored files: no `.venv`, no build output, and no `.devkit/managed/`, the synchronized copies that `.devkit/.gitignore` keeps out of Git. Two steps restore what work and commits need:
   1. **setup**: the `[worktree] setup` command, if configured, runs through `/bin/sh -c` in the worktree, without the caller's `VIRTUAL_ENV`, within 900 seconds. Set it to the project's environment step, for example `uv sync` or `just init`.
   2. **sync**: when the devkit project the command runs in has a receipt (`.devkit/installation.json`), `devkit sync --locked` runs in the same project directory of the worktree, within 300 seconds, with the worktree's `.venv/bin/python` when setup created one with devkit installed in it (a `devkit_agt-*.dist-info` in its `site-packages`, the test the commit gate hooks apply), else the interpreter running `start`. It writes the ignored managed copies only and never changes the tracked receipt, `AGENTS.md` or seeded files; when the worktree's environment no longer matches the committed receipt (a `RECEIPT_STALE` exit `1`) or lacks a deployed bundle's package, it fails and `start` reports `WORKTREE_SYNC_FAILED`. Without it, every devkit command that reads managed files fails in the worktree: bundle rules (and so a `devkit rules check --staged` commit gate, which then stops with `GATE_VERIFY_NOT_RUN` directing `devkit sync`), bundle gates, `get-context`, `playbook search`, workflow assets.

   Both run with stdin closed, in a session of their own: a timeout kills the whole process group (the shell and what it started, such as `uv sync`). Their output is discarded unless they fail; a failure or timeout is a `WORKTREE_SETUP_FAILED` or `WORKTREE_SYNC_FAILED` warning, and the worktree stays. The setup warning's `[FIX]` reruns the command. The sync runs with `--format json`, so its warning carries the sync's own error: the code and message (`RECEIPT_STALE`, `SELECTION_INVALID`, ...), its targets under the worktree, its `[DETAIL]` lines and its `[FIX]`, prefixed with the worktree path, since rerunning does not cure a stale receipt or a missing package; only an output that is not an error object (a timeout, a crash) gets the rerun command, with the advisory headlines kept ahead of the last lines. A reused worktree runs neither.

The commit gates of `devkit gate` are shared by every worktree and run with the worktree's own `.venv` first ([Commit Gate Overview](../gate/overview.md)), so a worktree without one falls back to the interpreter recorded at installation.

The command ends with `[NEXT_CMD: cd <path>]`: the task continues in the worktree.

## 3. finish

`finish` runs in the base checkout (`WORKTREE_RUN_FROM_BASE` otherwise) and finds the worktree by its path, else its branch. It removes only a linked worktree on the slug's branch, because it judges the merge by that branch alone:

- a worktree at the slug's path that is detached or on another branch would take commits the branch does not hold with it: `WORKTREE_CONFLICT`, whose `[FIX]` is to check out the slug's branch there with those commits on it;
- a slug whose branch is the base checkout's own (`finish main` in a base on `main`): `WORKTREE_CONFLICT`;
- a locked worktree (`git worktree lock`): `WORKTREE_LOCKED`, whose `[FIX]` is `git worktree unlock <path>` once the user agrees;
- neither a worktree nor a branch merged into the base HEAD: `WORKTREE_NOT_FOUND`;
- no worktree, and a merged branch of the slug's name without the marker (`start` did not create it, such as a `release` or the base's own `main` branch, a `finish` already completed for it, or `start` created it before devkit recorded the marker: such branches are not resumed automatically): `WORKTREE_NOT_FOUND`, nothing changed, whatever `delete_branch` says. No caller cleanup, merge or push runs for such a branch, and `finish` never deletes it itself: with `delete_branch = true` the `[FIX]` is `git branch -d <slug>` once the user agrees; with `delete_branch = false` it says that nothing is left to finish.

These checks, and those of step 1, run before the first change, so each of their refusals leaves the repository as it was; only uncommitted changes in the worktree surface later, at step 3:

1. **Integrate.**
   - With `--merge`: refused under `[worktree] pull_request = true` (`WORKTREE_PR_POLICY`; the default is `false`). The base must be on a branch (`WORKTREE_BASE_DETACHED`: a fast-forward of a detached HEAD moves no branch and pushes nothing, so the task's commits would end up on no branch) and clean (`WORKTREE_BASE_DIRTY`). When the base branch has a configured upstream (`branch.<base>.remote` and `.merge`), its remote ref is fetched first (never prompting, within 120 seconds); a fetched tip the base does not contain is `WORKTREE_BASE_BEHIND`, whose `[FIX]` is `git pull --ff-only` of it. A fetch that fails (offline, an unreachable remote, a remote ref that does not exist yet) skips this check: the push below reports what remains. `git merge --ff-only <slug>` then fast-forwards the base (`WORKTREE_MERGE_NOT_FF` when the base moved on: integrate the base into the branch first), and the base branch is pushed to that upstream (an explicit refspec, never forced, never prompting, within 120 seconds). A base branch without an upstream is not pushed (`push=no-upstream`). A push the upstream rejects because it moved on since the fetch is a `WORKTREE_PUSH_REJECTED` warning (`push=rejected`) whose `[FIX]` integrates the upstream into the base (`git pull --rebase`) and then pushes; any other failed push is a `WORKTREE_PUSH_FAILED` warning (`push=failed`) whose `[FIX]` is the push to rerun. Either way the cleanup continues.
   - Without `--merge`: the branch must already be an ancestor of the base HEAD (`WORKTREE_UNMERGED` otherwise, with nothing changed), the same test `status` reports as `merged`. A pull request merged by squash or rebase leaves the branch unmerged in this sense; remove that worktree and branch only with the user's authorization.

   Before either, when the branch will be deleted (step 4), its upstream, if it has one that exists locally, must contain it: `git branch -d` checks a branch against its upstream rather than the base, so a task branch pushed with `-u` and committed to since would be refused after the merge. That is `WORKTREE_BRANCH_UNPUSHED`, whose `[FIX]` pushes the branch to its upstream.
2. **Caller cleanup.** The library's `before_remove(result)` callback runs here, once the merge is confirmed and while the worktree still exists (it runs again on a rerun, so it must be idempotent). An `AdvisoryError` it raises reaches the library caller with the partial result as `error.result`, like the refusals below.
3. **Remove** the worktree with `git worktree remove`, within 1800 seconds. A worktree with uncommitted or untracked changes is `WORKTREE_DIRTY`: it is never removed by force. Any other failure is `WORKTREE_REMOVE_FAILED`; after a timeout the directory may be partly deleted while still registered (a rerun would report the deleted files as uncommitted changes), so its `[FIX]` is `git worktree remove --force <path>` once the user agrees.
4. **Delete the branch** with `git branch -d` (never `-D`) when `[worktree] delete_branch = true` (the default), which removes the marker with it. A failure is `WORKTREE_BRANCH_DELETE_FAILED`. With `delete_branch = false` the branch stays and only its marker is unset (`git config --unset-all`), so a rerun after a completed finish is `WORKTREE_NOT_FOUND`, as it is once the branch is deleted; a failure to unset it is `GIT_FAILED` with the partial result, and the rerun resumes and unsets it.

A refusal raised after step 1 carries the partial result: the command prints its `[WORKTREE_FINISHED: ...]` line (or, under `--format json`, the result with the error under `errors`) and the warnings collected so far (`WORKTREE_PUSH_FAILED`, `WORKTREE_PUSH_REJECTED`) before the error, so the caller sees what is already done.

**Post-finish extensions.** After a successful `finish` (never after a refusal), the command calls every `devkit.post_finish`
entry point of the installed packages, in sorted name order, as `extension(base, result)`: the base checkout's root (its repository root, which is also its devkit root) and the
result as its JSON object (`slug`, `path`, `branch`, `merged`, `push`, `removed`, `branch_deleted`). A package cleans
up what it keeps per task there (`devkit spec` prunes the handed-off proposal's directories and the task's scope
record). An extension returns `None` or a list: a string becomes a `POST_FINISH_NOTICE` notice, an advisory keeps its code
(an `ERROR` lowered to `WARNING`). It cannot fail the finish: an advisory it raises keeps its code the same way, with an
`extension: <name>` detail; any other exception or a malformed return value is a `POST_FINISH_EXTENSION_FAILED` warning. The extensions run in the CLI; the library's `finish` runs none (`before_remove` is
its callback). The rules are those of the `devkit.post_sync` extensions (`devkit.core.extensions`).

Rerunning the same command resumes once the cause is resolved:

- an already merged branch passes step 1 without `--merge` (with `--merge` the fast-forward is a no-op and the push runs again);
- when the worktree is already gone and the slug's branch remains merged into the base HEAD and carries the marker (what a stopped run leaves, or a worktree removed by hand), `finish` skips step 3, reports `removed=yes` and runs step 4 (deleting the branch, or with `delete_branch = false` unsetting its marker). A slug whose marked branch is merged and has no worktree is therefore finished by step 4 alone, whatever `delete_branch` says. The marker gates only this path: a slug whose worktree exists finishes whether or not its branch carries the marker (a branch created before devkit recorded it).

## 4. status

`status` lists every worktree (path, branch, short HEAD, base or linked, merged into the base HEAD, dirty, prunable) and every local branch that no worktree checks out and the base HEAD does not contain. It changes nothing and exits `0`: unmerged and dirty worktrees are ordinary while tasks run. A worktree on a branch without commits yet (`git switch --orphan`) is `merged=no`.

- A linked worktree with `merged=yes dirty=no` is cleaned up by `devkit worktree finish <slug>`.
- `merged=no`, `dirty=yes`, `dirty=-` (unreadable), `prunable=yes` (its directory was deleted; `git worktree prune` forgets it) and `[BRANCH: ...]` lines are removed only with the user's authorization.

## 5. Configuration

```toml
[worktree]
pull_request = false    # default; true integrates through pull requests and refuses `finish --merge`
delete_branch = true    # finish deletes the merged branch
setup = "uv sync"       # run in each new worktree (default: none)
```

The table is read from the devkit project containing the directory a command runs in (`-w`, else the current directory). An unknown key or a wrong type is `WORKTREE_CONFIG_INVALID`.

## 6. Module Layout

`devkit.worktree` imports only `devkit.core` and `devkit.advisory`; Git runs through `devkit.core.git.run_git`.

- `extensions.py`: the `devkit.post_finish` extension point (`run_post_finish`), on `devkit.core.extensions`.
- `lifecycle.py`: `locate`, `path_for`, `start`, `find`, `finish`, `status` and their results. `start` runs `devkit sync --locked` as a subprocess (`python -m devkit sync --locked`), so the module still imports no other area.
- `config.py`: `WorktreeConfig`, `read_worktree_config`.
- `errors.py`: one class per code ([reference](reference.md#error-codes)).
- `cli.py`: `devkit worktree start|finish|status`.

The lifecycle was ported from specrig's `worktree` package. the scope registry, its journal and the proposal-directory cleanup are methodology and live in devkit-spec, attached through the `devkit.post_finish` extension point; its `git.worktree` policy (which tasks run in a worktree) is methodology and stays there too.
