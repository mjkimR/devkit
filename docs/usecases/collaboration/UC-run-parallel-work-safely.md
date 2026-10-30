---
id: UC-run-parallel-work-safely
title: Run Parallel Work Safely
summary: "An orchestrating AI coding agent runs several proposals or spec bundles in parallel task worktrees and reads, before and during the work, which documents and code paths they share, to schedule them and order their integration without any task being blocked."
area: collaboration
primary_actor: AI coding agent orchestrating parallel tasks
supporting_actors:
  - Workers or developer sessions running the other tasks in their own worktrees
  - Git (the repository's common directory and its worktrees)
entrypoints:
  - packages/devkit-spec/src/devkit_spec/features/scope/cli/commands.py
  - packages/devkit-spec/src/devkit_spec/features/scope/usecases/collection.py
status: active
created_at: 2026-10-13
capabilities:
  - CAP-COLL-work-scope-registry
  - CAP-TRACE-code-entrypoints
  - CAP-DLV-project-policy
  - CAP-WT-task-worktrees
---

# [UC-run-parallel-work-safely] Run Parallel Work Safely

## 1. Goal

- **Goal**: select parallel execution and integration order using shared-path evidence and explicit uncertainty.
- **Scope**: Host comparison and observation through CAP-COLL-work-scope-registry.
- **Trigger**: the orchestrator needs to schedule two or more planned or running units.
- **Preconditions**: devkit-spec is installed; declarations follow CAP-TRACE-code-entrypoints.

## 2. Main Success Scenario

1. The Host reads project policy and compares planned declarations (CAP-DLV-project-policy,
   CAP-COLL-work-scope-registry).
2. The Host starts the selected activity worktrees (CAP-WT-task-worktrees).
3. Creation records initial eligible linked-worktree snapshots (CAP-COLL-work-scope-registry).
4. The workers write declarations and implementation changes through their normal delivery workflow.
5. The Host explicitly observes available snapshots, branch trees and worktrees at the chosen depth
   (CAP-COLL-work-scope-registry).
6. The Host uses overlaps, their horizon, provenance and missing coverage to choose parallelism and integration
   order: `current` overlap serializes running activities, `future` overlap orders handoff and integration
   (CAP-COLL-work-scope-registry).
7. Integration removes completed worktrees and their records through post-finish cleanup (CAP-WT-task-worktrees,
   CAP-COLL-work-scope-registry).

## 3. Extensions

- **1a.** A declaration cannot become a path: count its unresolved reason, never treat it as independence; resume at
  step 1 with incomplete evidence.
- **3a.** Automatic registration fails: preserve creation outcomes without a worker maintenance task; resume at
  step 4. The Host can observe qualifying unregistered work later.
- **5a.** A source, base, identity or comparison is unavailable or exceeds a budget: return usable partial evidence
  with `SPEC_SCOPE_COLLECTION_PARTIAL`; resume at step 6 with the missing coverage explicit.
- **5b.** No selected inventory source is readable: fail with `SPEC_SCOPE_COLLECTION_FAILED`; the Host repairs access
  and resumes at step 5.
- **5c.** The selected mode and fetch arguments conflict or a budget/remote is invalid: fail with `ARGUMENT_INVALID`;
  correct the arguments and resume at step 5.
- **5d.** Other-machine private changes are unavailable: retain published refs or snapshot-only evidence, with its
  provenance. For frequent multi-PC work use PRs with pushed declarations/changes; resume at step 6 without claiming
  private-worktree visibility.
- **6a.** Two Planning units overlap only in `future` evidence (declared or candidate paths) while their observed
  writes are disjoint: run their Planning in parallel; before handing either off, treat that evidence as `current`
  and hand off and integrate them sequentially; resume at step 7.
- **7a.** A stale record remains after worktree removal: the Host explicitly sweeps at the read revision; a changed
  record is retained with `SPEC_SCOPE_STALE_REVISION`; the use case ends.

## 4. Postconditions

- **Success guarantee**: the Host has observed-path overlaps, their `current` or `future` horizon and the
  coverage/freshness needed to interpret them.
  Workers have no scope update or ACK duty. Finished worktree records are cleaned after successful integration.
- **Minimal guarantee**: evidence grants no write permission and certifies no independence. Host collection leaves
  registry records, owner tokens and journals unchanged; explicit fetch updates only requested tracking refs.
  Creation snapshots can lag and observations are not atomic across worktrees.

## 5. Acceptance Criteria by Example Mapping

### Scenario 1: Compare planned declarations

- **Covers**: step 1; extension 1a.
- **Given** two proposals sharing a target and an unresolved input.
- **When** the Host compares declarations.
- **Then** output includes document overlap and the unresolved reason, with no registry writes.

### Scenario 2: Observe running work without worker publication

- **Covers**: steps 3–6; extension 3a.
- **Given** registered and unregistered task branches/worktrees with shared code boundaries.
- **When** the Host collects live evidence after worker edits.
- **Then** output attributes each source, reports observed overlap, creates no worker ACK and leaves tokens,
  registry bytes and journals unchanged.

### Scenario 3: Preserve partial coverage and published-only remote visibility

- **Covers**: extensions 5a and 5d.
- **Given** cached remote refs, inaccessible worktree evidence or a comparison/input limit.
- **When** the Host collects at the requested mode.
- **Then** usable evidence includes `SPEC_SCOPE_COLLECTION_PARTIAL` and missing coverage; default exit is 0 and
  strict exit is 1. No private remote changes are claimed.

### Scenario 4: Refuse an unusable request

- **Covers**: extensions 5b and 5c.
- **Given** no readable inventory or conflicting snapshot/fetch arguments.
- **When** the Host requests collection.
- **Then** exit is 2 with `SPEC_SCOPE_COLLECTION_FAILED` or `ARGUMENT_INVALID` respectively.

### Scenario 5: Clean only finished records

- **Covers**: step 7; extension 7a.
- **Given** a successful task finish or an explicitly swept stale record.
- **When** cleanup validates its read revision.
- **Then** only the eligible record is removed; a moved revision remains with `SPEC_SCOPE_STALE_REVISION`.

### Scenario 6: Tell current writes from future impact (GOP-04)

- **Covers**: step 6; extension 6a.
- **Given** two Planning units whose observed writes are only their own proposal directories, whose targets'
  `entrypoints` overlap, and one of which declares a planned document.
- **When** the Host collects scope for scheduling.
- **Then** exit is 0 without `--strict`; the output lists the observed proposal paths, the `horizon=future`
  evidence with `current=0` for the pair and the `planned-doc` input of the coverage gap; no field grants or refuses
  a write.
