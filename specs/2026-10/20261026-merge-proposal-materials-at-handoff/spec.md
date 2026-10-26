---
id: SPEC-merge-proposal-materials-at-handoff
title: Merge existing proposal materials during handoff
summary: Allows proposal handoff to merge materials per leaf into an existing destination after a complete lstat-based collision preflight, preserving existing files and refusing conflicting content or symbolic links.
status: planned
created: 2026-10-26
related_capabilities:
  - CAP-DLV-proposal-incubation
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-merge-proposal-materials-at-handoff] Merge existing proposal materials during handoff

## 1. Problem Statement & Motivation

Handed off from proposal PROP-merge-proposal-materials-at-handoff on 2026-10-26.

The Development handoff of PROP-persistent-python-facts-cache created its worktree but refused to graduate the
proposal with `SPEC_PROPOSAL_TARGET_EXISTS`. Measurements written earlier the same day already occupied the dated
materials directory `docs/materials/2026-10/20261022-persistent-python-facts-cache/`, while the proposal held a
different file, `materials/design.md`. The preflight refuses the whole handoff when that directory exists, even when
no file inside it collides, and its fix tells the agent to move or remove the directory, which deletes files the user
wanted to keep.

`ADR-merge-proposal-materials-per-leaf-at-handoff` decides the replacement: a per-leaf guarded merge planned in
preflight. This spec states its observable contract.

## 2. User Stories

- **US-1**: As an agent handing off a proposal, I want the handoff to merge the proposal's materials into a dated
  materials directory that already exists, so that I do not have to move files by hand when nothing conflicts.
- **US-2**: As a developer, I want every conflict refused before anything is written and every pre-existing file kept
  byte-identical on success, refusal and roll-back, so that a handoff never loses material I wrote earlier.

## 3. Non-Goals

1. **Scope Excluded**: overwrite flags and automatic resolution of differing content.
2. **Scope Excluded**: no-clobber moves or detection of a file written at a planned path between preflight and its
   move (the residual window, `ADR-merge-proposal-materials-per-leaf-at-handoff` Option 3).
3. **Scope Excluded**: searching same-slug materials directories of other dates, cross-file-system transaction
   infrastructure and changes to the facts-cache feature.
4. **Scope Excluded**: any relaxation of the ADR, document ID, alias or spec bundle collision checks; only the dated
   materials directory may pre-exist.

## 4. Acceptance Criteria & Behavioral Contracts

In these scenarios `<dest>` is `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` for the handoff date, `materials/` is
the proposal bundle's materials directory and "carried extras" are the other bundle files the handoff moves into
`<dest>`. "Pre-existing" means present in `<dest>` before the handoff started.

### [AC-01] Disjoint materials merge into an existing directory

- **Given** `<dest>` is a real directory holding `bench.json` and `nested/run-1.txt`, and the proposal holds
  `materials/design.md`, `materials/nested/run-2.txt` and a carried extra `notes.md`
- **When** the agent runs `devkit spec proposal handoff <slug>`
- **Then** the command exits `0`, `<dest>` holds all five files, the two pre-existing files are byte-identical,
  `HandoffResult.materials` is `<dest>`, `materials_merged` is `true` and `dropped_duplicates` is empty.

### [AC-02] Byte-identical duplicates keep the destination copy

- **Given** `<dest>/same.md` and `materials/same.md` are regular files with identical bytes (by `lstat` on both
  sides)
- **When** the handoff runs
- **Then** it succeeds, `<dest>/same.md` keeps its bytes and inode, the proposal copy is removed with the proposal,
  and `dropped_duplicates` lists `<dest>/same.md` workspace-relative; a carried extra identical to a pre-existing file
  is dropped the same way.

### [AC-03] Conflicts are refused in preflight with a merge-specific fix

- **Given** one of these at the same relative path: regular files with differing bytes; a file against a directory;
  a symbolic link on either side, equal link text included; a non-regular file on either side; a symbolic link or a
  file at a directory on the way to a planned path (`<dest>` itself included); or a carried extra against a
  pre-existing file with differing bytes
- **When** the handoff runs
- **Then** it raises `SPEC_PROPOSAL_TARGET_EXISTS` (exit `2` on the CLI), its `[TARGET]` lists the destination paths
  and its fix names the first conflict's source path, destination path and collision kind
  (`different-content`, `file-directory`, `symbolic-link` or `non-regular`) and never directs removal of `<dest>`;
  the source and destination trees are unchanged, and no spec bundle, ADR or material was written.

### [AC-04] Junk is ignored on both sides

- **Given** non-symlink operating-system junk (`.DS_Store`, `Thumbs.db`, `desktop.ini`) in `materials/` at the same
  path as junk in `<dest>`, next to a disjoint material file
- **When** the handoff runs
- **Then** it succeeds, the destination junk is unchanged and the proposal junk is removed with the proposal.

### [AC-05] Roll-back never touches pre-existing paths

- **Given** a merge handoff whose second leaf move fails (on the same file system, or across file systems where every
  move copies, `EXDEV`), or whose failure happens after every move
- **When** the handoff rolls back
- **Then** it raises `SPEC_PROPOSAL_HANDOFF_FAILED` (or the advisory error itself), every pre-existing file and
  directory of `<dest>` exists byte-identical, the moved leaves are back in `materials/`, and rerunning the handoff
  after the cause is removed succeeds.

### [AC-06] Links of pre-existing files resolve from where they are

- **Given** a pre-existing `<dest>/index.md` with a link `[bench](bench.json)` and a link into the proposal, and a
  moved `materials/design.md` with a relative link written for `materials/`
- **When** the handoff runs
- **Then** `<dest>/index.md` changes only in its link into the proposal, and the moved file's links resolve as they
  did from `materials/`.

### [AC-07] The merge is reported in result fields only

- **Given** a handoff that merged into a pre-existing `<dest>`
- **When** it is run with `--format json`, without `--format json`, and through the composed `--effort` handoff
- **Then** the JSON handoff object carries `materials_merged: true` and `dropped_duplicates` (workspace-relative
  destination paths), the text output prints `[MATERIALS: <dest> merged=yes]` and one
  `[DROPPED_DUPLICATE: <path>]` per duplicate, and no notice is added for the merge; a handoff without a pre-existing
  `<dest>` reports `materials_merged: false`, `dropped_duplicates: []` and `[MATERIALS: <dest>]` as before.

### [AC-08] The Living Spec states the merge contract

- **Given** `CAP-DLV-proposal-incubation`
- **When** it is read after this change
- **Then** its validation rule, handoff step 5, output section and error table state the merge rules, the residual
  window for same-path writes during the handoff and the result fields, and no longer list an existing materials
  directory as a refusal on its own.

## 5. Assumptions

- **Duplicate paths are destination paths**: `dropped_duplicates` lists the workspace-relative path of the kept
  destination file, because the proposal copy no longer exists after the handoff.
- **Text rendering**: `merged=yes` is added to the existing `[MATERIALS: ...]` line only when merged, and duplicates
  get their own `[DROPPED_DUPLICATE: ...]` lines, so a handoff without a merge prints exactly what it printed before.
- **Conflict reporting**: the preflight collects every conflict; the message and `[DETAIL]` list each one
  (`<source> -> <destination>: <kind>`), `target_files` holds every destination path, and the fix names the first
  conflict in path order and says the others in `[DETAIL]` are reconciled the same way.
- **Subtree without material**: an absent source subtree holding no material (only junk or empty directories) is not
  moved, as `materials/` itself is not moved without material; an absent subtree with material moves whole.
- **Containment above `<dest>`**: directories above `<dest>` keep the existing resolve-based outside-workspace check;
  the new `lstat` checks start at `<dest>`.

## 6. Source Proposal Notes

### Technical Spike Questions

- **Q1**: How should the merge plan represent directories, distinct files and byte-identical duplicate files while
  preserving target containment, non-symlink paths and existing document/ADR collision checks?
- **Q2**: How does preflight distinguish file/directory and symbolic-link collisions and report a differing-content
  conflict before any proposal, ADR, spec or material mutation occurs?
- **Q3**: How should failure recovery preserve already-existing files without promising filesystem transactions
  for unrelated runtime I/O failures? Confirm the behavior in CLI and native handoff paths.

The answers are the decisions of `ADR-merge-proposal-materials-per-leaf-at-handoff` (per-leaf plan, `lstat`
conflict rules, no pre-existing path in roll-back records, per-file link origins) and AC-01 to AC-07.

### Lifecycle & Retirement Criteria

Development completes when both handoff transports use the same guarded merge plan and the success and refusal tests
and the Living Spec reflection pass.
