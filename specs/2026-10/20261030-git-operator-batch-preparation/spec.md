---
id: SPEC-git-operator-batch-preparation
title: Bounded batch preparation for git-operator
summary: Let the Host dispatch an exact finite list of independent worktree preparations with per-item identity, authority, effects, checks and outcome, keeping original CLI results for partial or denied items and retrying only inspected authorized remainders.
status: planned
created: 2026-10-30
depends_on:
  - SPEC-git-operator-result-readiness
decomposed_from: PROP-git-operator-pilot-follow-up
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-git-operator-batch-preparation] Bounded batch preparation for git-operator

## 1. Problem Statement & Motivation

Handed off from proposal PROP-git-operator-batch-preparation on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-git-operator-batch-preparation`

### 1. Background & Hypothesis

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), preparing five exact worktrees required an
ad hoc multi-job payload and an aggregate return under a role contract written for one job. The operations
succeeded; partial-batch behavior remains unverified.

This repository repeated the pattern (`MAT-git-operator-batch-dispatch-observation`): one Host message listed six
`prepare-worktree` jobs with full fields, and one `git-operator` ran them in sequence and returned a result per job,
all completed in about 50 seconds. Earlier jobs here used one job per dispatch through operator continuation. No
item was refused, denied or partial in either run, and no cost or latency comparison exists.

The hypothesis: making the observed list form explicit, with a per-item result and a stated stop rule, keeps
per-item identity, authority and recovery when an item does not complete, without a new command.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Bounded batch preparation for git-operator so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1 Mechanism**: Is a typed list of existing independent jobs in the role contract enough, or is a new CLI
  operation worth it? Compare dispatch and result size, permission overhead and failure recovery. CLI support may
  belong in `packages/devkit` (`devkit worktree start`); choosing it records a boundary extension in Planning.
  - Finding: two real runs completed through the list form with the existing `devkit worktree start` per item. A
    multi-branch CLI option would fold several items into one exit code and one effect list, which the per-item
    `cli_result` must keep apart anyway, and it adds an interface in `packages/devkit` for no observed failure. On
    Codex each item still needs its own approval for the sibling-worktree write in either form.
  - Decision (user, `answer-01` q1 option a): a typed list of `prepare-worktree` items in the role contract and
    dispatch guidance, each item through the existing `devkit worktree start`, no CLI change. Only `prepare-worktree`
    may form a list (`answer-01` q3 option a).
- **Q2 Partial outcomes**: How does a batch stop or continue on a denied or partial item, and how does a retry target
  only the inspected, authorized remainder?
  - Finding: one `devkit worktree start` item ends in one of five classes
    (`MAT-git-operator-batch-dispatch-observation`): refused before creation, creation rolled back, created then failed
    before setup, created with a zero-exit setup or sync warning, or not dispatched because host approval was denied.
    The CLI code does not tell an item-local cause from a repository-wide one: a broken `post-checkout` hook is
    `WORKTREE_ADD_FAILED` and an offline or broken setup command is `WORKTREE_SETUP_FAILED` for every item, each after up
    to 900 seconds (`challenger-01` finding 1).
  - Decision (user, `answer-01` q2 option a): stop at the first item that is not completed and return every later
    item as not attempted; the Host retries only the items it names from the returned state. Every setup or sync
    remainder returns to the Host (`answer-01` q4 option a).

### 3. Proposed Design & Impact

The design below folds the user's answers in `answer-01` and the Planning decisions listed after the acceptance
checks.

- **List form**: a dispatch MAY carry a finite, exact list of `prepare-worktree` items. Each item repeats every field
  of a single job (operation, absolute repository/base/worktree, Unit/branch, refs, intended_effects, authority,
  allowed_boundaries, writers_quiesced, expected_checks) and has a distinct branch, worktree path and Unit. All items
  name the same retained base and base ref. Authority covers only the listed items. Other operations stay one job
  per dispatch, because each integration or handoff changes the state the next job depends on.
- **Execution**: the operator runs items one at a time in the listed order, each through the existing guarded
  `prepare-worktree` procedure, with its own refresh before mutation and, on Codex, its own approval request.
- **Stop rule**: before each item the operator checks that the retained base HEAD still equals the dispatched base
  ref; uncommitted base changes do not block, because `start` leaves them in the base (`CAP-WT-task-worktrees` §2).
  At the first item that is not completed (a refusal, a failure, a zero-exit setup or sync warning, a moved base ref,
  or host approval refused or unavailable), it stops and returns every later item as not attempted, with a null
  `cli_result`.
- **Return**: one role message whose `items` list holds, per attempted item, the single-job return
  `SPEC-git-operator-result-readiness` defines, unchanged: role status, identity, the original `cli_result` (status,
  exit and effects), `completed_effects`, `remaining_effects` with any exact dirty paths, `checks.worker_input` with
  `{head, dirty_paths}` and `blocker_codes`; the next actor for a remainder is the Host. An item stopped by refused or
  unavailable host approval carries the host-permission blocker code and a null `cli_result`. A separate
  `not_attempted` list names each later item's identity and requested effects, with a null `cli_result`. The batch
  status uses the same three role statuses: `completed` only when every item is completed; otherwise `needs_input`
  when any remainder needs a Host decision, else `failed`. No `partial` status and no other top-level item field is
  added. A non-error notice (for example `WORKTREE_REMOTE_UNCHECKED` or a registration advisory) is reported on its
  item, and the item is completed only when its `checks.worker_input` and effects say so.
- **Retry**: the Host verifies the returned per-item state against current CLI/Git observations (or dispatches
  `inspect-recovery`) and dispatches a new list naming only the remaining items it still authorizes, with current
  refs. A completed item is never repeated. A retained worktree with a setup or sync remainder returns to the Host,
  which repairs it directly or dispatches a supported operation; the operator runs no setup `[FIX]`, sync or
  registration repair, because rerunning the setup `[FIX]` alone leaves the locked sync and registration
  initialization unverified (`challenger-01` finding 3).
- **Documents**: the git-operator contract (Input, Procedure, Return), `git-operator-dispatch.md` (list form, stop rule,
  acceptance and retry), `git-operator-operations.md` (`prepare-worktree` list),
  `spec-delegate/references/payload.md` (the git-operator row: repeat fields per item), `CAP-DLV-delivery-workflows`
  §4.6.1 (EARS rules for the list) and `test_git_operator.py` (wording checks). `CAP-WT-task-worktrees` and
  `packages/devkit` do not change.

Dependency on `SPEC-git-operator-result-readiness` (`depends_on`), as its Planning settled it:

1. Its per-job return adds no top-level field: worker-input readiness is `checks.worker_input` with
   `{head, dirty_paths}`, dirty paths are listed in `remaining_effects`, the Host is the next actor, and a
   host-permission denial is a blocker code with a null `cli_result`. This proposal reuses that shape per item; if
   its accepted shape differs, each item wraps that shape instead.
2. It leaves the `prepare-worktree` interface unchanged; its composed handoff commits its own transaction, which no
   list item uses, because a list carries only `prepare-worktree`.

Acceptance checks (from the parent's verification candidates):

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-05 | An authorized finite preparation list with one denied or partial item | A batch stops or continues within its stated policy | Each item's original CLI result and completed and remaining effects are retained; retries target only inspected authorized remainders. |
| GOP-06 | A request for production edits, semantic conflict resolution or broader authority | The operator receives the job | It returns that work to the Host or implementer and performs no such mutation. |

GOP-05 is checked mechanically by wording tests in `test_git_operator.py` (list form, base-ref check, stop rule,
per-item `cli_result`, not-attempted items, retry of named remainders only) and by the existing worktree CLI tests of
each outcome class's code and exit. The operator's live stop and retry behaviour stays reported as unverified until a
real partial batch is observed, separately from those checks (`MAT-git-operator-batch-dispatch-observation`).

GOP-06 is already met by the git-operator contract's Authority and boundaries. `SPEC-git-operator-result-readiness`
owns the shared GOP-06 operator-scope wording (Host decision). This proposal keeps GOP-06 as a regression check and
adds only the sentence that a list's authority covers only its listed `prepare-worktree` items, with its wording
check.

#### Planning decisions

- The user chose every recommended option in `answer-01`: the contract list with no CLI change (q1), stop at the
  first non-completed item (q2), `prepare-worktree` only (q3) and every setup or sync remainder to the Host (q4).
- The Host decided that `SPEC-git-operator-result-readiness` owns the shared GOP-06 operator-scope wording
  (`challenger-01` finding 6).
- No PADR is written: the list form, stop rule and retry rule are capability rules that `CAP-DLV-delivery-workflows`
  §4.6.1 records at handoff, and no architecture or interface choice remains.
- `dev_effort` is `low`: Development changes only contract and guidance wording and its wording tests, with no CLI or
  `packages/devkit` change.

#### Non-goals

- **Scope Excluded**: a daemon, global repository lock or autonomous scheduler.
- **Scope Excluded**: operator source authoring, approval grants, force operations or arbitrary remote deletion.
- **Scope Excluded**: unmeasured token, cost or latency savings.

### 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-git-operator-batch-preparation`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.

