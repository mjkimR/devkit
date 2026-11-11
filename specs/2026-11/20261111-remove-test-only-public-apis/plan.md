---
id: PLAN-remove-test-only-public-apis
spec: SPEC-remove-test-only-public-apis
---

# Technical Plan: `SPEC-remove-test-only-public-apis` Remove test-only public APIs

## 1. Constitution & Invariant Review

None. `CAP-WT-task-worktrees` names `before_remove` only as an alternative to the `devkit.post_finish` extension;
the methodology-layer cleanup contract stays through the extension and `before_step`. No architecture `MUST` changes
and no feature edge is added.

## 2. Architecture Overview & Impact

- `packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py`: drop the `before_remove` keyword from
  `finish` and `discard` and its calls; docstrings and comments name `before_step` instead. The feature's
  `__init__.py` docstring drops the hook too. The change stays limited to these lines because concurrent work
  retires `finish --merge` in the same file.
- `packages/devkit-core/src/devkit_core/core/git.py`: `status_records(cwd, *pathspecs, untracked="all",
  optional_locks=False, deadline=None)`; `--no-renames` and `--ignore-submodules` are no longer built.
- `packages/devkit-dist/src/devkit_dist/features/search/`: remove `bm25_scores` (lexical service and package
  export), `limit` from `SearchIndex.search`, and `SearchHit.to_dict`.
- Living Spec: `CAP-WT-task-worktrees`, `CAP-SRCH-document-search`, `docs/development/reference/worktree.md`,
  `docs/development/reference/search.md`, `docs/development/reference/core.md`.

## 3. Component & Interface Design

```python
def finish(position, branch, *, merge=False, pull_request="auto", delete_branch=True, guard=None,
           network="allow", before_step=None, merge_method="no-ff") -> FinishResult: ...
def discard(position, branch) -> FinishResult: ...
def status_records(cwd, *pathspecs, untracked="all", optional_locks=False, deadline=None) -> list[StatusRecord]: ...
class SearchIndex:
    def search(self, query, *, mode=SearchMode.AUTO, min_score=0.0, min_similarity=0.0) -> list[SearchHit]: ...
```

Test migration: the finish tests that observed `before_remove` observe `before_step` calls (`worktree_remove` runs
at the same point; on a resumed finish whose worktree is already gone only `marker_clear` or `branch_delete` runs);
the caller-cleanup advisory test raises from `before_step("worktree_remove")`. The discard test drops the hook. The
core rename test keeps the rename record assertions without `--no-renames`; the options test drops
`ignore_submodules`. The lexical tests use `Bm25(documents).scores(query)`; the index test drops `limit` and
`to_dict`.

## 6. Verification & Test Plan

- `just lint` and `just check` for `devkit`, `devkit-core` and `devkit-dist`.
- `just test-affected --base main` (unit and integration) plus `just test-affected --base main --tier e2e` for the
  worktree lifecycle E2E tests; `just test-dist`.
- `uv run devkit rules check` and `uv run devkit workflow envelope check --unit <unit>`.
- `rg` over `packages tools scripts guides docs` for the removed names (excluding `docs/materials` and this unit).
