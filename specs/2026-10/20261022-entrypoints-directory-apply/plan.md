---
id: PLAN-entrypoints-directory-apply
spec: SPEC-entrypoints-directory-apply
summary: Implementation plan for directory-level code entrypoint filtering and application in devkit-spec.
status: planned
created: 2026-10-22
---

# [PLAN-entrypoints-directory-apply] Implementation Plan

## 1. Constitution & Invariant Review

- `CAP-TRACE-code-entrypoints`: Declared entrypoints can be files or directories (represented with a trailing `/`).
- Invariant: A document never lists a directory and files inside it from one apply (`collapse` invariant).
- Invariant: CLI commands remain backwards compatible with existing `--code <file>` filters.

## 2. Architecture Overview & Impact

- **Impacted components**:
  - `devkit_spec.features.entrypoints.services.derive`: In `select` or a new directory-synthesis step, detect `--code` items ending with `/`. For each valid directory, synthesize a candidate pair `<dir>` for documents that have descendant candidate files under that directory, and fold those descendant candidate files into `<dir>`.
  - `devkit_spec.features.entrypoints.usecases.derive`: Validate that any `--code` ending in `/` resolves to an existing directory in `root`.
  - `devkit_spec.features.entrypoints.usecases.apply`: Existing `apply` already appends trailing `/` to directories (`(root / pair.code).is_dir()`) and `collapse` drops descendant additions.
  - Tests under `packages/devkit-spec/tests/` to verify AC-01 through AC-04.

## 3. Component & Interface Design

- In `devkit_spec.features.entrypoints.services.derive`:
  - When filtering with `codes`:
    - Separate directory selectors (ending in `/`) and prefix/file selectors.
    - If a directory selector `<dir>/` is present:
      - Ensure `<dir>` is verified as an existing directory in the repository.
      - For documents having candidates covered by `<dir>`, ensure a `Pair` with `code = normalize(<dir>)` exists.
      - Mark all candidates covered by `<dir>` with `folded_into = normalize(<dir>)`.
- CLI `--code` option help and error handling:
  - Non-existent directory ending with `/` fails with `EntrypointsPathError` ("directory does not exist").

## 4. Storage & State Management

- No new persistent state; modifies document frontmatter (`entrypoints`) on `--apply`.

## 5. Error Handling & Edge Cases

- Non-existent directory with trailing slash raises `EntrypointsPathError`.
- Document already declaring `<dir>/` has the pair marked as `State.DECLARED`.
- Multiple `--code` options combining directories and specific files outside those directories work cleanly.

## 6. Verification & Test Plan

- Unit tests in `packages/devkit-spec/tests/unit/features/entrypoints/` or integration tests in `packages/devkit-spec/tests/integration/features/entrypoints/test_apply.py` and `test_derive.py`.
- Run `just test-affected` and `just rules-check`.
