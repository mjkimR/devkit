---
id: FB-no-public-git-observation-helpers
title: No public helper lists worktrees or parses git status, so each package writes its own
scope: repo
kind: suggestion
category: missing-capability
target: packages/devkit-core/src/devkit_core/core/git.py
origin: agent
severity: workaround
recurring: false
status: promoted
created_at: 2026-11-10
---

# [FB-no-public-git-observation-helpers] No public helper lists worktrees or parses git status, so each package writes its own

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: A feature that needs the worktrees of a repository, the changed paths between two commits
  or the records of `git status --porcelain=v1 -z` writes its own parser. Planning of the assignment commands found
  no public function for any of the three and planned a sixth worktree-list parser and a third status parser inside
  the new feature. The existing ones are private functions, or live in a feature without a `public_modules` entry,
  or belong to `devkit_spec`, which the new package may not import.
- **Proposed Procedure**: Add to `devkit_core.core` (exported beside `run_git` and `is_ancestor`) one function that
  returns the worktree records (path, HEAD, branch, bare, prunable, locked), one that returns the status records
  with both names of a rename, and one that resolves a revision to a full commit ID; then move the existing callers
  to them in a refactor of its own.
- **Expected Benefit**: One tested reading of each Git output. The record order of a rename, the trailing slash of an
  untracked nested repository and the `prunable` record are easy to get wrong and are now decided separately in
  each copy.
- **Cost & Risk**: Six call sites change; two of them (`devkit_agt` worktree lifecycle, `devkit_spec` scope
  inventory) carry behavior their tests pin, so the move needs their suites.
- **Attempted**: Not attempted. The assignment commands' design writes its own parsers and names this follow-up.

## Diagnostic Details

- **Reproduction**: `rg -n '"worktree", "list"' packages/*/src` and `rg -n "porcelain" packages/*/src`.
- **Expected / Actual**: Expected a public function in `devkit_core.core` or a `public_modules` entry; found private
  functions only.
- **Versions**: Worktree at `fe1f1885`.
- **Conditions**: A new package that may import `devkit_core`, `devkit_dist`, `devkit_agt` and `devkit_docs` and not
  `devkit_spec`.
- **Workarounds Attempted**: The parser is written in the feature.
- **Related Assets**: `.devkit/architecture.toml` (`public_modules`), `RULE-architecture`.

## Evidence

```text
packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py:179  def _entries(base)        private
packages/devkit-dist/src/devkit_dist/features/shared/repositories/local.py:126  def _worktrees(...)   private
packages/devkit/src/devkit_agt/features/integration/usecases/service.py:362  inline worktree list -z
packages/devkit-dist/src/devkit_dist/features/host/usecases/registrations.py:289  inline worktree list -z
packages/devkit-spec/src/devkit_spec/features/scope/services/inventory.py:35-58  worktree list parser
packages/devkit/src/devkit_agt/features/compact/services/porcelain.py:8  status_records, feature without public module
packages/devkit-spec/src/devkit_spec/features/worker/usecases/inspect.py:125-142  status parser
packages/devkit-core/src/devkit_core/core/__init__.py exports run_git, run_git_text, is_ancestor only
```

- **Disposition**: PROP-core-git-observation-helpers: queued as a draft proposal that adds the public helpers and moves the existing parsers to them.
