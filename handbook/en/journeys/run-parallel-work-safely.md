---
sources:
  CAP-COLL-work-scope-registry: a2dea3a64550dfad9c3225650fbf433174d56773
  CAP-DLV-project-policy: 69045e11fa4d0e8998f0b1ac44a30b403ab93425
  CAP-TRACE-code-entrypoints: f85e685d002096791b5d75d3954edc3782f59f9b
  CAP-WT-task-worktrees: 2f5c45415f121e1d1d47046f255be4d4163e24dc
  UC-run-parallel-work-safely: 0d974e0c636645b44666c8442980b3c83f3bdf72
title: Run parallel work safely
---

# Run parallel work safely

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `93e3808721b4`, generated 2026-11-13. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](adopt-sdd-from-adaptive-development.md)
- [Advance an idea](advance-an-idea.md)
- [Assess a selected test suite](assess-test-management.md)
- [Design necessary command entry points](design-command-entrypoints.md)
- [Discover and refine an idea](discover-and-refine-an-idea.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Execute an isolated command](execute-an-isolated-command.md)
- [Explore a design problem](explore-a-design-problem.md)
- [Find the latest maintenance run](find-the-latest-maintenance-run.md)
- [Find the right documents](find-the-right-documents.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Import selected third-party agent assets](import-third-party-agent-assets.md)
- [Improve an interface and user flow](improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Plan and hand off a proposal](plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Read decision supersession](read-decision-supersession.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Record a maintenance run](record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](research-an-idea-and-shape-a-roadmap.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Adopt and refresh bundle sources locally](snapshot-bundle-sources.md)
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

Source: [`UC-run-parallel-work-safely`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/collaboration/UC-run-parallel-work-safely.md),
contract [`CAP-COLL-work-scope-registry`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md).

## Before you start

- The repository is a Git repository with `devkit-spec` installed.
- Each task declares its scope in its bundle: `target-docs.md` or `reconcile.md` targets, the `_Boundary` entries of
  `tasks.md`, and the `entrypoints` of the documents it targets. Entrypoints turn a document into code paths
  ([`CAP-TRACE-code-entrypoints`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md)).
  A `_Boundary` entry under `specs/` is skipped, except the exact path of another spec bundle's feedback file
  (`specs/**/feedback/<name>.md`): it is collected as code, so two tasks that resolve the same feedback file overlap
  on it.
- The registry lives in the Git common directory, so every worktree of the repository shares it with no setup.

## Step by step

1. **Read the Git policy** to see which activities get their own worktree:

   ```sh
   uv run devkit spec policy     # look at [GIT_POLICY: worktree=...]
   ```

   See [`CAP-DLV-project-policy`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/delivery/CAP-DLV-project-policy.md).
2. **Inspect existing activity sources.** Run `uv run devkit spec scope collect` to compare declarations and observed changes from tasks with a `plan-*` or `dev-*` source. Queued drafts have no source and are excluded. Read unresolved inputs alongside overlaps.
3. **Start the tasks** you decided to run in parallel, each on its activity branch in its own task worktree
   (`uv run devkit worktree start dev-<slug>`;
   [`CAP-WT-task-worktrees`](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/worktree/CAP-WT-task-worktrees.md)).
   When `devkit spec new` or `devkit spec proposal handoff` creates the unit in a linked worktree, it records an
   initial scope snapshot in the registry on its own. That registration is best effort: if it fails, creation still
   succeeds and nobody has to repair it.
4. **Let the work run.** Workers write their declarations and changes through the normal delivery workflow. They
   have no duty to register, update or acknowledge scope, and `devkit workflow next` collects nothing.
5. **Observe when you need evidence.** The orchestrating agent asks for it explicitly, from any checkout:

   ```sh
   uv run devkit spec scope collect
   uv run devkit spec scope collect --fetch origin
   ```

   One collection combines creation snapshots, activity refs and accessible worktree declarations and changes,
   distinguishing observed current writes from a Planning proposal's declared future scope (`horizon`: `current` vs
   `future`). Drafts without an activity source are excluded. `--fetch` refreshes a configured remote first; without
   it, remote branches are what the last fetch saw. Output lists each `[SCOPE_CANDIDATE: ...]` and
   `[SCOPE_OBSERVATION: ...]`, the `[PAIR: ...]` (with `current`/`future` counts) and `[EVIDENCE: ...]` lines, and a
   `[SUMMARY: ... coverage=complete|partial ...]` reporting `current_overlapping`. Collecting changes no record or
   token.
6. **Order work and integration.** Use the overlaps, their `horizon` (`current` vs `future`), where each observation
   came from, and the coverage that is missing to decide what runs in parallel. Serialize current overlap
   (`current_overlapping`). Work with future-only overlap can keep Planning in parallel while ordering handoff and
   integration one after another.
7. **Finish.** Integration removes the worktree, and the post-finish cleanup removes that worktree's scope record.
   Other records stay.

## Reading "unresolved" and "partial"

An input that cannot become a path is counted as unresolved with its reason (for example `reason=no-entrypoints` for a
capability target without `entrypoints`, a planned document, a waived target or a missing file). Unresolved never
means "no overlap". Adding `entrypoints` to the capabilities you target makes the comparison sharper.

`coverage=partial` with a `SPEC_SCOPE_COLLECTION_PARTIAL` warning means some source, base, identity or comparison
could not be observed within its budget. The evidence that was collected is still usable, and the warning names
each missing source with its reason. Unknown inputs and unavailable sources never establish independence; pairs that
were not computed never count as zero overlap.

## When it goes wrong

- **`SPEC_SCOPE_COLLECTION_PARTIAL`.** Usable evidence with gaps; the run exits `0` (`1` under `--strict`). Decide
  with the gaps in view, or repair access and collect again.
- **`SPEC_SCOPE_COLLECTION_FAILED`.** No selected inventory source could be read. Repair access to the sources named
  in `[TARGET]` and collect again.
- **`ARGUMENT_INVALID`.** A budget or remote is invalid. Correct the arguments.
- **Work on another machine is missing.** No observation reads another PC's unpushed or uncommitted changes. For
  frequent multi-PC work, push declarations and changes, ideally through pull requests, so collection sees them.
- **A record outlives its worktree** (the cleanup failed, or the worktree was removed without a finish). From the base
  checkout run `uv run devkit spec scope sweep --apply`. Stale records whose revision is unchanged are removed
  (`[SWEEP: <task> verdict=removed reason=worktree-missing ...]`); a record whose revision moved is kept and reported
  as `SPEC_SCOPE_STALE_REVISION`.

## What you end up with

You know every pair's shared documents and code, where each observation came from and how much coverage is missing,
no task was ever blocked or given extra bookkeeping, and finished tasks leave no records behind. Overlap evidence is
a join of declarations and Git observations: it proves neither a merge conflict nor independence.
