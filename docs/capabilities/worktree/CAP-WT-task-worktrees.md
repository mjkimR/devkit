---
id: CAP-WT-task-worktrees
title: "Task Worktrees"
summary: "Task worktree isolation, creation-time local preference snapshots, activity branches, merge gates, and stale checkout cleanup."
area: worktree
status: active
entrypoints:
  - packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py
  - packages/devkit/src/devkit_agt/features/worktree/services/merging.py
  - packages/devkit/src/devkit_agt/features/worktree/repositories/pull_request.py
created_at: 2026-10-17
stories:
  - US-drive-development-to-integration
---

# [CAP-WT-task-worktrees] Task Worktrees: Overview

`devkit_agt.features.worktree` gives each activity of a task its own branch, and that branch its own Git worktree when the task needs one, and turns the end of the task into one deterministic command. An activity runs on the branch `plan-<slug>` (Planning) or `dev-<slug>` (Development), in `<parent of base>/<base name>-wt-<branch>`; `finish` integrates the branch into the base checkout (by default as a merge commit built outside any checkout), removes the worktree and deletes the branch. A new branch is never started where one of that name exists, locally or on a remote: an existing branch is continued only through `start --existing-branch`. Every step refuses instead of forcing, and rerunning the same command resumes where it stopped. Quick reference: [reference.md](../../development/reference/worktree.md).

The module is SDD-agnostic: it does not decide which tasks use a worktree, and it knows no document layout. It owns the branch names, so every host and agent computes the same ones. A methodology layer (devkit-spec) decides when a task gets a worktree, adds its own cleanup through a `devkit.post_finish` extension (or the library's `before_remove` callback), verifies that a branch and a unit belong together through a `devkit.attach_check` extension, and keeps any scope registry of its own. `devkit_agt.features.workflow` refuses to integrate a branch whose units are blocked through a `devkit.finish_guard` extension.

## 1. Checkouts and Paths

- **Base checkout**: the work tree whose `.git` directory is the repository's common Git directory. `start` and `finish` run there; `status` runs from any checkout. A bare repository, or a Git directory outside its work tree (`--separate-git-dir`, submodules), is `WORKTREE_UNSUPPORTED_LAYOUT`.
- **Activity branch**: `<activity>-<slug>`, the activity `plan` (Planning) or `dev` (Development). The slug is lowercase letters, digits, `-` and `_`, starting with a letter or digit; the whole name is 64 characters at most. Every command takes the whole branch name (`devkit worktree start dev-login`); anything else is `ARGUMENT_INVALID`. A caller turns its own names (a proposal id, a ticket) into a slug before calling. Results carry the branch and its `slug`.
- **Task worktree**: `<parent of base>/<base name>-wt-<branch>` on that branch, created from the base HEAD. The rule is fixed so every session and agent computes the same path.
- **Marker**: every branch `start` creates or attaches carries `branch.<branch>.devkitWorktree = <worktree path>` in the repository's common Git configuration (`.git/config`, shared by all worktrees); a branch started without a worktree carries the checkout's path. It tells a task branch from an ordinary branch that happens to share the name, and only gates `finish` on a branch that has no worktree ([section 3](#3-finish)). Beside it, `devkitBase` records the branch `start --no-worktree` started from, and `devkitUnit` the unit `start --existing-branch` was given. They last until `finish` completes: `git branch -d` removes them with the branch (Git drops the branch's `branch.<name>` configuration section), and with `delete_branch = false` `finish` unsets the marker once the worktree is removed (step 4).

## 2. start

1. Refuse inside a linked worktree (`WORKTREE_NESTED`): worktrees are not nested.
2. If the branch's path is already a worktree on the branch, the branch exists: `WORKTREE_BRANCH_EXISTS`, whose `[FIX]` is the `--existing-branch` command that checks the branch and reuses that worktree ([section 2b](#2b-start---existing-branch)). A plain `start` never continues an existing branch, so two runs never land in the same worktree unchecked. On another branch it is `WORKTREE_CONFLICT`; so is a registered worktree whose directory was deleted (`prunable`), with `git worktree prune` as its `[FIX]`.
3. A branch that is checked out elsewhere or already exists locally is `WORKTREE_BRANCH_EXISTS`; a path that exists but is not a worktree is `WORKTREE_CONFLICT`. Then each configured remote is asked whether it has the branch (`git ls-remote --heads`, never prompting, within 30 seconds): a remote that has it is `WORKTREE_BRANCH_EXISTS` too. A remote that cannot be reached is judged by its remote-tracking ref from the last fetch (`refs/remotes/<remote>/<branch>`) and reported as a `WORKTREE_REMOTE_UNCHECKED` warning. Every `WORKTREE_BRANCH_EXISTS` names the `--existing-branch` command that continues the branch ([section 2b](#2b-start---existing-branch)). Two checkouts that start the same branch at the same moment, or a branch another machine has not pushed, are not detected.
4. Otherwise `git worktree add -b <branch> <path>` from the base HEAD, within 1800 seconds (a large checkout, LFS or slow hooks take long), then `git config --local branch.<branch>.devkitWorktree <path>`, the marker ([section 1](#1-checkouts-and-paths)). Uncommitted changes in the base stay in the base. `git worktree add` and `git worktree remove` run in a session of their own, so a timeout kills the `post-checkout` hook and checkout filters (Git LFS) with Git rather than leaving them writing into a path the cleanup removes. When either step fails or times out (a failing `post-checkout` hook fails it too), `start` removes what it created, the registered worktree (with `--force --force`: Git locks a worktree while it checks it out) and the branch (with `git branch -d`, and only while it still points at the base HEAD it was created from; a branch a hook committed to is left), and raises `WORKTREE_ADD_FAILED` with Git's reason, so the rerun starts afresh; whatever it could not remove is listed as `left:` details, with the commands that remove it as the `[FIX]`. When another process creates the branch or the path between the checks of step 3 and Git, Git refuses with "already exists" and `start` removes nothing of it: a branch is `WORKTREE_BRANCH_EXISTS`; a path is `WORKTREE_CONFLICT`, once the branch Git created before refusing is removed.
5. A new worktree is a fresh checkout without the base's ignored files: no `.venv`, no build output, and no `.devkit/managed/`, the synchronized copies that `.devkit/.gitignore` keeps out of Git. Two steps restore what work and commits need:
   Before setup, validate and capture the caller project’s optional `.devkit/config.local.toml` in the retained base. Invalid input fails before checkout creation. After checkout, copy the complete bytes and mode to the corresponding project path. A missing source creates no local file. `WORKTREE_LOCAL_CONFIG_COPY_FAILED` retains the checkout, names source/destination and requires a deliberate manual copy before retrying setup; no setup or sync runs after that failure.
   1. **setup**: the `[worktree] setup` command, if configured, runs through `/bin/sh -c` in the worktree, without the caller's `VIRTUAL_ENV`, within 900 seconds. Set it to the project's environment step, for example `uv sync` or `just init`.
   2. **sync**: when the devkit project the command runs in has a receipt (`.devkit/installation.json`), `devkit sync --locked` runs in the same project directory of the worktree, within 300 seconds, with the worktree's `.venv/bin/python` when setup created one with devkit installed in it (a `devkit_agt-*.dist-info` in its `site-packages`, the test the commit gate hooks apply), else the interpreter running `start`. It writes the ignored managed copies only and never changes the tracked receipt, `AGENTS.md` or seeded files; when the worktree's environment no longer matches the committed receipt (a `RECEIPT_STALE` exit `1`) or lacks a deployed bundle's package, it fails and `start` reports `WORKTREE_SYNC_FAILED`. Without it, every devkit command that reads managed files fails in the worktree: bundle rules (and so the `rules-check` commit gate, which then stops with `RULES_RUN_FAILED` directing `devkit sync`), bundle gates, `get-context`, `playbook search`, workflow assets.

   After successful locked restoration, `devkit sync --registrations-only` initializes eligible local MCP entries
   using the same interpreter. Dist discovers the optional provider; no runtime import is added to worktree.
   Without the provider this is a no-op. Existing registration conflicts still refuse locked sync; absent fresh
   entries are initialized only in this separate step. Native handoff rechecks its environment before this step.
   Registration advisories are returned with the result and a failure keeps the created worktree. Trusted native
   handoff children carry a refusal-only identity constraint for the original owning workspace; sync checks it
   after locks and before each transaction write. No approval or terminal-cleanup authority crosses the process
   boundary. The parent rechecks the constraint after child completion.

   Setup, sync and registration initialization run with stdin closed, in a session of their own: a timeout kills the whole process group (the shell and what it started, such as `uv sync`). Their output is discarded unless they fail; a failure or timeout is a `WORKTREE_SETUP_FAILED` or `WORKTREE_SYNC_FAILED` warning, and the worktree stays. The setup warning's `[FIX]` reruns the command. The sync runs with `--format json`, so its warning carries the sync's own error: the code and message (`RECEIPT_STALE`, `SELECTION_INVALID`, ...), its targets under the worktree, its `[DETAIL]` lines and its `[FIX]`, prefixed with the worktree path, since rerunning does not cure a stale receipt or a missing package; only an output that is not an error object (a timeout, a crash) gets the rerun command, with the advisory headlines kept ahead of the last lines. A reused worktree runs neither and preserves its local file byte-for-byte, including intentional absence. Created worktrees own independent snapshots: later base/task edits or deletion do not propagate. Direct `git worktree add` and independent clones do not copy local configuration.

The commit gates of `devkit gate` are shared by every worktree and run with the worktree's own `.venv` first (`CAP-GATE-commit-gates`), so a worktree without one falls back to the interpreter recorded at installation.

The command ends with `[NEXT_CMD: cd <path>]`: the task continues in the worktree.

## 2a. start --no-worktree

`start <branch> --no-worktree` starts the activity branch in the current checkout instead, for a task that needs a branch but no separate directory: it creates the branch at the current HEAD and switches to it with `git switch -c`, which carries uncommitted changes over (work begun on the base continues on the branch). The name rule and the refusals of step 3 apply unchanged. It runs in the base checkout (`WORKTREE_NESTED` in a linked worktree, which `finish` would remove) on a branch (`WORKTREE_BASE_DETACHED` on a detached HEAD: nothing would say where the task integrates). The branch gets the marker, with the checkout's path, and `devkitBase`, the branch the checkout was on. No setup or sync runs: the checkout already has its environment. It prints `[BRANCH_STARTED: <branch> checkout=<path> from=<branch>]`.

Switching branches changes the branch seen by every session using that directory, so another session can commit
to the checked-out task branch. The direct user coordinates shared sessions; a separate worktree remains an option
for a direct session task. The local orchestration Host coordinates workers, which still run in their own
worktrees under `CAP-DLV-project-policy`. Shared-checkout use provides no isolation between concurrent sessions.

The branch is integrated by `finish` like a worktree's ([section 3](#3-finish)) once the base checkout is back on the branch it started from: `finish --merge` refuses from any other branch (`WORKTREE_CONFLICT`, whose `[FIX]` switches to the recorded `devkitBase`), since it would integrate the task into that branch instead. The finish result's `path` is the checkout the branch was started in, where a `devkit.post_finish` extension finds what it registered for the task.

## 2b. start --existing-branch

`start <branch> --existing-branch <branch|remote/branch> --unit <dir>` gives an existing activity branch its worktree, so a task stopped or started elsewhere (a branch prepared in the base checkout, a run on another machine, a pull request opened in the cloud) continues in this checkout. Nothing in the branch is reset or rewritten: the unit and its records continue where they stopped. It is the only path that takes an existing branch; `start` without it keeps refusing one. The checks run before the first change:

1. `--existing-branch` is the branch itself, or `<remote>/<branch>` with a configured remote (`ARGUMENT_INVALID` otherwise), and `--unit` goes with it.
2. The branch exists locally or as a fetched remote-tracking ref (`refs/remotes/<remote>/<branch>`); devkit fetches nothing, so fetch first to see a branch made elsewhere (`WORKTREE_NOT_FOUND` otherwise, whose `[FIX]` is the fetch). The remote compared with is the one named, else the local branch's upstream, else the one remote whose fetched ref has the branch (`ARGUMENT_INVALID` when several do), also for a local branch without an upstream (`start --no-worktree` sets none), so a copy that moved on elsewhere is never skipped. A named remote whose ref was never fetched while a local branch exists is `WORKTREE_NOT_FOUND` (its `[FIX]` is the fetch): comparing with nothing would attach a stale branch. A local branch that lacks commits of that remote branch (behind or diverged) is `WORKTREE_BRANCH_OUT_OF_SYNC`: devkit never merges or resets it, and the `[FIX]` fast-forwards a branch that is only behind. A local branch ahead of it is attached as it is, with a `WORKTREE_BRANCH_AHEAD` notice: the remote lacks its commits until they are pushed, and the `[FIX]` is that push.
3. `--unit`, relative to the devkit project (the directory a command runs in belongs to), is a directory of the branch's tree at its tip (`WORKTREE_UNIT_INVALID` otherwise).
4. Every `devkit.attach_check` entry point of the installed packages is called, in sorted name order, as `extension(root, branch, unit, tip)`: the base checkout's root, the branch, the unit relative to that root and the commit id the branch will be attached at, whose files the extension reads (`git show <tip>:<unit>/...`) since no worktree may exist yet. It returns `None` or a list of reasons; any reason refuses with `WORKTREE_ATTACH_REFUSED`, each reason a detail. An extension that raises or returns anything else refuses with `WORKTREE_ATTACH_CHECK_FAILED`: the correspondence was not verified. devkit-spec checks there that the unit's slug and bound workflow fit the branch's activity.
5. A registered worktree of the branch at its path is reused when it is clean (`created=no`); a missing or dirty one, or a path occupied otherwise, is `WORKTREE_CONFLICT`. The branch checked out in another worktree is `WORKTREE_BRANCH_EXISTS`. The branch checked out in the base checkout (`start --no-worktree`) must be clean there (`WORKTREE_CONFLICT`), and its `devkitBase` must be recorded (`WORKTREE_CONFLICT` whose `[FIX]` switches the base by hand otherwise).

Then, in order: the base checkout is switched back to its `devkitBase` when it was on the branch (it stays switched if a later step fails; the rerun finds it there); a remote-only branch gets a local branch tracking it (`git branch --track`); `git worktree add <path> <branch>` creates the worktree (a failure removes the worktree it created, never the branch, `WORKTREE_ADD_FAILED`), followed by the local-config copy, setup and sync of step 5; the marker and `devkitUnit` are recorded. The output is that of `start`, with `existing=yes unit=<dir>`.

## 3. finish

`--local-only` excludes fetch and push, including with `--merge`; local guards and safe cleanup remain active.
The library equivalent is `finish(..., network="forbid")` (`"allow"` preserves existing behavior). Successful local
merging reports `push=excluded`. Public `plan_finish` and `validate_finish` bind exact repository, ref and cleanup
identities (`plan_finish` records the merge method and whether the target already contains the branch; after the
merge `validate_finish` accepts a base that contains the result, so later commits on the base are allowed), and `before_step` validates each mutation boundary for the
`CAP-INT-mcp-services`. These APIs do not supply business approval.
Installed callbacks and native Git hooks must obey the local-only contract; this API is not a process sandbox.

`finish` runs in the base checkout (`WORKTREE_RUN_FROM_BASE` otherwise) and finds the worktree by its path, else its branch. It removes only a linked worktree on the branch, because it judges the merge by that branch alone:

- a worktree at the branch's path that is detached or on another branch would take commits the branch does not hold with it: `WORKTREE_CONFLICT`, whose `[FIX]` is to check out the branch there with those commits on it;
- a branch the base checkout itself is on: `WORKTREE_CONFLICT`; for a branch `start --no-worktree` created it is the routine `WORKTREE_BASE_ON_BRANCH` (`AUTO`), whose `[FIX]` switches the base back to its recorded `devkitBase` for a rerun;
- a locked worktree (`git worktree lock`): `WORKTREE_LOCKED`, whose `[FIX]` is `git worktree unlock <path>` once the user agrees;
- neither a worktree nor a branch: `WORKTREE_NOT_FOUND`;
- no worktree, and a branch without the marker (`start` did not create it, a `finish` already completed for it, or `start` created it before devkit recorded the marker: such branches are not resumed automatically): `WORKTREE_NOT_FOUND`, nothing changed, whatever `delete_branch` says. No caller cleanup, merge or push runs for such a branch, and `finish` never deletes it itself: when it is merged, with `delete_branch = true` the `[FIX]` is `git branch -d <branch>` once the user agrees; with `delete_branch = false` it says that nothing is left to finish.
- no worktree, and a marked branch: it is finished without a removal: `removed=yes` when its worktree was removed earlier (by hand, or by a stopped run), `removed=-` when it never had one (`start --no-worktree`). Without `--merge` it must be merged like any other (`WORKTREE_UNMERGED`).

These checks, and those of step 1, run before the first change, so each of their refusals leaves the repository as it was; only uncommitted changes in the worktree surface later, at step 3:

The local MCP executor may authorize these exact effects from shared base `dev-integration=auto`, without native elicitation, while preserving all dirty/locked/identity checks and selected branch retention (`CAP-INT-mcp-services`). This authority does not extend to the public CLI, remote operations, force cleanup or unrelated worktrees.

1. **Integrate.**
   - With `--merge`: refused under `[worktree] pull_request = "required"` (`WORKTREE_PR_POLICY`; the default `"auto"` allows it). The base must be on a branch (`WORKTREE_BASE_DETACHED`: a fast-forward of a detached HEAD moves no branch and pushes nothing, so the task's commits would end up on no branch) and clean (`WORKTREE_BASE_DIRTY`). Every `devkit.finish_guard` entry point of the installed packages is then called, in sorted name order, as `extension(base, branch, merge_base, tip)`: the base checkout's root, the branch, the commit id of its merge base with the base HEAD (empty when there is none) and of its tip. It returns `None` or a list of reasons; any reason refuses with `WORKTREE_BLOCKED`, each reason a detail, and nothing changed. An extension that raises or returns anything else refuses with `WORKTREE_GUARD_FAILED`: the branch was not verified. devkit-agt registers one: `devkit_agt.features.workflow` refuses a branch whose units hold an unresolved problem, an unanswered question or a malformed worker envelope (`CAP-DLV-workflow-envelopes`). The library's `finish` takes the same check as its `guard(merge_base, tip)` callback and runs no extension itself. When the base branch has a configured upstream (`branch.<base>.remote` and `.merge`), its remote ref is fetched first (never prompting, within 120 seconds); a fetched tip the base does not contain is `WORKTREE_BASE_BEHIND`, whose `[FIX]` is `git pull --ff-only` of it. A fetch that fails (offline, an unreachable remote, a remote ref that does not exist yet) skips this check: the push below reports what remains. Before the guards, the branch must contain the base HEAD (`WORKTREE_MERGE_NOT_FF` otherwise, whose `[FIX]` merges the base into the branch in its worktree with a message the commit-msg gate accepts and never rebases, since the task's records cite its commit SHAs), and under `[worktree] merge = "no-ff"` Git must have a committer identity (`WORKTREE_COMMIT_FAILED`). The command takes the Git common directory's devkit integration lock (`devkit-integration.lock`, shared with `CAP-INT-mcp-services`; `LOCK_HELD` while another integration holds it). The branch must still point at the commit the guard checked (`WORKTREE_CONFLICT` when a run committed to it meanwhile; rerun once it ends). Then the base lands it (`ADR-merge-commit-outside-checkout`): under `merge = "no-ff"` (the default) `merging.build_result` builds, in the object store, a merge commit whose first parent is the base HEAD, whose second is the checked tip, whose tree is the branch's tree and whose message is `chore(merge): integrate <branch> into <base branch>` (`git commit-tree`, signed when `commit.gpgSign` is on, within 30 seconds, `WORKTREE_COMMIT_FAILED` with nothing changed on failure), and `git merge --ff-only <that commit>` fast-forwards the base onto it, so the base checkout never stops mid-merge; under `merge = "ff-only"` it fast-forwards onto the tip. `"ff-only"` in the base's or the branch's committed policy wins. A branch the base already contains builds nothing. The base branch is then pushed to that upstream (an explicit refspec, never forced, never prompting, within 120 seconds). A base branch without an upstream is not pushed (`push=no-upstream`). A push the upstream rejects because it moved on since the fetch is a `WORKTREE_PUSH_REJECTED` warning (`push=rejected`) whose `[FIX]` fetches the upstream ref and merges it with `git merge --no-ff -m "chore(merge): integrate <remote>/<ref> into <base branch>" FETCH_HEAD`, then pushes: the task's commits keep their SHAs (`git pull --rebase`, and also `--rebase=merges`, would rewrite them), at the cost of the upstream's commits becoming the second parent of that merge, and a conflict leaves the base checkout mid-merge (`git merge --abort`). Any other failed push is a `WORKTREE_PUSH_FAILED` warning (`push=failed`) whose `[FIX]` is the push to rerun. Either way the cleanup continues.
   - Without `--merge`: the branch must already be an ancestor of the base HEAD (`WORKTREE_UNMERGED` otherwise, with nothing changed), the same test `status` reports as `merged`. A pull request merged by squash or rebase leaves the branch unmerged in this sense; remove that worktree and branch only with the user's authorization.

   Before either (and before the guards), when the branch will be deleted (step 4), its upstream, if it has one that exists locally, must contain it: `git branch -d` checks a branch against its upstream rather than the base, so a task branch pushed with `-u` and committed to since would be refused after the merge. That is `WORKTREE_BRANCH_UNPUSHED`, whose `[FIX]` pushes the branch to its upstream.
2. **Caller cleanup.** The library's `before_remove(result)` callback runs here, once the merge is confirmed and while the worktree still exists (it runs again on a rerun, so it must be idempotent). An `AdvisoryError` it raises reaches the library caller with the partial result as `error.result`, like the refusals below.
3. **Remove** the worktree with `git worktree remove`, within 1800 seconds. A worktree with uncommitted or untracked changes is `WORKTREE_DIRTY`: it is never removed by force. Any other failure is `WORKTREE_REMOVE_FAILED`; after a timeout the directory may be partly deleted while still registered (a rerun would report the deleted files as uncommitted changes), so its `[FIX]` is `git worktree remove --force <path>` once the user agrees.
4. **Delete the branch** with `git branch -d` (never `-D`) when `[worktree] delete_branch = true` (the default), which removes the marker with it. A failure is `WORKTREE_BRANCH_DELETE_FAILED`. With `delete_branch = false` the branch stays and only its marker is unset (`git config --unset-all`), so a rerun after a completed finish is `WORKTREE_NOT_FOUND`, as it is once the branch is deleted; a failure to unset it is `GIT_FAILED` with the partial result, and the rerun resumes and unsets it.

A refusal raised after step 1 carries the partial result: the command prints its `[WORKTREE_FINISHED: ...]` line (or, under `--format json`, the result with the error under `errors`) and the warnings collected so far (`WORKTREE_PUSH_FAILED`, `WORKTREE_PUSH_REJECTED`) before the error, so the caller sees what is already done.

**Post-finish extensions.** After a successful `finish` (never after a refusal), the command calls every `devkit.post_finish`
entry point of the installed packages, in sorted name order, as `extension(base, result)`: the base checkout's root (its repository root, which is also its devkit root) and the
result as its JSON object (`branch`, `slug`, `path`, `merged`, `push`, `removed`, `branch_deleted`). A package cleans
up what it keeps per task there (`devkit spec` prunes the handed-off proposal's directories and the task's scope
record). An extension returns `None` or a list: a string becomes a `POST_FINISH_NOTICE` notice, an advisory keeps its code
(an `ERROR` lowered to `WARNING`). It cannot fail the finish: an advisory it raises keeps its code the same way, with an
`extension: <name>` detail; any other exception or a malformed return value is a `POST_FINISH_EXTENSION_FAILED` warning. The extensions run in the CLI; the library's `finish` runs none (`before_remove` is
its callback). The rules are those of the `devkit.post_sync` extensions (`devkit_core.core.extensions`).

Rerunning the same command resumes once the cause is resolved:

- an already merged branch passes step 1 without `--merge` (with `--merge` nothing is built or merged and the push runs again);
- when the worktree is already gone and the branch remains merged into the base HEAD and carries the marker (what a stopped run leaves, or a worktree removed by hand), `finish` skips step 3, reports `removed=yes` and runs step 4 (deleting the branch, or with `delete_branch = false` unsetting its marker). A marked branch that is merged and has no worktree is therefore finished by step 4 alone, whatever `delete_branch` says. The marker gates only this path: a branch whose worktree exists finishes whether or not it carries the marker (a branch created before devkit recorded it).

## 3a. finish --discard

`finish <branch> --discard` closes a task without integrating it (a depth escalation, a supersede, an abandon): it drops the unmerged branch, on the authority the caller's close needs, and is the only path devkit offers for that. It runs in the base checkout and excludes `--merge` (`ARGUMENT_INVALID`). It finds the worktree as `finish` does (the same `WORKTREE_CONFLICT`, `WORKTREE_BASE_ON_BRANCH` and `WORKTREE_LOCKED` refusals, so the base checkout must not be on the branch), takes any activity branch, also one devkit did not start (another checkout, made by hand; its name says it is a task's), removes the worktree (`WORKTREE_DIRTY` with uncommitted or untracked changes: never by force) and deletes the branch with `git branch -D`. The `devkit.post_finish` extensions run as after `finish`, with `discarded: true` in the result, so a package releases what it kept for the task. Remote branches and pull requests are the caller's. The output is `[WORKTREE_FINISHED: ...]` with `merged=no discarded=yes`.

## 4. status

`status` lists every worktree (path, branch, short HEAD, base or linked, merged into the base HEAD, dirty, prunable) and every local branch that no worktree checks out and the base HEAD does not contain. It changes nothing and exits `0`: unmerged and dirty worktrees are ordinary while tasks run. A worktree on a branch without commits yet (`git switch --orphan`) is `merged=no`.

- A linked worktree with `merged=yes dirty=no` is cleaned up by `devkit worktree finish <branch>`.
- `merged=no`, `dirty=yes`, `dirty=-` (unreadable), `prunable=yes` (its directory was deleted; `git worktree prune` forgets it) and `[BRANCH: ...]` lines are removed only with the user's authorization.

## 5. Configuration

```toml
[worktree]
pull_request = "auto"   # default: a pull request or `finish --merge`, as the task needs; "required" refuses `--merge`
delete_branch = true    # finish deletes the merged branch
merge = "no-ff"         # default: each task lands as a merge commit; "ff-only": fast-forward only
setup = "uv sync"       # run in each new worktree (default: none)
stale_after = "14d"     # an activity branch idle this long is stale (default "14d"; "<N>d" or "<N>w")
```

The table is read from the devkit project containing the directory a command runs in (`-w`, else the current directory). An unknown key, a wrong type, a `pull_request` other than `"auto"` or `"required"`, a `merge` other than `"no-ff"` or `"ff-only"` or a `stale_after` other than `"<N>d"` or `"<N>w"` (`N` from 1 to 9999) is `WORKTREE_CONFIG_INVALID`. `pull_request` states whether integration must go through a pull request, not whether one is opened: the confirmed `pull-request` route in `CAP-INT-mcp-services` can push the task branch and open its PR. Under `"auto"` the caller chooses the route; `finish --merge` remains local and refuses required PR policy with a directive naming the native PR route.

## 6. Stale Branches

An activity branch nobody moves stays in progress: nothing expires it. `devkit worktree status` inspects local worktrees without querying GitHub. Its explicit `--stale` view instead reports the `plan-*` and `dev-*` branches, local and remote-tracking, whose last activity is older than `[worktree] stale_after` (default 14 days). The last activity is the later of the branch's last commit (over its local branch and every fetched remote copy) and the last update of its pull request, the latest one GitHub lists for that head branch (`gh pr list --state all`).

- **Condition**: it runs only when `gh auth status` succeeds. Without `gh`, or logged out, it judges nothing and reports a `WORKTREE_STALE_SKIPPED` notice, which is not a failure. When `gh pr list` fails (a repository GitHub does not know), branches are judged by their last commit alone (`WORKTREE_STALE_PR_UNKNOWN`, pull request state `unknown`).
- **Output**: per stale branch, most idle first, `[STALE_BRANCH: <branch> unit= last_activity= pr= refs=]`: the unit `start --existing-branch` recorded while the branch still holds it (`-` when none was, or when a handoff replaced it), the last activity (UTC), the pull request state (`none`, `draft`, `open`, `blocked` when GitHub reports its merge as blocked, `merged`, `closed` or `unknown`) and where the branch exists (`local` and remote names); then `[SUMMARY: checked= branches= stale= stale_after=]`. Each stale branch is also a `WORKTREE_STALE_BRANCH` warning whose `[FIX]` names the `start --existing-branch` command that resumes it and the commands that discard it once the user decides.
- **Hygiene**: devkit-agt registers the report as the `devkit.hygiene` extension `worktree-stale`, so a whole-workspace `devkit rules check --phase hygiene` shows the same warnings (`CAP-GOV-evaluation-lifecycle`). The commit gate and CI run the `linter` phase and never see it.
- Nothing is cleaned up: the report replaces no decision. Resume or discard a branch only as the user decides.

## 7. Module Layout

`devkit_agt.features.worktree` uses `devkit_core`, distribution project support and `devkit.advisory`; Git runs through `devkit_core.core.git.run_git`.

- `extensions.py`: the `devkit.post_finish` extension point (`run_post_finish`), on `devkit_core.core.extensions`, and the fail-closed check groups `devkit.finish_guard` (`run_finish_guards`) and `devkit.attach_check` (`run_attach_checks`).
- `lifecycle.py`: `locate`, `check_branch`, `path_for`, `start`, `start_branch`, `attach`, `find`, `finish`, `status` and their results.
- `stale.py`: `stale_branches` and the `devkit.hygiene` extension `hygiene`; `gh` runs through `run_gh`, which callers and tests can replace. `start` runs `devkit sync --locked` as a subprocess (`python -m devkit_dist sync --locked`), so the module still imports no other area.
- `merging.py`: the result commit (`build_result`, `merge_message`, `merge_method`, `check_identity`), `fast_forward` and the integration lock (`integration_lock`); with `advance=True` (the integration service only) it merges an advanced target with `git merge-tree --write-tree` (Git 2.38 or later, `WORKTREE_GIT_UNSUPPORTED`; a conflict is `WORKTREE_MERGE_CONFLICT`).
- `config.py`: `WorktreeConfig`, `read_worktree_config`.
- `errors.py`: one class per code ([reference](../../development/reference/worktree.md#error-codes)).
- `cli.py`: `devkit worktree start|finish|status|stale`.

The lifecycle was ported from specrig's `worktree` package. the scope registry, its journal and the proposal-directory cleanup are methodology and live in devkit-spec, attached through the `devkit.post_finish` extension point; its `git.worktree` policy (which tasks run in a worktree) is methodology and stays there too.


The library's `start(position, branch, ..., revision=COMMIT)` optionally pins the source commit. It resolves the
revision before remote branch checks and passes the resolved commit to `git worktree add`, so configured setup
runs from that commit even when another process advances the base meanwhile. Cleanup after failed creation uses
the pinned commit as its origin. Omitting `revision` preserves creation from the base's current HEAD. The local
MCP proposal handoff uses this option to keep setup bound to the reviewed commit.

Project MCP registration preserves worktree cleanliness: tracked host files and visible foreign untracked files
remain unchanged; generated entries and their ownership ledger remain ignored. Clone-local exclusions are narrowly
scoped and checked across linked worktrees before addition. MCP uses a retained interpreter/import source and base
executor, with the task checkout passed separately as its configuration workspace. Task cleanup cannot remove the
runtime. Configuration-workspace deletion blocks subsequent approval and resume, apart from exact same-call terminal
cleanup already approved; see `CAP-MCP-runtime-registration`.
