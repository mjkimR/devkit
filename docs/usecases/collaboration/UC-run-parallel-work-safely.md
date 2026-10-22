---
id: UC-run-parallel-work-safely
title: Run Parallel Work Safely
summary: "An orchestrating AI coding agent runs several proposals or spec bundles in parallel task worktrees and reads, before and during the work, which documents and code paths they share, to schedule them and order their integration without any task being blocked."
area: collaboration
primary_actor: AI coding agent orchestrating parallel tasks
supporting_actors:
  - Workers or developer sessions running the other tasks in their own worktrees
  - Git (the repository's common directory and its worktrees)
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

- **Goal**: see which Living Spec documents and code paths planned and running tasks share, and how much of their
  scope is still unknown, so that the orchestrator decides what runs in parallel and in which order work is integrated
  before conflicts appear, without any task being blocked by a lock
- **Scope**: `devkit spec scope` and its work-scope registry, together with the task worktrees the tasks run in
- **Trigger**: the orchestrator has two or more proposals or spec bundles to run at the same time
- **Preconditions**: the repository is a Git repository with devkit-spec installed; each task declares its scope in
  its bundle (`target-docs.md` or `reconcile.md` targets, `tasks.md` `_Boundary` entries, the targets'
  `entrypoints`); the registry lives in the Git common directory, so every worktree shares it without configuration

---

## 2. Main Success Scenario

1. The orchestrator reads the project's Git policy to learn which activities run in their own task worktree
   (`CAP-DLV-project-policy`).
2. The orchestrator compares the declared scopes of the planned proposals or spec bundles; the system reports, for
   each pair, the documents and code paths both touch and each side's unresolved inputs, and writes nothing
   (`CAP-COLL-work-scope-registry`, path contract `CAP-TRACE-code-entrypoints`).
3. The orchestrator decides which tasks run in parallel and starts each one on its activity branch in its own task
   worktree (`CAP-WT-task-worktrees`).
4. Each task registers its spec bundle in the shared registry; the system stores the declared and Git-observed scope
   and returns the worktree's owner token once (`CAP-COLL-work-scope-registry`).
5. After a task writes `tasks.md` or `reconcile.md`, it updates its record; the system recollects the scope, writes
   it at the next revision and reports the other records it overlaps, without granting or refusing any write
   (`CAP-COLL-work-scope-registry`).
6. The orchestrator queries the registry and orders integration by the reported overlaps
   (`CAP-COLL-work-scope-registry`).
7. Each task finishes; the system integrates its branch, removes its worktree and then removes the finished
   worktree's record through the post-finish cleanup (`CAP-WT-task-worktrees`, `CAP-COLL-work-scope-registry`).

---

## 3. Extensions

- **\*a.** An input cannot become a path (a capability target without `entrypoints`, a planned document, a waived
  target, a missing input file): the system counts it as unresolved with its reason and never reads it as "no
  overlap"; resumes at the same step.
- **4a.** The worktree already registered a task: the system refuses with `SPEC_SCOPE_TOKEN_EXISTS` and keeps the
  first record; resumes at step 5 with the existing registration.
- **5a.** The worktree registered nothing: the system refuses with `SPEC_SCOPE_TOKEN_MISSING`; the task takes no part
  in the registry and skips the update; resumes at step 6.
- **5b.** The record changed between the task's read and its write: the system refuses with
  `SPEC_SCOPE_STALE_REVISION` and writes nothing; the task updates again; resumes at step 5.
- **5c.** The lock or Git outlasts the configured timeout: the system refuses with `SPEC_SCOPE_TIMEOUT`; the task
  retries with the same request ID, and an update that already applied is answered from the stored record without a
  second write; resumes at step 6.
- **7a.** A record remains for a worktree that is gone (the post-finish record removal failed, or the worktree was
  removed without a finish): the orchestrator sweeps the registry from the base checkout; the system removes each
  stale record whose revision is unchanged and keeps a record whose revision moved, reporting
  `SPEC_SCOPE_STALE_REVISION`; the use case ends.

---

## 4. Postconditions

- **Success guarantee**: every running task's record holds its declared and observed scope at its latest revision;
  the orchestrator has each pair's document and code overlaps and unresolved counts; no task was blocked by an
  overlap; the records of finished tasks are gone, and the namespace journal keeps every register, update, release
  and sweep event.
- **Minimal guarantee**: no scope result grants or refuses a write; a refused registration or update leaves the
  existing record unchanged; readers never see a partial record, and queries create nothing in the registry; a
  failed journal append never changes an operation's result.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Compares two proposals before work starts
- **Covers**: main success scenario (step 2)
- **Given**: two proposals whose `target-docs.md` both list the same capability file
- **When**: the orchestrator runs `devkit spec scope compare --proposal <a> --proposal <b>`
- **Then**: the output has one `[PAIR: ... docs=1 ...]` line with an `[EVIDENCE: <path> ... kind=doc ...]` line and a
  `[SUMMARY: sets=2 pairs=1 overlapping=1]` line, and nothing is written

### Scenario 2: Reports a running task's overlaps without blocking it
- **Covers**: main success scenario (steps 4 and 5)
- **Given**: two task worktrees, each registered with `devkit spec scope register --spec <dir>`, whose `tasks.md`
  boundaries share a source directory
- **When**: one of them runs `devkit spec scope update --spec <dir>`
- **Then**: it prints the pair with `kind=code` evidence and `[SCOPE_ACK: status=applied ... overlaps=1 ...]`, and
  the overlap does not prevent either task from writing

### Scenario 3: Removes a finished task's record after the finish
- **Covers**: main success scenario (step 7)
- **Given**: a registered task in its own worktree
- **When**: `devkit worktree finish` integrates its branch and removes the worktree
- **Then**: the post-finish cleanup removes that worktree's record at the revision it read, and the other records
  stay in the registry

### Scenario 4: Counts unknown scope instead of hiding it
- **Covers**: \*a
- **Given**: a spec whose `reconcile.md` targets a capability without `entrypoints`
- **When**: the scope is compared or updated
- **Then**: the input is counted as unresolved with `reason=no-entrypoints`, never read as "no overlap"

### Scenario 5: Refuses a second registration from one worktree
- **Covers**: 4a
- **Given**: a worktree that already registered a task
- **When**: it runs `devkit spec scope register --spec <dir>` again
- **Then**: the command fails with `SPEC_SCOPE_TOKEN_EXISTS`, and the first record and its token are unchanged

### Scenario 6: Skips the update in an unregistered worktree
- **Covers**: 5a
- **Given**: a worktree that registered nothing
- **When**: the task runs `devkit spec scope update --spec <dir>` after writing `tasks.md`
- **Then**: the command fails with `SPEC_SCOPE_TOKEN_MISSING`, nothing is written, and the task continues without the
  registry

### Scenario 7: Refuses an update against a changed record
- **Covers**: 5b
- **Given**: a record whose revision moved after the task read it
- **When**: the task's update is applied
- **Then**: the command prints `[SCOPE_ACK: status=stale ...]`, fails with `SPEC_SCOPE_STALE_REVISION`, and the record
  keeps the other writer's revision

### Scenario 8: Answers a retried update from the stored record
- **Covers**: 5c
- **Given**: an update with request ID `r1` that ended with `[SCOPE_ACK: status=timeout ...]` and
  `SPEC_SCOPE_TIMEOUT`, so the task did not see its outcome
- **When**: the task reruns `devkit spec scope update --spec <dir> --request-id r1`
- **Then**: when the record already applied `r1`, the result comes from the stored record with the `added` and
  `removed` counts of `r1` and no second write happens; otherwise the update applies once

### Scenario 9: Sweeps a stale record left by a removed worktree
- **Covers**: 7a
- **Given**: a registered task whose worktree no longer exists on this host and whose record no post-finish cleanup
  removed
- **When**: the agent runs `devkit spec scope sweep --apply` in the base checkout
- **Then**: the record is reported as `[SWEEP: <task> verdict=removed reason=worktree-missing ...]` and is gone,
  while a record whose revision changed since it was read is kept with `SPEC_SCOPE_STALE_REVISION`
