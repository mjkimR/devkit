---
id: ADR-viewer-working-tree
title: Read the checked-out repository working tree
summary: "For local repository browsing, we read saved files below the registered checkout and show its branch, to expose uncommitted work without branch switching, accepting that other branches and unsaved buffers are unavailable."
status: accepted
created_at: 2026-10-24
supersedes: ADR-viewer
---

# [ADR-viewer-working-tree] Read the checked-out repository working tree

- **Status**: Accepted; supersedes `ADR-viewer`
- **Date**: 2026-10-24
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `packages/devkit-viewer/`, `CAP-VIEW-repository-viewer`

---

## 1. Context & Problem Statement

The viewer reads committed Git objects and offers branch selection. A developer cannot inspect a saved edit until committing it. The intended use is to review the current checkout, with the current branch name as context.

The registered repository root remains the boundary for file reads. The local web server must continue to protect against path traversal and must not write to repositories. Proposal-review artifacts remain an exact-generation exception with their existing local adapter and expiry rules.

## 2. Decision Drivers

- Show saved uncommitted and untracked files.
- Keep every file read within the registered checkout.
- Remove ordinary Git object reads and other-branch enumeration.
- Preserve the loopback-only, GET-only, no-CORS, no-write server.
- Keep the Python and Svelte packaging and their runtime dependencies unchanged.

## 3. Considered Options

### Read saved working-tree files and show the checked-out branch (Selected)

- **Overview**: Resolve and read requested paths below each registered repository root. Query Git only for the branch label, returning `HEAD` for detached checkouts.
- **Pros**: Saved uncommitted and untracked files appear immediately; ordinary tree and blob reads no longer spawn Git processes; the interface identifies the checkout being read.
- **Cons**: Other branches and unsaved editor buffers are unavailable. Filesystem traversal needs explicit path and symlink checks.

### Continue reading Git objects at selected refs

- **Overview**: Keep the existing branch picker and read committed tree/blob objects with Git subprocesses.
- **Pros**: Reads any local branch without changing the checkout and confines content to Git objects.
- **Cons**: Hides saved uncommitted content, requires repeated Git calls and exposes branch switching that this viewer does not need.

## 4. Decision Outcome

We read tree and blob content directly from the registered current working directory and display the checked-out branch as a label. Ordinary content requests ignore any `ref` query parameter. Directory listings omit symlinks, and requests for symlinks fail as missing paths. A resolved path outside the registered root is never served. The UI and roadmap read only the current checkout.

The exact-generation proposal-review route remains unchanged. The server continues to bind to loopback, refuse foreign Host headers, answer GET only, and write nothing.

## 5. Consequences

- **Positive**: Saved modifications and untracked files are visible without a commit. Ordinary content reads no longer start Git processes. One repository view corresponds to one checked-out directory.
- **Negative / Risks**: Other local branches are not visible. Unsaved editor buffers are unavailable. Filesystem access can race with changes made while a response is being assembled.
- **Follow-ups**: Reconsider filesystem watchers only if users need automatic updates before navigating or reloading.

## 6. Confirmation

- Integration tests prove uncommitted and untracked files are visible and external symlinks are not served.
- Frontend tests prove the branch is a label, no selector is present, and views do not request other branches.
