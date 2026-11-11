---
id: ADR-literal-read-test-selection
title: Select tests by their literal repository-path reads
summary: For affected-test selection, we add the repository paths that test modules, conftests and local helpers read through root-anchored literal path expressions as dependencies, keeping the data table for other readers, to select new readers without new rows, accepting slower document-only selection.
proposal: SPEC-select-tests-by-read-document-paths
status: accepted
created_at: 2026-11-11
---

# [ADR-literal-read-test-selection] Select tests by their literal repository-path reads

- **Status**: Accepted
- **Date**: 2026-11-11

---

## 1. Context & Problem Statement

`scripts/affected_tests.py` maps a changed non-source file to its readers only through the hand-kept `DATA` table
and maps a package source file only through static imports. A test that reads a file its imports do not reach is
skipped when only that file changes. At this head 37 reader pairs are missed: helper reads of
`.devkit/architecture.toml`, bundle assets of another package, recipe scripts, `guides/`, `.devkit/config.toml`,
package-root Markdown and the frontend script `scripts/viewer.sh` (which select nothing) and test data beside its
reader. Every repository document read by literal path is already
listed, so each new reader depends on someone adding a row. A missed reader lets a
failing test reach `main` until the next complete CI (`ADR-test-selection-and-ci`).

## 2. Decision Drivers

- Select a test whose read of a changed file is visible in its source, without a hand-kept row.
- Never reduce today's selection: explicit data checks, full triggers and the full fallback stay.
- Keep the selector static and stateless; it never imports or runs inspected code.
- Keep the added cost small next to a pytest run.

## 3. Considered Options

- **Add `DATA` rows for the measured misses** (rejected): cheapest now, but the class stays open and the next new
  reader is missed again.
- **A meta-test that fails when a literal read has no covering row** (rejected): runs only when the selector or that
  test is selected, so a new reader added elsewhere still passes, and every finding still needs a row.
- **Collect root-anchored literal reads as dependencies** (selected): closes the class for literal reads at the cost of
  parsing every test-tree file for each selection.
- **Record runtime file access** (rejected): needs executed tests and stored coverage, which
  `ADR-test-selection-and-ci` excludes.

## 4. Decision Outcome

Chosen: collect root-anchored literal reads as dependencies, because it removes the hand-kept step for every reader
visible in source while keeping all existing checks.

- A path expression is a read when it evaluates statically from `Path(__file__)` through `resolve`, `parent`,
  `parents[N]`, `/` with string literals, `joinpath` and names bound once to such an expression. It counts wherever
  it occurs, including as a call argument or a method receiver (`(ROOT / "x").read_text()`). A loop variable over a
  literal tuple or list expands into one read per element. → `ARCH-07-deployment` §1.3 (MUST)
- Every test-tree file is scanned once. A read in a test module belongs to it; a read in a conftest belongs to the
  test modules under its directory; a read in a local helper belongs to the test modules whose import discovery
  reaches that helper. → `ARCH-07-deployment` §1.3 (MUST)
- A changed path selects a reader when it equals an exact read or lies under a directory read. `iterdir`, a join with
  a runtime segment and a non-literal glob pattern read their base directory. A literal `glob` or `rglob` pattern
  selects when the changed path or one of its ancestors below the base matches it, so a new or deleted subdirectory
  counts. → `ARCH-07-deployment` §1.3 (MUST)
- A read that resolves to the repository root itself, or that the scan cannot resolve, adds nothing; it is not an
  import uncertainty and widens nothing. → `ARCH-07-deployment` §1.3 (MUST)
- Reads only add tests: a path that selects the full suite still does, and a path that selects nothing today,
  `.devkit/` and frontend paths included, selects its literal readers; a path no test reads still selects nothing.
  → `ARCH-07-deployment` §1.3 (MUST)
- A frontend change keeps `reason=frontend` and the `[FRONTEND_CHECK: ...]` line whether or not literal readers add
  pytest tests. → `ARCH-07-deployment` §1.3 (MUST)
- The `DATA` table keeps every row, and readers by document ID, by subprocess in the repository root or through an
  unresolved base keep or gain explicit rows. Removing a row the scan now covers is a later, measured reduction.
  → `ARCH-07-deployment` §1.3 (MUST)
- The scan reuses the selector's in-process parsed trees and stores nothing between runs.

## 5. Consequences

- **Positive**:
  - A new test that reads a repository file by literal path is selected for that file's changes with no table edit.
  - The measured misses in `docs/materials/2026-11/20261111-select-tests-by-read-document-paths/read-path-survey.md` are selected.
- **Negative / Risks**:
  - A document-only selection now parses and scans every test-tree file: about 0.01 s becomes about 2 to 3 s on the
    measured machine.
  - A join with a runtime segment widens to its base directory, so a few tests read whole bundle or package
    directories.
  - Reads through unresolved bases stay invisible; complete nightly and release CI remains the backstop.
- **Follow-ups**:
  - When a `DATA` row is fully covered by scanned reads, a later change may remove it with the before/after
    collection matrices `ARCH-07-deployment` §1.3 asks for.

## 6. Confirmation

- `packages/devkit/tests/e2e/package/test_affected_tests.py`: positive fixtures for each read form and each measured
  miss group, and negative fixtures for `tmp_path` literals, unanchored strings and a path no test reads; a frontend
  path with a literal reader (`scripts/viewer.sh`) and one without keep `reason=frontend` and the frontend check.
- `ARCH-07-deployment` §1.3 restates the traced clauses after Development.
