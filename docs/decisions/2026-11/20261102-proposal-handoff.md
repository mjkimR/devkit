---
id: ADR-proposal-handoff
title: Proposal handoff merges materials per leaf and commits its composed transaction
summary: "For the proposal handoff, we merge materials per leaf after an lstat preflight that refuses any collision, and commit the composed handoff's own delta as one child of the reviewed base, to keep existing files intact and give workers committed input, accepting a same-path write window."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-merge-proposal-materials-per-leaf-at-handoff
  - ADR-composed-handoff-commits-its-own-transaction
---

# [ADR-proposal-handoff] Proposal handoff merges materials per leaf and commits its composed transaction

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `CAP-DLV-proposal-planning`

---

## 1. Context & Problem Statement

The proposal handoff moves `materials/` and the carried bundle files into the dated directory
`docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`. A preflight that refuses the whole handoff with
`SPEC_PROPOSAL_TARGET_EXISTS` when that directory exists blocks it even when no file inside collides. Relocation code
that moves whole directories, records the destination as written and removes it on roll-back, and registers one
directory origin for link rewriting is not safe once the destination holds files the handoff did not create. A fix
directive telling an agent to move or remove the destination path deletes the files the user wanted to keep.

The composed handoff (`devkit spec proposal handoff <slug> --effort`, and `accept --mode accept_and_handoff`) creates
`dev-<slug>` at the reviewed base head, checks that the worktree is clean, then writes the spec bundle, promotes ADRs,
moves materials, rewrites references, removes the proposal and registers the scope. A worker's range starts at the
worktree HEAD after the Host's own commits, and a worker's write scope excludes the proposal deletion, ADR promotion
and material moves, so a handoff that commits nothing needs a Host commit before a worker starts. The composed
acceptance already commits its exact service-created delta. `MAT-git-operator-handoff-commit-evidence` records four
such Host commits on 2026-10-30, each staging every changed path without judgment.

---

## 2. Decision Drivers

### Materials merge
- No pre-existing destination file loses or changes bytes, on success, on refusal or on roll-back.
- Every refusal happens in preflight, before any proposal, ADR, spec or material mutation.
- Links are never followed and the allowed roots do not grow.
- The CLI and native handoff share one plan and one result.
- Output carries only what changes the agent's next step.
- Implementation cost proportionate to a narrow trigger (a same-day handoff after materials were written early).

### Handoff commit
- A worker starts from clean committed input without an unnamed Host step.
- The commit holds only what the handoff wrote; no unrelated work enters it.
- Lifecycle checks stay light: no new command, record or approval.
- A refused or rewritten commit stays observable; nothing is rolled back silently.

---

## 3. Considered Options

### Materials merge
- **Per-leaf guarded merge** (selected in `ADR-merge-proposal-materials-per-leaf-at-handoff`): preflight plans every
  leaf against the existing destination and refuses any conflict; the move writes only paths that were absent. Covers
  the trigger without manual recovery; adds a merge plan and per-leaf roll-back records.
- **Keep the refusal and change only the fix directive** (rejected in
  `ADR-merge-proposal-materials-per-leaf-at-handoff`): size S: the directive tells the agent to move the destination's
  files into the proposal's `materials/` and rerun. Leaves the manual recovery on every occurrence.
- **No-clobber leaf moves on top of the per-leaf merge** (rejected in
  `ADR-merge-proposal-materials-per-leaf-at-handoff`, on cost, since same-path writes during a handoff are not
  expected): `os.link` plus `os.unlink` and `O_EXCL` copies would also catch a file written at a planned path between
  preflight and move. More platform-dependent code for a window the ADR writes already accept.

### Handoff commit
- **The composed handoff commits its transaction** (selected in `ADR-composed-handoff-commits-its-own-transaction`,
  by the user at Planning): removes the Host step; the worktree was verified clean at the reviewed head, so the delta
  is exactly the handoff's own.
- **Keep the handoff write-only; the result names the dirty paths and the Host as next actor** (rejected in
  `ADR-composed-handoff-commits-its-own-transaction`): no code change, but the Host commit stays on every handoff with a
  Host-chosen message.
- **Commit in every handoff, plain `handoff <slug>` included** (rejected in
  `ADR-composed-handoff-commits-its-own-transaction`): the plain form runs in a `dev-<slug>` checkout that may hold
  other work, so it would commit unrelated changes or refuse.

---

## 4. Decision Outcome

We adopt the per-leaf guarded materials merge, because it keeps pre-existing files intact and refuses before writing
while removing the manual recovery, and a composed handoff that commits its own transaction, because it gives workers
clean committed input with one commit step that mirrors the composed acceptance.

### Materials merge
- **Plan**: one set of planned leaves from the `materials/` leaves and the carried extras, checked against the
  destination in one pass. An absent subtree moves whole; an existing real directory is descended into; a file is a
  leaf move. Non-symlink `JUNK_FILES` are dropped on the source side and ignored on the destination side. The clash
  rule between carried extras and `materials/` paths is unchanged. (ADR-merge-proposal-materials-per-leaf-at-handoff)
- **Duplicates and conflicts**: a path that is a regular file on both sides by `lstat` with identical bytes is a
  duplicate; the destination bytes stay and the proposal copy is dropped. Differing bytes, a file against a directory,
  any symbolic link on either side at the same path (equal link text included) and any non-regular file are
  conflicts, refused with `SPEC_PROPOSAL_TARGET_EXISTS`. Links are never followed.
  (ADR-merge-proposal-materials-per-leaf-at-handoff)
- **Containment**: the destination and every existing directory on the way to a planned leaf must be a real directory
  by `lstat`; a symbolic link at or above a planned path is a conflict refused in preflight.
  (ADR-merge-proposal-materials-per-leaf-at-handoff)
- **Pre-existing paths**: no pre-existing file or directory is recorded as written or moved, on the same file system or
  across file systems (`EXDEV`); directory creation records only directories the handoff created. Roll-back therefore
  never removes or moves a pre-existing path. (ADR-merge-proposal-materials-per-leaf-at-handoff)
- **Link rewriting**: the relocation plan registers a file origin per moved leaf and a directory origin only for a
  subtree the handoff created whole, so the rewriting step changes a pre-existing Markdown file only in links that
  pointed into the proposal; the handoff's one other edit to a pre-existing file is the partial-supersession pointer
  of `CAP-DLV-proposal-lifecycle` (§4.1, step 4). (ADR-merge-proposal-materials-per-leaf-at-handoff)
- **Concurrent changes**: no guarantee. A file written at a planned path between preflight and its move may be
  replaced, as for the ADR writes; the contract states this window. (ADR-merge-proposal-materials-per-leaf-at-handoff)
- **Reporting**: the handoff result and its JSON output carry whether the materials merged into an existing directory
  and the dropped duplicate paths; no NOTICE. (ADR-merge-proposal-materials-per-leaf-at-handoff)
- **Refusal directive**: a merge conflict carries its own fix naming the source path, the destination path and the
  collision kind, telling the agent to reconcile that one path; it never directs removal of the destination directory.
  The error code stays `SPEC_PROPOSAL_TARGET_EXISTS`. (ADR-merge-proposal-materials-per-leaf-at-handoff)

### Handoff commit
- After the handoff and scope registration succeed, the composed handoff stages the delta `git status` reports (the
  worktree was clean at the reviewed head before the handoff) and commits once with the subject
  `spec: hand off <slug> to Development`, under the normal commit gate.
  (ADR-composed-handoff-commits-its-own-transaction)
- It verifies after the commit that HEAD's single parent is the reviewed base head and the worktree is clean, and
  reports HEAD as read after `git commit` returns (a metadata-rewriting post-commit hook changes the SHA).
  (ADR-composed-handoff-commits-its-own-transaction)
- On a refused commit (the gate or any other `git commit` failure) it keeps the handoff's writes in place,
  uncommitted, and returns a stopped handoff (`status: needs_recovery`, exit `1`, `SPEC_HANDOFF_COMMIT_REFUSED`) with
  the commit output, the exact dirty paths and a next action instead of a next command; it rolls nothing back.
  (ADR-composed-handoff-commits-its-own-transaction)
- The plain `devkit spec proposal handoff <slug>` stays write-only.
  (ADR-composed-handoff-commits-its-own-transaction)

---

## 5. Consequences

- **Positive**:
  - A handoff whose dated materials directory already exists succeeds without manual moves when nothing conflicts,
    and a refusal leaves both trees and the workspace unchanged. (ADR-merge-proposal-materials-per-leaf-at-handoff)
  - The Host no longer commits the handoff transaction; a git-operator handoff result can report clean committed
    worker input. (ADR-composed-handoff-commits-its-own-transaction)
- **Negative / Risks**:
  - Two equal symbolic links need manual reconciliation; a same-path write during the handoff can be lost.
    (ADR-merge-proposal-materials-per-leaf-at-handoff)
  - A next-day handoff after the same early write still splits materials across two dated directories; same-slug
    directories of other dates are not searched. (ADR-merge-proposal-materials-per-leaf-at-handoff)
  - The post-handoff link check, when the result carries unresolved links or rewrites outside the new spec and promoted
    ADRs, becomes a later Host commit on the same branch, before a worker starts, instead of part of the handoff
    commit. (ADR-composed-handoff-commits-its-own-transaction)
  - A refused commit leaves a dirty worktree that the Host repairs and commits; a rerun of the composed handoff refuses
    that worktree (`SPEC_HANDOFF_WORKTREE_CONFLICT`), as it does for any changed checkout.
    (ADR-composed-handoff-commits-its-own-transaction)
- **Follow-ups**:
  - If a lost same-path write is ever observed, revisit the no-clobber leaf moves.
    (ADR-merge-proposal-materials-per-leaf-at-handoff)
  - If a project's commit-message policy rejects the fixed subject, the refusal path applies; add a configurable
    subject only when such a policy is observed. (ADR-composed-handoff-commits-its-own-transaction)

---

## 6. Confirmation

- Tests under `packages/devkit-spec/tests/` for the proposal handoff: disjoint merge, nested disjoint files,
  identical duplicates, differing bytes, file/directory collisions, symbolic links (including equal link text and a
  link at or above a planned path), carried extras against pre-existing files, junk on both sides, `EXDEV` and a
  failure injected mid-move keeping every pre-existing path byte-identical, and a preflight refusal leaving source and
  destination unchanged with no spec or ADR created. (ADR-merge-proposal-materials-per-leaf-at-handoff)
- `CAP-DLV-proposal-lifecycle` states the merge rules, the residual window and the result fields; review checks it
  against the tests. (ADR-merge-proposal-materials-per-leaf-at-handoff)
- Integration tests under `packages/devkit-spec/tests/integration/features/delivery/` cover the committed handoff
  (single parent, clean worktree, reported HEAD after a rewriting hook) and the refused commit (stopped result, dirty
  paths kept, exit `1`, no next command). Review checks the `CAP-DLV-proposal-lifecycle` composed handoff contract.
  (ADR-composed-handoff-commits-its-own-transaction)
