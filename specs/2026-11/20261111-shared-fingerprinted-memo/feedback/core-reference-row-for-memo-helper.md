---
id: FB-core-reference-row-for-memo-helper
title: The core quick reference describes the devkit_core.core modules but the new memo module was outside the write scope
scope: repo
kind: friction
category: docs-mismatch
target: docs/development/reference/core.md
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-11-11
---

# [FB-core-reference-row-for-memo-helper] The core quick reference describes the devkit_core.core modules but the new memo module was outside the write scope

## 1. Friction / Question (friction, question)

- **Context**: `SPEC-shared-fingerprinted-memo` adds `devkit_core.core.memo` (`safe_memo_path`, `envelope_problem`,
  `PathRefusal`, `EnvelopeProblem`). The Development payload declared the core source, its tests, the two memo
  modules and the two capability directories, not `docs/development/reference/`.
- **Expectation**: the repository guide keeps quick references in step with `docs/` and the packages; the core
  quick reference describes the public `devkit_core.core` modules, one row each.
- **Actual**: the reference has no row for `devkit_core.core.memo`. The file is neither in the declared scope nor
  adjacent under the worker's Tier B rule (it is not under the module's ownership root and restates no capability
  contract ID), so the worker did not write it.
- **Workaround (or Interpretation Chosen)**: left unchanged; the Host decides whether to add the row with this Unit
  or later.
- **Suggestion**: add one row after `devkit_core.core.logs`: "`devkit_core.core.memo` | the safe memo path and
  envelope rules of the fingerprinted memos under `.devkit/transient/`: `safe_memo_path(root, parts, *, create)`
  returns the path or a `PathRefusal`, `envelope_problem(loaded, version, fingerprint)` returns `None` or an
  `EnvelopeProblem`; nothing logs". A payload that adds a `devkit_core.core` module could name the reference file.

## Diagnostic Details

- **Reproduction**: `rg -n "devkit_core.core.memo" docs/development/reference/core.md` finds nothing on the Unit
  head.
- **Expected / Actual**: a row for the new public module / none.
- **Versions**: Unit branch `dev-shared-fingerprinted-memo`.
- **Conditions**: Development worker with a declared write scope.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `SPEC-shared-fingerprinted-memo`, `docs/development/reference/core.md`,
  `packages/devkit-core/src/devkit_core/core/memo.py`.

## Evidence

```text
docs/development/reference/core.md "## Modules" table: rows for frontmatter, paths, files, git, deadline, locks,
plugins and logs (and others outside devkit_core.core); none for memo.
```
