---
id: PLAN-viewer-working-tree
spec: SPEC-viewer-working-tree
---

# Technical Plan: `SPEC-viewer-working-tree` Show the working tree for the current branch

## 1. Constitution & Invariant Review

- `ADR-viewer` currently requires Git object reads, permits any local branch, and explicitly excludes uncommitted edits. The new contract supersedes that decision for ordinary repository reads; preserve the exact-generation proposal-review read path and loopback, Host, GET-only, no-CORS and no-write boundaries.
- `CAP-VIEW-repository-viewer` describes the current Git-ref contract and must be updated in place.
- The registered repository root remains the security boundary. Resolve requested paths and refuse any path whose resolved location is outside that root.

## 2. Architecture Overview & Impact

- `devkit-viewer` HTTP read use cases and browse repository implementation will read the current checkout with `pathlib`; Git is used only to identify the checked-out branch (`HEAD` when detached).
- The Svelte app will display repository and branch labels, remove branch selection and ignore a legacy hash `ref`. Existing `RepositoryDataSource` tree/blob method signatures remain usable; the local HTTP adapter will send current-tree requests without a ref.
- Dashboard, roadmap and document index will read one current working tree and will not enumerate activity branches.
- No runtime dependency is added. The special `/review/<repo>/<generation>` route is unchanged.

## 3. Component & Interface Design

- `GET /api/repos` remains `{"repos": [{"id", "default_branch"}]}`; `default_branch` reports the checked-out branch, or `HEAD` when detached.
- `GET /api/repos/<id>/info` remains `{"repo_id", "default_branch"}`.
- `GET /api/repos/<id>/tree?path=` retains `{"items": [{"name", "path", "type", "size"?}]}` and lists immediate filesystem entries, including untracked and saved modified files.
- `GET /api/repos/<id>/blob?path=` retains `{"path", "encoding": "base64", "content", "size}` and returns current file bytes. A legacy `ref` parameter is ignored; it never selects another branch.
- The optional `refs` client capability may remain for third-party data sources, but devkit's app and its roadmap/dashboard do not call it.
- Use existing `ReadError` payloads: invalid relative syntax is `400 VIEWER_PATH_INVALID`; missing files, directories, and paths resolving outside the root are `404 VIEWER_PATH_NOT_FOUND`.

```text
Svelte views -> RepositoryDataSource -> GET tree/blob -> working-tree reader
                                      -> GET info     -> checked-out branch name
```

## 4. Storage & State Management

The server keeps no document cache or persistent index. Each request reads the saved current filesystem state. This avoids stale content and makes uncommitted edits visible immediately after saving.

## 5. Error Handling & Edge Cases

- Preserve UTF-8/base64 payload compatibility, sorting with directories before files, and blob byte sizes.
- Exclude symlinks and `.git` directories from listings and refuse requested symlink or `.git` paths. This prevents traversal outside the registration root, symlink cycles, and serving Git metadata.
- Treat an unresolvable checked-out branch as `HEAD`, including detached checkouts.
- Preserve loopback binding, Host refusal, GET-only behavior and no-write guarantees.

## 6. Verification & Test Plan

- Add focused integration coverage for saved uncommitted changes, untracked files, directory listings, invalid paths and external symlinks, branch reporting and detached `HEAD`.
- Update frontend tests for a branch label without a branch selector, current-tree requests, and absence of other-branch roadmap/dashboard reads.
- Run `just test-affected`, `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build`, and `just lint-check viewer` as required by repository verification policy.
- The generated viewer build must be committed and pass `uv run devkit generated check viewer-assets`.
