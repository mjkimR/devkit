---
sources:
  CAP-COLL-work-scope-registry: 23990ff536e67c96f25dff1857c08cbd0c4c8838
  CAP-DLV-project-policy: 2af5b2fde75faecfa8260244a614fa796525de03
  CAP-TRACE-code-entrypoints: 71c9a300749a114f5dd4141e70aee300dcafd4ee
  CAP-WT-task-worktrees: 2ea80d46ab9cf19504182e73b6f2bcc301e8f7db
  UC-run-parallel-work-safely: f60eea1f7ddb44d8d4d47058e2777990f1a50d64
title: Run parallel work safely
---

# Run parallel work safely

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `022b9f03bbd2`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
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
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
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

When you (or an orchestrating agent) run two or more proposals or spec bundles at once, the risk is that they touch
the same documents or code and collide at integration. devkit does not lock anything. Instead `devkit spec scope`
shows, before and during the work, which Living Spec documents and code paths the tasks share and how much of their
scope is still unknown, so you decide what runs in parallel and in which order it lands.

Task worktrees and activity branches are explained in [Concepts](../concepts.md); the registry itself in the
[collaboration area](../areas/collaboration.md).

Source: [`UC-run-parallel-work-safely`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/collaboration/UC-run-parallel-work-safely.md),
contract [`CAP-COLL-work-scope-registry`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md).

## Before you start

- The repository is a Git repository with `devkit-spec` installed.
- Each task declares its scope in its bundle: `target-docs.md` or `reconcile.md` targets, the `_Boundary` entries of
  `tasks.md`, and the `entrypoints` of the documents it targets. Entrypoints turn a document into code paths
  ([`CAP-TRACE-code-entrypoints`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md)).
  A `_Boundary` entry under `specs/` is skipped, except the exact path of another spec bundle's feedback file
  (`specs/**/feedback/<name>.md`): it is collected as code, so two tasks that resolve the same feedback file overlap
  on it.
- The registry lives in the Git common directory, so every worktree of the repository shares it with no setup.

## Step by step

1. **Read the Git policy** to see which activities get their own worktree:

   ```sh
   uv run devkit spec policy     # look at [GIT_POLICY: worktree=...]
   ```

   See [`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/delivery/CAP-DLV-project-policy.md).
2. **Compare the planned scopes** before anything starts. This reads declarations only and writes nothing:

   ```sh
   uv run devkit spec scope compare --proposal <a> --proposal <b>
   uv run devkit spec scope compare --spec <dir-a> --spec <dir-b>
   ```

   Each pair gets a `[PAIR: ... docs=N ...]` line with `[EVIDENCE: <path> ... kind=doc|code ...]` lines, then a
   `[SUMMARY: sets=2 pairs=1 overlapping=1]`.
3. **Start the tasks** you decided to run in parallel, each on its activity branch in its own task worktree
   (`uv run devkit worktree start dev-<slug>`;
   [`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
   When `devkit spec new` or `devkit spec proposal handoff` creates the unit in a linked worktree, it records an
   initial scope snapshot in the registry on its own. That registration is best effort: if it fails, creation still
   succeeds and nobody has to repair it.
4. **Let the work run.** Workers write their declarations and changes through the normal delivery workflow. They
   have no duty to register, update or acknowledge scope, and `devkit workflow next` collects nothing.
5. **Observe when you need evidence.** The orchestrating agent asks for it explicitly, from any checkout:

   ```sh
   uv run devkit spec scope collect                        # default --mode worktrees
   uv run devkit spec scope collect --mode refs --fetch origin
   ```

   The mode chooses how deep to look: `snapshot` reads only the registry records, `refs` adds local and fetched
   `plan-*` and `dev-*` branches, and `worktrees` adds each accessible worktree's declarations and its committed,
   staged, unstaged and untracked paths. `--fetch` refreshes a configured remote first; without it, remote branches
   are what the last fetch saw. Output lists each `[SCOPE_CANDIDATE: ...]` and `[SCOPE_OBSERVATION: ...]`, the
   `[PAIR: ...]` and `[EVIDENCE: ...]` lines, and a `[SUMMARY: ... coverage=complete|partial ...]`. Collecting changes
   no record, token or journal.
6. **Order integration.** Use the overlaps, where each observation came from, and the coverage that is missing to
   decide what keeps running in parallel; integrate overlapping work one after another.
7. **Finish.** Integration removes the worktree, and the post-finish cleanup removes that worktree's scope record.
   Other records stay.

## Reading "unresolved" and "partial"

An input that cannot become a path is counted as unresolved with its reason (for example `reason=no-entrypoints` for a
capability target without `entrypoints`, a planned document, a waived target or a missing file). Unresolved never
means "no overlap". Adding `entrypoints` to the capabilities you target makes the comparison sharper.

`coverage=partial` with a `SPEC_SCOPE_COLLECTION_PARTIAL` warning means some source, base, identity or comparison
could not be observed within its budget. The evidence that was collected is still usable, and the warning names
each missing source with its reason. Pairs that were not computed never count as zero overlap.

## When it goes wrong

- **`SPEC_SCOPE_COLLECTION_PARTIAL`.** Usable evidence with gaps; the run exits `0` (`1` under `--strict`). Decide
  with the gaps in view, or repair access and collect again.
- **`SPEC_SCOPE_COLLECTION_FAILED`.** No selected inventory source could be read. Repair access to the sources named
  in `[TARGET]` and collect again.
- **`ARGUMENT_INVALID`.** The mode and fetch arguments conflict (for example `--mode snapshot` with `--fetch`), or a
  budget or remote is invalid. Correct the arguments.
- **Work on another machine is missing.** No observation reads another PC's unpushed or uncommitted changes. For
  frequent multi-PC work, push declarations and changes, ideally through pull requests, so `refs` mode sees them.
- **A record outlives its worktree** (the cleanup failed, or the worktree was removed without a finish). From the base
  checkout run `uv run devkit spec scope sweep --apply`. Stale records whose revision is unchanged are removed
  (`[SWEEP: <task> verdict=removed reason=worktree-missing ...]`); a record whose revision moved is kept and reported
  as `SPEC_SCOPE_STALE_REVISION`.

## What you end up with

You know every pair's shared documents and code, where each observation came from and how much coverage is missing,
no task was ever blocked or given extra bookkeeping, and finished tasks leave no records behind. Overlap evidence is
a join of declarations and Git observations: it proves neither a merge conflict nor independence.
