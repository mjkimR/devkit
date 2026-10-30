---
id: PADR-composed-handoff-commits-its-own-transaction
title: Composed handoff commits its own transaction
summary: "For the composed proposal handoff, we commit the CLI-generated handoff transaction in the fresh dev worktree as one direct child of the reviewed base, to give workers clean committed input without a Host commit step, accepting a commit-gate refusal as a stopped handoff."
proposal: PROP-git-operator-result-readiness
status: draft
created_at: 2026-10-30
---

# [PADR-composed-handoff-commits-its-own-transaction] Composed handoff commits its own transaction

- **Status**: Draft
- **Date**: 2026-10-30

---

## 1. Context & Problem Statement

The composed handoff (`devkit spec proposal handoff <slug> --effort`, and `accept --mode accept_and_handoff`) creates
`dev-<slug>` at the reviewed base head, checks that the worktree is clean, then writes the spec bundle, promotes
ADRs, moves materials, rewrites references, removes the proposal and registers the scope. It exits 0 with
`status: handed_off` and commits nothing. A worker's range starts at the worktree HEAD after the Host's own commits,
and a worker's write scope excludes the proposal deletion, ADR promotion and material moves, so every handoff needs
a Host commit before a worker starts. The composed acceptance already commits its exact service-created delta.
`MAT-git-operator-handoff-commit-evidence` records four such Host commits on 2026-10-30, each staging every changed
path without judgment.

## 2. Decision Drivers

- A worker starts from clean committed input without an unnamed Host step.
- The commit holds only what the handoff wrote; no unrelated work enters it.
- Lifecycle checks stay light: no new command, record or approval.
- A refused or rewritten commit stays observable; nothing is rolled back silently.

## 3. Considered Options

- **A. The composed handoff commits its transaction (selected)**: removes the Host step; the worktree was verified
  clean at the reviewed head, so the delta is exactly the handoff's own.
- **B. Keep the handoff write-only; the result names the dirty paths and the Host as next actor**: no code change,
  but the Host commit stays on every handoff with a Host-chosen message.
- **C. Commit in every handoff, plain `handoff <slug>` included**: the plain form runs in a `dev-<slug>` checkout that
  may hold other work, so it would commit unrelated changes or refuse.

## 4. Decision Outcome

Option A, because it meets the first two drivers at the cost of one commit step that mirrors the composed acceptance.

- After the handoff and scope registration succeed, the composed handoff stages the delta `git status` reports (the
  worktree was clean at the reviewed head before the handoff) and commits once with the subject
  `spec: hand off <slug> to Development`, under the normal commit gate.
- It verifies after the commit that HEAD's single parent is the reviewed base head and the worktree is clean, and
  reports HEAD as read after `git commit` returns (a metadata-rewriting post-commit hook changes the SHA).
- On a refused commit (the gate or any other `git commit` failure) it keeps the handoff's writes in place,
  uncommitted, and returns a stopped handoff (`status: needs_recovery`, exit `1`, `SPEC_HANDOFF_COMMIT_REFUSED`) with
  the commit output, the exact dirty paths and a next action instead of a next command; it rolls nothing back.
- The plain `devkit spec proposal handoff <slug>` stays write-only.

## 5. Consequences

- The Host no longer commits the handoff transaction; a git-operator handoff result can report clean committed
  worker input.
- The post-handoff link check, when the result carries unresolved links or rewrites outside the new spec and
  promoted ADRs, becomes a later Host commit on the same branch, before a worker starts, instead of part of the
  handoff commit.
- A refused commit leaves a dirty worktree that the Host repairs and commits; a rerun of the composed handoff
  refuses that worktree (`SPEC_HANDOFF_WORKTREE_CONFLICT`), as it does today for any changed checkout.
- Follow-up: if a project's commit-message policy rejects the fixed subject, the refusal path applies; add a
  configurable subject only when such a policy is observed.

## 6. Confirmation

Integration tests under `packages/devkit-spec/tests/integration/features/delivery/` cover the committed handoff
(single parent, clean worktree, reported HEAD after a rewriting hook) and the refused commit (stopped result, dirty
paths kept, exit `1`, no next command). Review checks the `CAP-DLV-proposal-planning` composed handoff contract.
