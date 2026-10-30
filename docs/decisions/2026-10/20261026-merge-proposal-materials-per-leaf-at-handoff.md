---
id: ADR-merge-proposal-materials-per-leaf-at-handoff
title: Merge proposal materials per leaf at handoff
summary: For a handoff whose dated materials directory already exists, we merge proposal materials per leaf after a full lstat-based preflight and refuse any differing file, type or symbolic-link collision, to keep pre-existing files intact, accepting an undetected same-path write window.
proposal: SPEC-merge-proposal-materials-at-handoff
status: accepted
created_at: 2026-10-26
---

# [ADR-merge-proposal-materials-per-leaf-at-handoff] Merge proposal materials per leaf at handoff

- **Status**: Accepted
- **Date**: 2026-10-26

---


## 1. Context & Problem Statement

The proposal handoff moves `materials/` and the carried bundle files into the dated directory
`docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`. Its preflight refuses the whole handoff with
`SPEC_PROPOSAL_TARGET_EXISTS` when that directory exists, even when no file inside collides. The relocation code
moves whole directories, records the destination as written and removes it on roll-back, and registers one
directory origin for link rewriting; none of that is safe once the destination holds files the handoff did not
create. The refusal's fix directive tells an agent to move or remove the destination path, which deletes the
files the user wanted to keep.

## 2. Decision Drivers

- No pre-existing destination file loses or changes bytes, on success, on refusal or on roll-back.
- Every refusal happens in preflight, before any proposal, ADR, spec or material mutation.
- Links are never followed and the allowed roots do not grow.
- The CLI and native handoff share one plan and one result.
- Output carries only what changes the agent's next step.
- Implementation cost proportionate to a narrow trigger (a same-day handoff after materials were written early).

## 3. Considered Options

### Option 1: Per-leaf guarded merge (Selected)

Preflight plans every leaf against the existing destination and refuses any conflict; the move writes only paths
that were absent. Covers the trigger without manual recovery; adds a merge plan and per-leaf roll-back records.

### Option 2: Keep the refusal and change only the fix directive

Size S: the directive tells the agent to move the destination's files into the proposal's `materials/` and rerun.
Leaves the manual recovery on every occurrence.

### Option 3: No-clobber leaf moves on top of Option 1

`os.link` plus `os.unlink` and `O_EXCL` copies would also catch a file written at a planned path between preflight
and move. More platform-dependent code for a window the ADR writes already accept.

## 4. Decision Outcome

Chosen option: Option 1, because it keeps pre-existing files intact and refuses before writing (first two drivers)
while removing the manual recovery; Option 3 is rejected on cost, since same-path writes during a handoff are not
expected.

- **Plan**: one set of planned leaves from the `materials/` leaves and the carried extras, checked against the
  destination in one pass. An absent subtree moves whole; an existing real directory is descended into; a file is a
  leaf move. Non-symlink `JUNK_FILES` are dropped on the source side and ignored on the destination side. The clash
  rule between carried extras and `materials/` paths is unchanged.
- **Duplicates and conflicts**: a path that is a regular file on both sides by `lstat` with identical bytes is a
  duplicate; the destination bytes stay and the proposal copy is dropped. Differing bytes, a file against a
  directory, any symbolic link on either side at the same path (equal link text included) and any non-regular file
  are conflicts, refused with `SPEC_PROPOSAL_TARGET_EXISTS`. Links are never followed.
- **Containment**: the destination and every existing directory on the way to a planned leaf must be a real
  directory by `lstat`; a symbolic link at or above a planned path is a conflict refused in preflight.
- **Pre-existing paths**: no pre-existing file or directory is recorded as written or moved, on the same file system
  or across file systems (`EXDEV`); directory creation records only directories the handoff created. Roll-back
  therefore never removes or moves a pre-existing path.
- **Link rewriting**: the relocation plan registers a file origin per moved leaf and a directory origin only for a
  subtree the handoff created whole, so a pre-existing Markdown file changes only in links that pointed into the
  proposal.
- **Concurrent changes**: no guarantee. A file written at a planned path between preflight and its move may be
  replaced, as for the ADR writes; the contract states this window.
- **Reporting**: the handoff result and its JSON output carry whether the materials merged into an existing
  directory and the dropped duplicate paths; no NOTICE.
- **Refusal directive**: a merge conflict carries its own fix naming the source path, the destination path and the
  collision kind, telling the agent to reconcile that one path; it never directs removal of the destination
  directory. The error code stays `SPEC_PROPOSAL_TARGET_EXISTS`.

## 5. Consequences

- Positive: a handoff whose dated materials directory already exists succeeds without manual moves when nothing
  conflicts, and a refusal leaves both trees and the workspace unchanged.
- Negative: two equal symbolic links need manual reconciliation; a same-path write during the handoff can be lost.
- Risk: a next-day handoff after the same early write still splits materials across two dated directories; same-slug
  directories of other dates are not searched.
- Follow-up: if a lost same-path write is ever observed, revisit Option 3.

## 6. Confirmation

- Tests under `packages/devkit-spec/tests/` for the proposal handoff: disjoint merge, nested disjoint files,
  identical duplicates, differing bytes, file/directory collisions, symbolic links (including equal link text and a
  link at or above a planned path), carried extras against pre-existing files, junk on both sides, `EXDEV` and a
  failure injected mid-move keeping every pre-existing path byte-identical, and a preflight refusal leaving source
  and destination unchanged with no spec or ADR created.
- `CAP-DLV-proposal-planning` states the merge rules, the residual window and the result fields; review checks it
  against the tests.
