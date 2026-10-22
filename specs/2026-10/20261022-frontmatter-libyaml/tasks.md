---
id: TASKS-frontmatter-libyaml
spec: SPEC-frontmatter-libyaml
plan: PLAN-frontmatter-libyaml
---

# Task Breakdown: `SPEC-frontmatter-libyaml`

- [x] **Task 1**: Add guarded strict C parsing with exact Python fallback diagnostics and regression tests.
  - **_Boundary**: `packages/devkit-core/src/devkit_core/core/frontmatter.py`, `packages/devkit-core/tests/unit/core/test_frontmatter.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: Frontmatter tests, lint and type checks, then `just test-affected`.
- [x] **Task 2**: Measure equivalent repository header parsing and record the guarded parser performance.
  - **_Boundary**: `specs/2026-10/20261022-frontmatter-libyaml/evidence.md`
  - _Requirements: AC-05_
  - **Verification**: Nine alternating preloaded-header runs with equal results and at least 2x faster median.
