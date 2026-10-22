---
id: PADR-parse-memo-location-and-format
title: Parse memo location and format
summary: For storing the parse memo, we write one JSON file at .devkit/transient/spec/document-index.json of each worktree, only where .devkit/transient/ exists, to keep it ignored, per worktree and safe to load, accepting no memo in unsynced workspaces.
proposal: PROP-document-index-cache
status: draft
created_at: 2026-10-22
---

# [PADR-parse-memo-location-and-format] Parse memo location and format

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

The parse memo (`PADR-content-keyed-document-parse-memo`) needs a file that Git ignores, that belongs to one worktree,
and that loading cannot turn into code execution. `.devkit/transient/` is already the per-checkout, Git-ignored state
directory: `.devkit/.gitignore`, which a writing sync seeds, ignores `/transient/` (`CAP-DIST-workspace-ownership`),
devkit-dist keeps its journal, lock and `deployed.json` there, and devkit-agt its work units
(`.devkit/transient/work/`). Every Git worktree has its own working tree, so its own `.devkit/transient/`. The
repository `.gitignore` ignores neither `.devkit/` nor any cache directory at the root.

Frontmatter values include `datetime.date` (375 of them in this repository), which plain JSON cannot hold.

## 2. Decision Drivers

- Never shown by `git status`, never staged, never read by the rules (they skip Git-ignored files).
- One memo per worktree, with no cross-worktree sharing to coordinate.
- Loading a damaged or planted file yields at worst wrong-shaped data, which validation rejects, never code execution.
- Load cost small next to the 300 ms it saves.

## 3. Considered Options

- **`.devkit/transient/spec/document-index.json`**: ignored by the seeded `.devkit/.gitignore`, per worktree, follows
  the existing transient convention; absent in a workspace that was never synced.
- **The worktree's Git directory** (`<git-dir>/devkit-spec-document-index.json`): ignored without any `.gitignore`, but
  needs the Git directory resolved on every call and puts derived data where devkit-spec otherwise keeps only the scope
  token.
- **A user cache directory** (`~/.cache/devkit/...`, keyed by worktree path): outside the workspace, survives worktree
  removal as garbage and needs its own cleanup.
- **Format: pickle**: fastest (about 5 ms) and keeps every type, but loading a crafted file runs code.
- **Format: JSON with tagged dates**: about 3 ms to decode and 3 to 6 ms to rebuild the documents; values stay plain
  data.

## 4. Decision Outcome

Chosen options: **`.devkit/transient/spec/document-index.json`** and **JSON**, because they meet the ignore,
per-worktree and safe-load drivers with no new ignore rule and a load cost under 10 ms.

- **Location**: `<root>/.devkit/transient/spec/document-index.json`, `<root>` being the root the load indexes. The memo
  is read and written only when `<root>/.devkit/transient/` exists as a directory and is not a symbolic link;
  otherwise the load behaves as today and creates no file or directory. `spec/` is created on the first write.
- **Format**: one UTF-8 JSON object with `version`, `fingerprint` and `entries` (path to digest and stored result).
  `date` and `datetime` values are tagged objects decoded back to the same type. A file whose parse result holds any
  other value JSON cannot represent is not stored and is parsed on each load.
- Deleting the file is always safe: the next load rebuilds it.

## 5. Consequences

- Positive: no repository `.gitignore` change and no new ignored path; the memo follows the checkout, so worktrees,
  clones and branch switches never share it.
- Negative: a workspace without `.devkit/transient/` (never synced, or a test fixture) gets no memo. A workspace that
  installs the `spec` bundle has been synced, so the cost falls on bare fixtures only.
- Negative: about 1 MB on disk per worktree for this repository's 693 files.
- Risk: a project that removes `/transient/` from `.devkit/.gitignore` sees the memo as an untracked file; that edit
  already exposes the sync journal and lock the same way.

## 6. Confirmation

- Tests: a workspace without `.devkit/transient/` gets no memo file; a symbolic link in its place is not followed; a
  memo holding dates round-trips to equal frontmatter.
- Review: `CAP-DOCS-document-model` names the path and states that deleting it is safe.
