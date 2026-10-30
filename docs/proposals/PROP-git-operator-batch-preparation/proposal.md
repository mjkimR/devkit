---
id: PROP-git-operator-batch-preparation
title: Bounded batch preparation for git-operator
summary: "Let the Host dispatch an exact finite list of independent worktree preparations with per-item identity, authority, effects, checks and outcome, keeping original CLI results for partial or denied items and retrying only inspected authorized remainders."
status: reviewing
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
milestone: MS-git-operator-lifecycle-refinement
depends_on: [PROP-git-operator-result-readiness]
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
  excludes:
    - .devkit/managed/
    - packages/devkit-core/
    - packages/devkit/
task_kind: feature
decomposed_from: PROP-git-operator-pilot-follow-up
workflow: sdd-proposal
---

# [PROP-git-operator-batch-preparation] Bounded batch preparation for git-operator

## 1. Background & Hypothesis

In the resource-indexer consumer pilot (`MAT-git-operator-consumer-pilot`), preparing five exact worktrees required an
ad hoc multi-job payload and an aggregate return under a role contract written for one job. The operations
succeeded; partial-batch behavior remains unverified.

This repository repeated the pattern (`MAT-git-operator-batch-dispatch-observation`): one Host message listed six
`prepare-worktree` jobs with full fields, and one `git-operator` ran them in sequence and returned a result per job,
all completed in about 50 seconds. Earlier jobs here used one job per dispatch through operator continuation. No
item was refused, denied or partial in either run, and no cost or latency comparison exists.

The hypothesis: making the observed list form explicit, with a per-item result and a stated stop rule, keeps
per-item identity, authority and recovery when an item does not complete, without a new command.

## 2. Technical Spike Questions

- **Q1 Mechanism**: Is a typed list of existing independent jobs in the role contract enough, or is a new CLI
  operation worth it? Compare dispatch and result size, permission overhead and failure recovery. CLI support may
  belong in `packages/devkit` (`devkit worktree start`); choosing it records a boundary extension in Planning.
  - Finding: two real runs completed through the list form with the existing `devkit worktree start` per item. A
    multi-branch CLI option would fold several items into one exit code and one effect list, which the per-item
    `cli_result` must keep apart anyway, and it adds an interface in `packages/devkit` for no observed failure. On
    Codex each item still needs its own approval for the sibling-worktree write in either form. Recommended: the
    contract list, no CLI change.
- **Q2 Partial outcomes**: How does a batch stop or continue on a denied or partial item, and how does a retry target
  only the inspected, authorized remainder?
  - Finding: one `devkit worktree start` item ends in one of five classes
    (`MAT-git-operator-batch-dispatch-observation`): refused before creation, creation rolled back, created then failed
    before setup, created with a zero-exit setup or sync warning, or not dispatched because host approval was denied.
    Items are independent only while they share an unchanged retained base; a moved or dirty base, a host permission
    refusal or a CLI that cannot run at all affects every later item. Recommended: continue past an item-local outcome,
    stop at a shared blocker, and retry only the items the Host names from the returned state.

## 3. Proposed Design & Impact

The recommended design below is pending the user's answers to this Planning round.

- **List form**: a dispatch MAY carry a finite, exact list of `prepare-worktree` items. Each item repeats every field
  of a single job (operation, absolute repository/base/worktree, Unit/branch, refs, intended_effects, authority,
  allowed_boundaries, writers_quiesced, expected_checks) and has a distinct branch, worktree path and Unit. All items
  name the same retained base and base ref. Authority covers only the listed items. Other operations stay one job
  per dispatch, because each integration or handoff changes the state the next job depends on.
- **Execution**: the operator runs items one at a time in the listed order, each through the existing guarded
  `prepare-worktree` procedure, with its own refresh before mutation and, on Codex, its own approval request.
- **Stop rule**: after an item-local outcome (a refusal or failure of that item's branch, path or setup), the
  operator records it and continues with the next item. After a shared blocker (the retained base ref moved or the
  base is dirty, host approval refused or unavailable, or the CLI cannot run for a reason no item owns) it stops and
  returns every later item as not attempted, with a null `cli_result`.
- **Return**: one role message whose `items` list holds, per item, the single-job result
  `PROP-git-operator-result-readiness` defines (original CLI status, exit and effects; host permission; worker-input
  readiness with exact dirty paths; next actor), plus the `not_attempted` items. The batch status uses the same three
  role statuses: `completed` only when every item is completed; otherwise `needs_input` when any remainder needs a
  Host decision, else `failed`. No `partial` status is added.
- **Retry**: the Host verifies the returned per-item state against current CLI/Git observations (or dispatches
  `inspect-recovery`) and dispatches a new list naming only the remaining items it still authorizes, with current
  refs. A completed item is never repeated. For a retained worktree with `WORKTREE_SETUP_FAILED` or a rerunnable
  `WORKTREE_SYNC_FAILED`, a retry item MAY name the warning's exact `[FIX]` in that worktree as its intended effect
  (pending Q4); other remainders return to the Host.
- **Documents**: the git-operator contract (Input, Procedure, Return), `git-operator-dispatch.md` (list form, stop rule,
  acceptance and retry), `git-operator-operations.md` (`prepare-worktree` list and setup remainder),
  `spec-delegate/references/payload.md` (the git-operator row: repeat fields per item), `CAP-DLV-delivery-workflows`
  §4.6.1 (EARS rules for the list) and `test_git_operator.py` (wording checks). `CAP-WT-task-worktrees` and
  `packages/devkit` do not change.

Assumptions (from `PROP-git-operator-result-readiness`, which is in parallel Planning):

1. Its per-job result keeps the three role statuses and the original CLI status, exit and effects, and adds host
   permission, worker-input readiness with exact dirty paths and the next actor as separate fields. This proposal
   reuses that shape per item unchanged; if it lands a different shape, the batch wraps that shape.
2. It does not change the `prepare-worktree` or handoff interface (its Q2); otherwise the setup-remainder retry follows
   the changed interface.

Acceptance checks (from the parent's verification candidates):

| ID | Given | When | Then |
| --- | --- | --- | --- |
| GOP-05 | An authorized finite preparation list with one denied or partial item | A batch stops or continues within its stated policy | Each item's original CLI result and completed and remaining effects are retained; retries target only inspected authorized remainders. |
| GOP-06 | A request for production edits, semantic conflict resolution or broader authority | The operator receives the job | It returns that work to the Host or implementer and performs no such mutation. |

GOP-05 is checked by contract wording tests and an isolated fixture or replay of a list with one refused item and one
setup-warning item, reported apart from live runs (`MAT-git-operator-batch-dispatch-observation`); no live partial
batch is required.

### Non-goals

- **Scope Excluded**: a daemon, global repository lock or autonomous scheduler.
- **Scope Excluded**: operator source authoring, approval grants, force operations or arbitrary remote deletion.
- **Scope Excluded**: unmeasured token, cost or latency savings.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-git-operator-batch-preparation`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
