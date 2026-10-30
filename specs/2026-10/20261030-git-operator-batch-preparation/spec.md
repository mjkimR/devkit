---
id: SPEC-git-operator-batch-preparation
title: Bounded batch preparation for git-operator
summary: Let the Host dispatch an exact finite list of independent worktree preparations with per-item identity, authority, effects, checks and outcome, keeping original CLI results for partial or denied items and retrying only inspected authorized remainders.
status: in-progress
created: 2026-10-30
depends_on:
  - SPEC-git-operator-result-readiness
decomposed_from: PROP-git-operator-pilot-follow-up
related_capabilities:
  - CAP-DLV-delivery-workflows
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-git-operator-batch-preparation] Bounded batch preparation for git-operator

## 1. Problem Statement & Motivation

Handed off from proposal PROP-git-operator-batch-preparation on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-git-operator-batch-preparation`

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), preparing five exact worktrees required an
ad hoc multi-job payload and an aggregate return under a role contract written for one job. This repository repeated
the pattern (`MAT-git-operator-batch-dispatch-observation`): one Host message listed six `prepare-worktree` jobs with
full fields, and one `git-operator` ran them in sequence and returned a result per job. No item was refused, denied
or partial in either run, and no cost or latency comparison exists.

The `git-operator` contract still says "one exact lifecycle job", so the list form, its stop rule and its per-item
return are undefined. One `devkit worktree start` item ends in one of five outcome classes the material lists
(refused before creation, creation rolled back, created then failed before setup, created with a zero-exit setup or
sync warning, not dispatched because host approval was denied), and one CLI code does not tell an item-local cause
from a repository-wide one.

The hypothesis: making the observed list form explicit, with a per-item result and a stated stop rule, keeps
per-item identity, authority and recovery when an item does not complete, without a new command.

### Premise check against the current base

`SPEC-git-operator-result-readiness` is on the base (`133819ed`) with the shape this spec reuses: the single-job
return adds `checks.worker_input: {head, dirty_paths}` for `prepare-worktree` and `handoff`, each dirty path is a
`remaining_effects` entry with role status `needs_input`, every result returns to the Host, and a host refusal before
dispatch is a blocker code with a null CLI result (null status and exit code, empty effects). It owns the GOP-06
operator-scope sentence in the contract's Authority and boundaries. `prepare-worktree` is unchanged. Both premises of
the proposal hold.

## 2. User Stories

- **US-1**: As a Host preparing several independent Units, I want to dispatch one exact finite list of
  `prepare-worktree` items to one `git-operator`, so that I do not compose an ad hoc multi-job payload.
- **US-2**: As a Host whose list has an item that does not complete, I want the operator to stop there and return
  each attempted item's single-job result and each later item as not attempted, so that I know exactly what exists and
  what remains.
- **US-3**: As a Host retrying a stopped list, I want guidance to verify the returned state and dispatch only the
  remaining items I still authorize, so that a completed item is never repeated and a setup or sync remainder stays
  my decision.

## 3. Non-Goals

1. **Scope Excluded**: a new CLI operation or flag, including a multi-branch `devkit worktree start`; `packages/devkit`
   and `CAP-WT-task-worktrees` do not change.
2. **Scope Excluded**: a list of any operation other than `prepare-worktree`; `handoff`, integration, cleanup and
   `inspect-recovery` stay one job per dispatch.
3. **Scope Excluded**: concurrent execution of list items, a daemon, a global repository lock or an autonomous
   scheduler.
4. **Scope Excluded**: operator-run repair of a setup or sync remainder (the setup `[FIX]`, `devkit sync`, registration
   initialization), approval grants, force operations or arbitrary remote deletion.
5. **Scope Excluded**: a claim of token, cost or latency savings; the list form's live stop and retry behavior stays
   reported as unverified until a real partial list is observed.
6. **Scope Excluded**: a new GOP-06 operator-scope sentence beyond the list-authority sentence; the wording belongs to
   `SPEC-git-operator-result-readiness`.

## 4. Acceptance Criteria & Behavioral Contracts

Each criterion is checked by contract-text tests in
`packages/devkit-spec/tests/integration/bundles/spec/test_git_operator.py` on the bundle sources; a test passes only
when one paragraph, list item or table row states every token it names (`assert_rule`).

### [AC-01] The role contract accepts a finite list of prepare-worktree items only
- **Given** the `git-operator` contract's Input section
- **When** a Host composes a dispatch of more than one job
- **Then** the contract states that a dispatch MAY carry a finite, exact preparation list of `prepare-worktree` items,
  that each item repeats every single-job field and has its own branch, worktree path and Unit, that all items name
  the same retained base and base ref, and that every other operation stays one job per dispatch

### [AC-02] Items run serially and the list stops at the first item that is not completed
- **Given** a preparation list in the contract's Procedure
- **When** the operator runs it
- **Then** the contract states that items run one at a time in the listed order, each through the guarded
  `prepare-worktree` procedure with its own refresh and its own approval request on Codex; that before each item the
  operator checks that the retained base HEAD still equals the dispatched base ref; and that at the first item that is
  not completed (a refusal, a failure, a zero-exit setup or sync warning, a moved base ref, or refused or unavailable
  host approval) it stops and returns every later item as not attempted

### [AC-03] The list return wraps the single-job return per item
- **Given** the contract's Return section
- **When** a preparation list ends
- **Then** the contract shows a list return with `items` and `not_attempted`, states that each attempted item carries
  the single-job return unchanged (its original `cli_result`, `completed_effects`, `remaining_effects`,
  `checks.worker_input` and `blocker_codes`), that an item stopped by refused or unavailable host approval carries a
  host-permission blocker code and the null CLI result, that each `not_attempted` entry names the item's identity and
  intended effects with the null CLI result, that the list status is `completed` only when every listed item is
  `completed`, else `needs_input` when any attempted item is `needs_input`, else `failed`, and that no `partial`
  status is added

### [AC-04] The Host retries only inspected, authorized remainders
- **Given** the dispatch reference `git-operator-dispatch.md`
- **When** a preparation list returns with a stopped item or not-attempted items
- **Then** it states that the Host verifies each returned item against its own CLI/Git observation or dispatches
  `inspect-recovery`, dispatches a new list naming only the remaining items it still authorizes with current refs,
  never repeats a completed item, and handles a setup or sync remainder itself or through a supported operation; and
  the role contract states that the operator runs no setup `[FIX]`, sync or registration repair

### [AC-05] A list's authority covers only its listed items, and GOP-06 still holds
- **Given** the contract's Authority and boundaries section
- **When** the operator receives a preparation list, or a request for production edits, semantic conflict resolution
  or broader authority
- **Then** the section states that a list's authority covers only its listed `prepare-worktree` items, and the
  existing GOP-06 sentence (production edits, semantic conflict resolution and authority beyond the job return to the
  Host, with no such mutation) still passes its regression test

### [AC-06] Dispatch guidance and payload carry the list form
- **Given** `git-operator-operations.md` and `spec-delegate/references/payload.md`
- **When** the Host prepares a preparation list
- **Then** the `prepare-worktree` operations row states that a list runs its items in order and stops at the first
  item that is not completed, and the payload's `git-operator` row states that a preparation list repeats every field
  per item

### [AC-07] No CLI change
- **Given** the change against the base `133819ed`
- **When** the diff is listed for `packages/devkit/`
- **Then** it is empty, and the existing worktree CLI tests of each outcome class's code and exit pass unchanged

## 5. Assumptions

- "Null `cli_result`" in the user's decisions means the single-job null CLI result the base contract defines
  (`{status: null, exit_code: null, effects: []}`), so a not-attempted entry and a host-denied item share one shape.
- The list status rule reads "any remainder needs a Host decision" as "any attempted item is `needs_input`": a list
  whose stopped item `failed` is `failed` even though later items were not attempted, because not-attempted items are
  always a remainder and would otherwise make every stopped list `needs_input`.
- A moved base ref stops the list at the item about to run; that item is returned as attempted with `needs_input`, the
  changed-ref blocker and the null CLI result, because the single-job procedure returns changed refs as a blocker
  before any mutation.
- No stable host-permission code exists; the contract keeps "a host-permission blocker code" as the base contract's
  single-job return does, and this spec names none.
- The list form adds no use case extension: `UC-drive-development-to-integration` extension 1b ("the Host reuses
  git-operator for read-only preparation and exact authorized execution") stays true for a list.
