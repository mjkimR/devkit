---
id: PLAN-gitignore-drift-detection
spec: SPEC-gitignore-drift-detection
---

# Technical Plan: SPEC-gitignore-drift-detection

## 1. Constitution & Invariant Review

No conflict: CAP-DIST-workspace-ownership keeps ignore/index mutation out of sync. No new feature dependency,
package dependency or ADR is needed. Native paths come from inventory/receipt files outside `.devkit/`.

## 2. Architecture Overview & Impact

Add a distribution repository helper for read-only Git queries and notice construction. Call it from the sync
planner after ownership conflicts are checked, before applying changes. Use existing SyncNotice subclasses
with warning levels and stable codes. No schema change.

## 3. Component & Interface Design

`projection_git_notices(root, desired, previous)` returns advisory objects. Read tracked paths once with
`git ls-files -z`, intersect with known projection paths, and query effective ignores in one NUL-delimited
`git check-ignore --no-index --stdin -z` call. Use exact literal pathspecs and shell quoting in untracking advice.
Keep warnings bounded to ten targets each and include the full category count. Removed untracked files need
no ignore advice. Query errors become a warning; non-repositories return no findings.

## 6. Verification & Test Plan

Real temporary Git repositories cover AC-01 through AC-04, including nested ignore negation, tracked ignored
files, previous ownership, shell-special names, dry-run, strict JSON and locked mode. Check byte-identical index
and ignore files. Run `just test-affected`, `just lint-check dist`, `just check dist`, `just test-dist`, and
`uv run devkit rules check`. Reconcile the two existing distribution capabilities.
