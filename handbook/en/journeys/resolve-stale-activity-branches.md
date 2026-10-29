---
sources:
  CAP-GOV-evaluation-lifecycle: 3e13fc27305e7933a1876ea9879a7423b5a771e0
  CAP-HARN-agent-guidance: 3e6c66d7ea068a580cc1ee82308708d407dab6bd
  CAP-WT-task-worktrees: 2ea80d46ab9cf19504182e73b6f2bcc301e8f7db
  UC-resolve-stale-activity-branches: b19fb4071f1680f2fa080aab2b6f4b7a7d22741c
title: Resolve stale activity branches
---

# Resolve stale activity branches

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `18b834c35c0c`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](adopt-sdd-from-incubation.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](incubate-an-idea.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
- [Speed up selected slow operations](speed-up-selected-slow-operations.md)
- [Advisories](../areas/advisory.md)
- [Agent-first CLI toolkit](../areas/cli.md)
- [Collaboration](../areas/collaboration.md)
- [Compact command output](../areas/compact.md)
- [Delivery](../areas/delivery.md)
- [Distribution](../areas/distribution.md)
- [Documents](../areas/documents.md)
- [Commit gates](../areas/gate.md)
- [Generated Files](../areas/generated.md)
- [Governance rules](../areas/governance.md)
- [Harness](../areas/harness.md)
- [Host](../areas/host.md)
- [Integration](../areas/integration.md)
- [MCP](../areas/mcp.md)
- [Search](../areas/search.md)
- [Traceability](../areas/traceability.md)
- [Viewer](../areas/viewer.md)
- [Worktree](../areas/worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

Every Planning task runs on a `plan-<slug>` branch and every Development task on a `dev-<slug>` branch. Nothing
expires them: a branch nobody moves simply stays "in progress". This journey shows how your agent finds the ones idle
longer than your project allows and brings each to your decision: resume it, discard it, or keep it. devkit deletes
nothing on its own.

For activity branches and task worktrees, see [Concepts](../concepts.md) and the [worktree area](../areas/worktree.md).

Source: [`UC-resolve-stale-activity-branches`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/delivery/UC-resolve-stale-activity-branches.md),
contract [`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/worktree/CAP-WT-task-worktrees.md)
(section "Stale Branches").

## Before you start

- `devkit-agt` is installed and you work from the base checkout.
- Branches made elsewhere are fetched (`git fetch`): devkit fetches nothing.
- The GitHub CLI is logged in (`gh auth status`), because last activity includes pull request updates.
- The threshold is `[worktree] stale_after` in `.devkit/config.toml`, `"<N>d"` or `"<N>w"`, default `"14d"`.

## Step by step

1. **Run the report**, on its own or as part of a whole-workspace hygiene check:

   ```sh
   uv run devkit worktree status --stale
   uv run devkit rules check -p hygiene     # same warnings, via the worktree-stale extension
   ```

   The `feedback-hygiene` playbook runs it too. Hygiene extensions belong to the `hygiene` phase
   ([`CAP-GOV-evaluation-lifecycle`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md),
   [governance area](../areas/governance.md)).
2. **Read the result.** Each `plan-*` or `dev-*` branch, local or remote-tracking, whose last activity (the later of its
   last commit and its pull request's last update) is older than `stale_after` gets a line, most idle first:

   ```text
   [STALE_BRANCH: dev-<slug> unit=... last_activity=... pr=open refs=local,origin]
   [SUMMARY: checked=yes branches=... stale=1 stale_after=14d]
   ```

   Each one is also a `WORKTREE_STALE_BRANCH` warning whose `[REPORT]` asks you whether to resume or discard it. Its
   `[FIX]` is the exact resume command when the branch's unit is recorded, and a `[DETAIL]` names the discard
   commands. The report changes nothing.
3. **Decide.** The agent tells you about each stale branch with both paths and takes neither unasked.
4. **To discard:** the agent first closes the branch's open pull request and deletes its remote copies (devkit leaves
   those to the caller), then, from the base checkout:

   ```sh
   uv run devkit worktree finish dev-<slug> --discard
   ```

   This removes the worktree, deletes the unmerged branch and prints `[WORKTREE_FINISHED: ...]` with
   `merged=no discarded=yes`.
5. **To resume:** the agent runs the command the warning's `[FIX]` names, for example

   ```sh
   uv run devkit worktree start plan-<slug> --existing-branch plan-<slug> --unit docs/proposals/PROP-<slug>
   ```

   The branch gets its worktree with nothing reset or rewritten, and work continues from the stage
   `devkit workflow next --unit <dir>` names.
6. **To keep:** do nothing. The next report warns about the branch again.

## When it goes wrong

- **No warnings in a commit or CI run.** Expected: the commit gate, CI and runs with explicit targets use the `linter`
  phase and never judge branches. Run the hygiene check over the whole workspace.
- **`WORKTREE_CONFIG_INVALID`.** `stale_after` is not `<N>d` or `<N>w` (for example `"2 weeks"`). The report refuses;
  in a hygiene run the extension shows as `HYGIENE_EXTENSION_FAILED` without failing the run. Fix the value.
- **`WORKTREE_STALE_SKIPPED` notice, `checked=no`.** `gh` is missing or logged out, so nothing was judged. Log in and
  rerun. This is not a failure.
- **`pr=unknown`.** `gh pr list` failed; branches were judged by their last commit alone. A repository with a GitHub
  remote also gets a `WORKTREE_STALE_PR_UNKNOWN` notice; one without a GitHub remote, where the lookup fails on every
  run, only logs it.
- **The branch carries an accepted proposal still in the base.** Discarding it is a close: you decide supersede or
  abandon, the agent commits the close (for an abandon, the rejection ADR and the deletion of the accepted proposal) to the base as Backlog
  work, and only then discards the branch
  ([`CAP-HARN-agent-guidance`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/harness/CAP-HARN-agent-guidance.md)).
- **The branch exists only on a remote.** The `[FIX]` names `git -C <base> push origin --delete dev-<slug>` and no
  local discard; once the remote copy is gone nothing is left.
- **`WORKTREE_DIRTY`.** The worktree has uncommitted or untracked changes. devkit checks this before any change and
  never removes the worktree by force; you decide what happens to the changes, then rerun.
- **`WORKTREE_BASE_ON_BRANCH`.** The branch was started with `--no-worktree` and the base checkout is still on it. Its
  `[FIX]` switches the base back to the branch it started from; rerun.
- **`WORKTREE_LOCKED`.** The worktree is locked. Its `[FIX]` is `git worktree unlock <path>`, run only once you agree.

## What you end up with

Each branch you decided on is either resumed in its worktree with its unit intact, or gone together with its pull
request, remote copies and worktree. A branch you keep stays as it was. A refused discard deletes nothing.
