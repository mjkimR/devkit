---
id: ADR-parse-memo-location-and-format
title: Parse memo location and format
summary: For storing the parse memo, we write one JSON file at .devkit/transient/spec/document-index.json of each worktree, only where .devkit/transient/ exists, to keep it ignored, per worktree and safe to load, accepting no memo in unsynced workspaces.
proposal: SPEC-document-index-cache
status: accepted
created_at: 2026-10-22
---

# [ADR-parse-memo-location-and-format] Parse memo location and format

- **Status**: Accepted
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

The parse memo (`ADR-content-keyed-document-parse-memo`) needs a file that Git ignores, that belongs to one worktree,
and that loading cannot turn into code execution. `.devkit/transient/` is already the per-checkout, Git-ignored state
directory: `.devkit/.gitignore`, which a writing sync seeds, ignores `/transient/` (`CAP-DIST-workspace-ownership`),
devkit-dist keeps its journal, lock and `deployed.json` there, and devkit-agt its work units
(`.devkit/transient/work/`). Every Git worktree has its own working tree, so its own `.devkit/transient/`. The
repository `.gitignore` ignores neither `.devkit/` nor any cache directory at the root.

Frontmatter values include `datetime.date` (375 of them in this repository), which plain JSON cannot hold. The strict
loader requires string keys only at the top level, so nested mappings may have integer, boolean, null or date keys,
which `json.dumps` silently turns into strings.

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
- **Format: JSON with tagged dates only**: about 3 ms to decode, but a nested non-string key is coerced to a string
  and a literal one-key mapping shaped like a tag decodes as a date.
- **Format: JSON with every container tagged**: lists and mappings become tagged objects and a mapping a list of
  key-value pairs, so no value is ambiguous; the frontmatter of all 637 documents decodes in 1.4 to 1.9 ms.

## 4. Decision Outcome

Chosen options: **`.devkit/transient/spec/document-index.json`** and **JSON with every container tagged**, because
they meet the ignore, per-worktree and safe-load drivers with no new ignore rule, a faithful round trip and a load cost
under 10 ms.

- **Location**: `<root>/.devkit/transient/spec/document-index.json`, `<root>` being the root the load indexes. The memo
  is used only when `<root>/.devkit/transient/` exists as a directory, neither it, `spec/` nor the memo path is a
  symbolic link, and the memo path resolves inside `<root>`; otherwise the load behaves as today and creates no file
  or directory. `spec/` is created on the first write.
  Superseded in part by `ADR-document-package`: the memo lives at `.devkit/transient/docs/document-index.json`.
- **Format**: one UTF-8 JSON object with `version`, `fingerprint` and `entries` (path to digest and stored result).
  Strings, booleans, integers, finite floats and null stay plain; every list, mapping, `datetime` and `date` is a
  one-key tagged object (a mapping as a list of key-value pairs, so any key type survives; `datetime` checked before
  `date`, with its UTC offset). A parse result holding any other value (a non-finite float, another type) is stored
  as an "unstorable" marker with its digest and parsed on each load.
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

- Tests: a workspace without `.devkit/transient/` gets no memo file; a symbolic link at `.devkit/transient/`,
  `spec/` or the memo path is not followed; frontmatter with a date, a naive `datetime`, an aware `datetime` (`Z` and
  `+09:00`), nested integer, boolean and null keys and a literal tag-shaped mapping round-trips to equal frontmatter,
  and a non-finite float is stored as unstorable.
- Review: `CAP-DOCS-document-model` names the path and states that deleting it is safe.
