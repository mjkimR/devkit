---
sources:
  CAP-GATE-commit-gates: 83c1bd822d3330dab5eed84e7b8f13a552e5f638
  CAP-INT-mcp-services: 41636553f0fe6331719d5d0cfaad2965deda6eb1
  CAP-MCP-runtime-registration: 6dd9d3d5cf7a915a18d80f1adae375cf73823c1a
  CAP-WT-task-worktrees: a885013edf5dd548ffad4e9140c4b32b01b16ce2
  UC-drive-development-to-integration: bc214c7d80b401cf5b2ba5027c9144673d104393
  UC-handle-delivery-problems-and-exceptions: 3bd25e04ea70fadeefdc4a324a9780da89013610
  UC-resolve-stale-activity-branches: b19fb4071f1680f2fa080aab2b6f4b7a7d22741c
  UC-route-development-intent: 50d6278b292da8b936bc1bd6587bde501f490ee6
  UC-run-parallel-work-safely: eb22803d64e8af4f3479c6c935942508db14f5cf
title: Worktree
---

# Worktree

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `5e71d74c8e5a`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Collaboration](collaboration.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
- [Host](host.md)
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

`devkit worktree` gives each activity of a task its own branch and, when the task needs one, its own Git worktree, and
turns the end of the task into one deterministic command (`CAP-WT-task-worktrees`). Every step refuses instead of
forcing, and rerunning the same command resumes where it stopped. Which tasks get a worktree is decided by the
methodology layer (devkit-spec and its Git policy), not by this module. See [Concepts](../concepts.md) for activities,
units and integration.

## Names and places

- **Activity branch**: `plan-<slug>` for Planning, `dev-<slug>` for Development. The slug is lowercase letters,
  digits, `-` and `_`; the whole name is at most 64 characters. Commands always take the whole branch name.
- **Task worktree**: `<parent of base>/<base name>-wt-<branch>`, for example `devkit-wt-dev-login` next to `devkit`.
  The path is fixed so every session and agent computes the same one.
- **Base checkout**: the main work tree. `start` and `finish` run there; `status` runs anywhere.
- **Marker**: `start` records `branch.<branch>.devkitWorktree` in the shared Git configuration, which tells a task
  branch from an unrelated branch of the same name.

## Start a task

```sh
devkit worktree start dev-login
```

devkit refuses a branch that already exists locally or on any reachable remote (`WORKTREE_BRANCH_EXISTS`), refuses
nesting inside a linked worktree (`WORKTREE_NESTED`), then creates the worktree from the base HEAD. A fresh checkout
lacks the base's ignored files, so `start` also:

1. copies your `.devkit/config.local.toml`, if any, as a snapshot (later edits on either side do not propagate);
2. runs `[worktree] setup` (for example `uv sync`) in the worktree;
3. runs `devkit sync --locked` to restore the managed bundle copies that rules, gates, `get-context` and playbooks
   need, then `devkit sync --registrations-only` for the optional MCP entry (`CAP-MCP-runtime-registration`).

A failing setup or sync is a warning (`WORKTREE_SETUP_FAILED`, `WORKTREE_SYNC_FAILED`) with its fix, and the worktree
stays. The command ends with `[NEXT_CMD: cd <path>]`. Commit gates run with the worktree's own `.venv` first
(`CAP-GATE-commit-gates`).

Two variants:

- `devkit worktree start dev-login --no-worktree` creates the branch in the current checkout and carries your
  uncommitted changes over. No setup runs. Every session using that directory sees the switch, so it gives no
  isolation between concurrent sessions.
- `devkit worktree start dev-login --existing-branch [<remote>/]dev-login --unit <dir>` continues a branch that was
  started elsewhere: another checkout, another machine, a cloud run. Nothing is reset. devkit fetches nothing, so
  fetch first; a local copy that is behind or diverged is `WORKTREE_BRANCH_OUT_OF_SYNC`, and installed attach checks
  confirm the unit belongs to the branch (`WORKTREE_ATTACH_REFUSED`).

How the workflow chooses between these is part of the journey
[Route development intent](../journeys/route-development-intent.md) (`UC-route-development-intent`). Parallel tasks
in separate worktrees can compare their scopes through the shared registry, see
[Run parallel work safely](../journeys/run-parallel-work-safely.md) (`UC-run-parallel-work-safely`) and
[Collaboration](collaboration.md).

## Finish a task

In the Host-driven workflow, integration goes through `devkit integration` (see [Integration](integration.md),
`CAP-INT-mcp-services`), which uses the same merge and cleanup machinery after your decision or under `auto` policy.
The underlying command is:

```sh
devkit worktree finish dev-login --merge [--local-only]
```

It runs in the base checkout and, in order:

1. **Integrates.** The base must be on a branch and clean, and the task branch must already contain the base HEAD
   (`WORKTREE_MERGE_NOT_FF`: merge the base into the branch, never rebase, since records cite commit SHAs). Installed
   finish guards run; devkit-agt refuses a branch whose units hold an unresolved problem or unanswered question
   (`WORKTREE_BLOCKED`). The base then lands the branch as a merge commit built outside any checkout (or a
   fast-forward under `merge = "ff-only"`) and pushes to its upstream unless `--local-only`.
2. **Removes** the worktree. Uncommitted or untracked changes stop it (`WORKTREE_DIRTY`); it is never removed by
   force.
3. **Deletes** the branch with `git branch -d` (unless `delete_branch = false`).
4. Runs post-finish extensions, such as devkit-spec's cleanup of the scope record and handed-off proposal.

Without `--merge`, `finish` only cleans up a branch that is already merged. A pull request merged by squash or rebase
leaves the branch unmerged in Git's sense; remove that one only with your authorization.

To drop a task without integrating it (an abandon, a supersede, a depth escalation), use
`devkit worktree finish dev-login --discard`. It removes a clean worktree and deletes the branch with `git branch -D`;
remote branches and pull requests stay yours to close.

A refusal after the merge step prints what was already done. Fix the cause and rerun the same command. Recovery for
blocked or interrupted delivery is covered in
[Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
(`UC-handle-delivery-problems-and-exceptions`); the full flow to landing is
[Drive development to integration](../journeys/drive-development-to-integration.md)
(`UC-drive-development-to-integration`).

## See what is open

`devkit worktree status` lists every worktree (branch, HEAD, merged, dirty, prunable) and every unmerged local branch
without a worktree. It changes nothing. A linked worktree with `merged=yes dirty=no` is cleaned up with
`devkit worktree finish <branch>`; anything unmerged, dirty or prunable is removed only when you decide.

### Stale branches

Nothing expires an activity branch. `devkit worktree status --stale` reports `plan-*` and `dev-*` branches, local and
remote-tracking, idle longer than `[worktree] stale_after` (default 14 days), judged by the last commit and the last
pull request update. It needs an authenticated `gh`; without it you get a `WORKTREE_STALE_SKIPPED` notice. Each
stale branch is a `WORKTREE_STALE_BRANCH` warning whose fix names the resume command and the discard commands, and the
same report appears in `devkit rules check --phase hygiene`. Nothing is cleaned up automatically; the journey
[Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
(`UC-resolve-stale-activity-branches`) walks through the decision.

## Configure

```toml
[worktree]
pull_request = "auto"   # "required" refuses `finish --merge` and the local integration route
delete_branch = true    # finish deletes the merged branch
merge = "no-ff"         # or "ff-only"
setup = "uv sync"       # run in each new worktree (default: none)
stale_after = "14d"     # "<N>d" or "<N>w"
```

An invalid value is `WORKTREE_CONFIG_INVALID`.

## Extension points

Packages hook into the lifecycle through entry points: `devkit.attach_check` (verify branch and unit before attaching),
`devkit.finish_guard` (refuse to integrate) and `devkit.post_finish` (clean up after a successful finish). An extension
that misbehaves fails closed for checks and guards, and only warns after a finish.

## Sources

- [CAP-WT-task-worktrees](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md):
  paths, start variants, finish steps, status, configuration and stale branches.
- [Worktree quick reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/worktree.md):
  commands and error codes.
- Related: [Integration](integration.md), [Collaboration](collaboration.md).
