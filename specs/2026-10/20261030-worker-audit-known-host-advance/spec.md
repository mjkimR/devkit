---
id: SPEC-worker-audit-known-host-advance
title: Stop requiring an unchanged base checkout in worker validation
summary: Drop the base-checkout HEAD and status equality from worker validation and require each returned turn to add its own worker envelope, so integrations and other sessions need not wait for a running worker; a partial committed escape into the base is an accepted residual.
status: in-progress
created: 2026-10-30
decomposed_from: PROP-git-operator-pilot-follow-up
related_capabilities: [CAP-DLV-delivery-workflows]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-worker-audit-known-host-advance] Stop requiring an unchanged base checkout in worker validation

## 1. Problem Statement & Motivation

Handed off from proposal PROP-worker-audit-known-host-advance on 2026-10-30.
- **Preserved Materials**: `docs/materials/2026-10/20261030-worker-audit-known-host-advance`

The exact-base observation rule caused unnecessary serialization in the resource-indexer consumer pilot
(`MAT-git-operator-consumer-pilot`): the Host held independent Planning integrations while a Development worker ran,
solely to preserve its recorded base HEAD. The worker reference (`spec-delegate/references/worker.md`) requires the
base checkout's status and HEAD to match the pre-spawn record, and the payload reference (`payload.md`) asks the Host
to record both before spawning; `devkit spec worker inspect` only reports the base checkout's HEAD and dirty paths as
information.

The equality exists to catch a worker write that escapes into the base checkout, because a worker's default cwd may
be the base checkout (`MAT-base-observation-options`). In this repository on 2026-10-30, another session committed to
`main` while a Development worker ran; the Host validated the range with `devkit spec worker inspect --base
<accepted>` without issue.

The worker's own range audit, one explicit envelope condition and the existing dirty-base refusals name every worker
escape except a partial committed one, so the equality goes without a replacement mechanism
(`ADR-drop-the-base-checkout-equality-from-worker-validation`). Escapes surface as follows:

- A full escape (the whole turn, its `worker` envelope included, committed in the base checkout): the new condition
  "`<returned>` adds this turn's `worker` envelope, absent at `<accepted>`" fails. Inspection alone does not catch it
  on a later turn, because it derives `head` from the latest envelope on the branch and re-audits the previous turn.
- An uncommitted write in the base checkout: handoff refuses (`SPEC_HANDOFF_BASE_DIRTY`) and integration refuses
  (`WORKTREE_BASE_DIRTY`).
- A partial committed escape (some worker commits on the base branch, the rest on its branch): no check names it. The
  user accepted it as an exception to "a defect must not stay hidden"; it needs several commands of one turn to miss
  the worktree cwd, and none has been observed.

## 2. User Stories

- **US-1**: As a Host orchestrating Development workers, I want worker validation to stop comparing the base checkout
  with a pre-spawn record, so that my own integrations and other sessions' commits to the base branch proceed while a
  worker runs.
- **US-2**: As a Host validating a returned turn, I want an explicit condition that the returned head adds this turn's
  own `worker` envelope, so that a turn committed entirely in the base checkout still fails validation.

## 3. Non-Goals

1. **Scope Excluded**: a global repository lock or autonomous scheduler.
2. **Scope Excluded**: treating a base advance as worker authorship, write permission or a skip of the final
   integration checks.
3. **Scope Excluded**: a declaration record of Host advances, a base-advance window in inspection, or a commit-gate
   branch check.
4. **Scope Excluded**: changing integration's dirty-base refusal or its handling of moved targets (the sibling unit
   integration-merge-moved-target owns that).
5. **Scope Excluded**: any change to `devkit spec worker inspect` (its checks, exit codes or `base_checkout`
   observation) or other code.
6. **Scope Excluded**: a follow-up draft for the partial committed escape. **When to Reconsider**: if such an escape is
   observed, the follow-up is a commit-gate check that refuses a base-checkout commit touching a path an active task
   worktree's unit owns.
7. **Scope Excluded**: rewriting completed specs or earlier materials that restate the equality; they stay as history.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The worker and payload references drop the base equality and add the turn's own envelope

- **Given** the spec bundle's `spec-delegate/references/worker.md` and `payload.md`
- **When** `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py` runs
- **Then** neither file requires a pre-spawn record of the base checkout or an unchanged base checkout status or HEAD
  (no block of either names the base checkout together with "before spawning" or "status and HEAD"); one `worker.md`
  condition requires `<returned>` to add this turn's `worker` envelope, absent at `<accepted>`; the ancestry, worktree
  HEAD, write-scope and clean-worktree conditions remain; and the test exits `0`.

### [AC-02] The Living Spec states the dropped equality and the accepted residual

- **Given** `CAP-DLV-delivery-workflows`, `ADR-drop-the-base-checkout-equality-from-worker-validation` and
  `ADR-orchestration-workers`
- **When** the reconcile review of this unit checks them
- **Then** the capability's acceptance requirements name the turn's own `worker` envelope instead of an unchanged
  base, its base-checkout observation names no Host comparison with a saved state, the promoted ADR names the two
  superseded clauses of `ADR-orchestration-workers`, and `ADR-orchestration-workers` carries one pointer line to the
  promoted ADR naming both superseded clauses, its decision text otherwise unchanged.

### [AC-03] A base advance after spawning never enters or blocks the audited range

- **Given** a unit branch whose audit base is A, a commit B made on the base branch in the base checkout after the
  worker's range started (Host, foreign or unknown author), and a returned head C that adds the turn's `worker`
  envelope
- **When** `devkit spec worker inspect` runs in the linked worktree
- **Then** the audited range is A..C, B's paths are absent from `changed_paths`, the `base_checkout` observation
  reports B as its HEAD, and the exit code is `0`.

## 5. Assumptions

- `MAT-git-operator-consumer-pilot` keeps its ID when its proposal hands off; the sibling proposal
  integration-merge-moved-target is cited as plain text because its proposal file is deleted at its own handoff.
- AC-03 restates the proposal's GOP-08 for this unit. A dirty base checkout and real conflicts stop at handoff or
  integration through their existing refusals, which this unit leaves unchanged; AC-03 pins only the inspection side
  with one characterization test beside the existing linked-worktree test, because no current test advances the base
  HEAD under a worker range. No code changes.
- The pointer line in `ADR-orchestration-workers` is a reference repair (constitution §2), so that ADR's decision
  text and frontmatter stay as they are; the promoted ADR carries no `supersedes` field, because superseding the alias
  of the committed-results decision would also retire the worker's Git actions and the rest of that decision.
