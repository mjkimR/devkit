# Task Worktrees: Overview

`devkit.worktree` gives each task its own Git worktree and turns the end of the task into one deterministic command. A task named by a slug runs in `<parent of base>/<base name>-wt-<slug>` on branch `<slug>`; `finish` integrates the branch into the base checkout, removes the worktree and deletes the branch. Every step refuses instead of forcing, and rerunning the same command resumes where it stopped. Quick reference: [reference.md](reference.md).

The module is SDD-agnostic: it does not decide which tasks use a worktree, and it knows no document layout. A methodology layer (specrig) decides when a task gets a worktree, adds its own cleanup through the library's `before_remove` hook, and keeps any scope registry of its own.

## 1. Checkouts and Paths

- **Base checkout**: the work tree whose `.git` directory is the repository's common Git directory. `start` and `finish` run there; `status` runs from any checkout. A bare repository, or a Git directory outside its work tree (`--separate-git-dir`, submodules), is `WORKTREE_UNSUPPORTED_LAYOUT`.
- **Task worktree**: `<parent of base>/<base name>-wt-<slug>` on branch `<slug>`, created from the base HEAD. The rule is fixed so every session and agent computes the same path.
- **Slug**: lowercase letters, digits, `-` and `_`, starting with a letter or digit, 64 characters at most; anything else is `ARGUMENT_INVALID`. A caller turns its own names (a proposal id, a ticket) into a slug before calling.

## 2. start

1. Refuse inside a linked worktree (`WORKTREE_NESTED`): worktrees are not nested.
2. If the slug's path is already a worktree on the slug's branch and clean, reuse it (`created=no`). On another branch, or with uncommitted changes, it is `WORKTREE_CONFLICT`.
3. A branch named after the slug that is checked out elsewhere, or that already exists, is `WORKTREE_BRANCH_EXISTS`; a path that exists but is not a worktree is `WORKTREE_CONFLICT`.
4. Otherwise `git worktree add -b <slug> <path>` from the base HEAD. Uncommitted changes in the base stay in the base.
5. A new worktree is a fresh checkout without the base's ignored files: no `.venv`, no build output, and no `.devkit/managed/`, the synchronized copies that `.devkit/.gitignore` keeps out of Git. Two steps restore what work and commits need:
   1. **setup**: the `[worktree] setup` command, if configured, runs through `/bin/sh -c` in the worktree, without the caller's `VIRTUAL_ENV`, within 900 seconds. Set it to the project's environment step, for example `uv sync` or `just init`.
   2. **sync**: when the devkit project the command runs in has a receipt (`.devkit/installation.json`), `devkit sync` runs in the same project directory of the worktree, within 300 seconds, with the worktree's `.venv/bin/python` when setup created one, else the interpreter running `start`. It writes the ignored managed copies only: the receipt, `AGENTS.md` and the projected skills are tracked and already match. Without it, every devkit command that reads managed files fails in the worktree: bundle rules (and so a `devkit rules check --staged` commit gate, which then stops with `GATE_VERIFY_NOT_RUN` directing `devkit sync`), bundle gates, `get-context`, `playbook search`, workflow assets.

   Their output is discarded unless they fail; a failure or timeout is a `WORKTREE_SETUP_FAILED` or `WORKTREE_SYNC_FAILED` warning whose `[FIX]` reruns the step, and the worktree stays. A reused worktree runs neither.

The commit gates of `devkit gate` are shared by every worktree and run with the worktree's own `.venv` first ([Commit Gate Overview](../gate/overview.md)), so a worktree without one falls back to the interpreter recorded at installation.

The command ends with `[NEXT_CMD: cd <path>]`: the task continues in the worktree.

## 3. finish

`finish` runs in the base checkout (`WORKTREE_RUN_FROM_BASE` otherwise) and finds the worktree by its path or its branch (`WORKTREE_NOT_FOUND`).

1. **Integrate.**
   - With `--merge`: refused under `[worktree] pull_request = true` (`WORKTREE_PR_POLICY`, the default). The base must be clean (`WORKTREE_BASE_DIRTY`); `git merge --ff-only <slug>` fast-forwards it (`WORKTREE_MERGE_NOT_FF` when the base moved on: integrate the base into the branch first). The base branch is then pushed to its configured upstream (`branch.<base>.remote` and `.merge`, an explicit refspec, never forced, never prompting, within 120 seconds). A base branch without an upstream, or on a detached HEAD, is not pushed (`push=no-upstream`). A failed push is a `WORKTREE_PUSH_FAILED` warning whose `[FIX]` is the push to rerun; the cleanup continues.
   - Without `--merge`: the branch must already be an ancestor of the base HEAD (`WORKTREE_UNMERGED` otherwise, with nothing changed). A pull request merged by squash or rebase leaves the branch unmerged in this sense; remove that worktree and branch only with the user's authorization.
2. **Caller cleanup.** The library's `before_remove(result)` hook runs here, once the merge is confirmed and while the worktree still exists.
3. **Remove** the worktree with `git worktree remove`. A worktree with uncommitted or untracked changes is `WORKTREE_DIRTY`: it is never removed by force.
4. **Delete the branch** with `git branch -d` (never `-D`) when `[worktree] delete_branch = true` (the default).

A refusal raised after step 1 changed something carries the partial result: the command prints its `[WORKTREE_FINISHED: ...]` line (or, under `--format json`, the result with the error under `errors`) before the error, so the caller sees what is already done. Rerunning resumes: an already merged branch passes step 1 without `--merge`.

## 4. status

`status` lists every worktree (path, branch, short HEAD, base or linked, merged into the base HEAD, dirty, prunable) and every local branch that no worktree checks out and the base HEAD does not contain. It changes nothing and exits `0`: unmerged and dirty worktrees are ordinary while tasks run.

- A linked worktree with `merged=yes dirty=no` is cleaned up by `devkit worktree finish <slug>`.
- `merged=no`, `dirty=yes`, `dirty=-` (unreadable), `prunable=yes` (its directory was deleted; `git worktree prune` forgets it) and `[BRANCH: ...]` lines are removed only with the user's authorization.

## 5. Configuration

```toml
[worktree]
pull_request = true     # integrate through pull requests: `finish --merge` is refused
delete_branch = true    # finish deletes the merged branch
setup = "uv sync"       # run in each new worktree (default: none)
```

The table is read from the devkit project containing the directory a command runs in (`-w`, else the current directory). An unknown key or a wrong type is `WORKTREE_CONFIG_INVALID`.

## 6. Module Layout

`devkit.worktree` imports only `devkit.core` and `devkit.advisory`; Git runs through `devkit.core.git.run_git`.

- `lifecycle.py`: `locate`, `path_for`, `start`, `find`, `finish`, `status` and their results. `start` runs `devkit sync` as a subprocess (`python -m devkit sync`), so the module still imports no other area.
- `config.py`: `WorktreeConfig`, `read_worktree_config`.
- `errors.py`: one class per code ([reference](reference.md#error-codes)).
- `cli.py`: `devkit worktree start|finish|status`.

The lifecycle was ported from specrig's `worktree` package. specrig's scope registry, its journal and the proposal-directory cleanup stay in specrig, attached through `before_remove`; its `git.worktree` policy (which tasks run in a worktree) is methodology and stays there too.
