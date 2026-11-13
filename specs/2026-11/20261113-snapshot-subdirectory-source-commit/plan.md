---
id: PLAN-snapshot-subdirectory-source-commit
spec: SPEC-snapshot-subdirectory-source-commit
---

# Fix plan

## 1. Constitution & Invariant Review

None. The fix restores `CAP-DIST-in-repo-bundles` verified identity and keeps `ARCH-05-2-components` ownership.
No package, feature edge, layer or test tier is added. No new ADR or Living Spec wording is required.

## 2. Architecture Overview & Impact

`source_commit()` remains a distribution repository helper. Add `--full-tree` only to its `ls-tree` call so
repository-relative input paths are interpreted from the repository root. Keep its working directory, captured
HEAD, 10-second timeout, byte/mode verification and failure-to-null behavior.

The existing snapshot integration module owns real Git fixtures. A subdirectory fixture can initialize Git at the
parent of its provider without moving production code or introducing a shared helper.

## 6. Verification & Test Plan

- AC-01: a retained real-Git subdirectory identity/path-equivalence test first fails, then passes.
- AC-02: parameterized dirty-byte/mode cases plus existing root-provider and captured-HEAD tests pass.
- AC-03: build a valid old null-identity snapshot with an in-test repository substitution, then verify metadata-only
  preview, digest-reviewed apply and unchanged file timestamps using the actual fixed implementation.
- Run the complete snapshot integration module, `just test-dist`, `just lint-check`, `just check`,
  `just test-affected --base 4131e8950bec81152a9d4eb62a200ef64d4995fa --tier all` with full fallback,
  and cumulative rules. No viewer frontend path is changed.
- Reconcile against the actual diff with a low-effort self-review and self-checked reconcile envelope.
