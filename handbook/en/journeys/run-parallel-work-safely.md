---
sources:
  CAP-COLL-work-scope-registry: e60ca6b5e8eccf19fac5b506233860376125ae9a
  CAP-DLV-project-policy: 7cec046a7324de8f46048c80dea6a4286bf809ef
  CAP-TRACE-code-entrypoints: 3b8cb1476d9102bf09e6ffc6a469c3e00e58da97
  CAP-WT-task-worktrees: a885013edf5dd548ffad4e9140c4b32b01b16ce2
  UC-run-parallel-work-safely: eb22803d64e8af4f3479c6c935942508db14f5cf
title: Run parallel work safely
---

# Run parallel work safely

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `5e71d74c8e5a`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
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

When you (or an orchestrating agent) run two or more proposals or spec bundles at once, the risk is that they touch
the same documents or code and collide at integration. devkit does not lock anything. Instead `devkit spec scope`
shows, before and during the work, which Living Spec documents and code paths the tasks share and how much of their
scope is still unknown, so you decide what runs in parallel and in which order it lands.

Task worktrees and activity branches are explained in [Concepts](../concepts.md); the registry itself in the
[collaboration area](../areas/collaboration.md).

Source: [`UC-run-parallel-work-safely`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/usecases/collaboration/UC-run-parallel-work-safely.md),
contract [`CAP-COLL-work-scope-registry`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md).

## Before you start

- The repository is a Git repository with `devkit-spec` installed.
- Each task declares its scope in its bundle: `target-docs.md` or `reconcile.md` targets, the `_Boundary` entries of
  `tasks.md`, and the `entrypoints` of the documents it targets. Entrypoints turn a document into code paths
  ([`CAP-TRACE-code-entrypoints`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md)).
  A `_Boundary` entry under `specs/` is skipped, except the exact path of another spec bundle's feedback file
  (`specs/**/feedback/<name>.md`): it is collected as code, so two tasks that resolve the same feedback file overlap
  on it.
- The registry lives in the Git common directory, so every worktree of the repository shares it with no setup.

## Step by step

1. **Read the Git policy** to see which activities get their own worktree:

   ```sh
   uv run devkit spec policy     # look at [GIT_POLICY: worktree=...]
   ```

   See [`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/delivery/CAP-DLV-project-policy.md).
2. **Compare the planned scopes** before anything starts. This reads declarations only and writes nothing:

   ```sh
   uv run devkit spec scope compare --proposal <a> --proposal <b>
   uv run devkit spec scope compare --spec <dir-a> --spec <dir-b>
   ```

   Each pair gets a `[PAIR: ... docs=N ...]` line with `[EVIDENCE: <path> ... kind=doc|code ...]` lines, then a
   `[SUMMARY: sets=2 pairs=1 overlapping=1]`.
3. **Start the tasks** you decided to run in parallel, each on its activity branch in its own task worktree
   (`uv run devkit worktree start dev-<slug>`;
   [`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
4. **Register each task** from its worktree:

   ```sh
   uv run devkit spec scope register --spec <dir>
   ```

   The registry stores the declared and Git-observed scope and prints the worktree's owner token once.
5. **Update after planning changes.** Whenever a task writes `tasks.md` or `reconcile.md`:

   ```sh
   uv run devkit spec scope update --spec <dir>
   ```

   The result is `[SCOPE_ACK: status=applied ... overlaps=N ...]` plus the overlapping records. An overlap never
   grants or refuses a write; it is information for scheduling.
6. **Order integration.** `uv run devkit spec scope query` lists the records and this worktree's overlaps with the
   others; integrate overlapping work one after another.
7. **Finish.** `devkit worktree finish` integrates the branch and removes the worktree, and the post-finish cleanup
   removes that worktree's scope record. Other records stay.

## Reading "unresolved"

An input that cannot become a path is counted as unresolved with its reason (for example `reason=no-entrypoints` for a
capability target without `entrypoints`, a planned document, a waived target or a missing file). Unresolved never
means "no overlap". Adding `entrypoints` to the capabilities you target makes the comparison sharper.

## When it goes wrong

- **`SPEC_SCOPE_TOKEN_EXISTS`.** This worktree already registered a task. The first record and token stay; continue
  with `update`.
- **`SPEC_SCOPE_TOKEN_MISSING`.** This worktree registered nothing. Nothing is written; the task simply takes no part
  in the registry.
- **`SPEC_SCOPE_STALE_REVISION` with `[SCOPE_ACK: status=stale ...]`.** The record changed between your read and your
  write. Nothing was written; run `update` again.
- **`SPEC_SCOPE_TIMEOUT` with `status=timeout`.** The lock or Git took too long. Retry with the same request ID
  (`devkit spec scope update --spec <dir> --request-id <id>`); an update that already applied is answered from the
  stored record without a second write.
- **A record outlives its worktree** (the cleanup failed, or the worktree was removed without a finish). From the base
  checkout run `uv run devkit spec scope sweep --apply`. Stale records whose revision is unchanged are removed
  (`[SWEEP: <task> verdict=removed reason=worktree-missing ...]`); a record whose revision moved is kept and reported
  as `SPEC_SCOPE_STALE_REVISION`.

## What you end up with

Each running task's record reflects its latest scope, you know every pair's shared documents and code and how much is
unknown, no task was ever blocked, and finished tasks leave no records behind. Overlap evidence is a join of
declarations and Git observations: it proves neither a merge conflict nor independence.
