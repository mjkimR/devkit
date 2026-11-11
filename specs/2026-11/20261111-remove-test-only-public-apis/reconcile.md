---
reconcile_id: REC-remove-test-only-public-apis
status: resolved
targets:
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/capabilities/search/CAP-SRCH-document-search.md
    resolution: modified
  - file: docs/development/reference/worktree.md
    resolution: modified
  - file: docs/development/reference/search.md
    resolution: modified
  - file: docs/development/reference/core.md
    resolution: modified
---

# Reconcile: `SPEC-remove-test-only-public-apis`

- `CAP-WT-task-worktrees`: the methodology-layer cleanup names only the `devkit.post_finish` extension; finish step 2
  now describes the library's `before_step("worktree_remove", result)` callback (only when step 3 removes a worktree;
  the CLI passes none), and the post-finish paragraph names `before_step` as the library's callback.
- `CAP-SRCH-document-search`: the module layout lists `tokenize` and `Bm25` without `bm25_scores`.
- Worktree reference: the library example and the `WORKTREE_NOT_FOUND` row use `before_step`; the partial-result
  sentence names an advisory `before_step` raises once the merge is confirmed.
- Search reference: `SearchIndex.search` has no `limit` (callers truncate), the example drops `limit` and
  `SearchHit.to_dict`, and the primitives list drops `bm25_scores`.
- Core reference: `status_records(cwd, *pathspecs, untracked="all", optional_locks=False, deadline=None)` without
  `--no-renames` and `--ignore-submodules`.

No use case, architecture document or glossary term changes: the removed members were library parameters with no
production caller and no CLI or agent-facing behavior. No source feedback is carried. Entrypoints: no document gains
one: `devkit spec entrypoints derive` only cross-joined every task boundary with both capabilities, and each
capability was touched for wording, so every candidate is rejected.
