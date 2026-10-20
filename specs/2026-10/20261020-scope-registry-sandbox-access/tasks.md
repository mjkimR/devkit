---
id: TASKS-scope-registry-sandbox-access
spec: SPEC-scope-registry-sandbox-access
plan: PLAN-scope-registry-sandbox-access
---

# Task Breakdown: `SPEC-scope-registry-sandbox-access`

- [ ] **Task 1**: Separate read-only namespace locking and query ownership lookup, with error, side-effect and concurrency tests.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/scope/, packages/devkit-spec/src/devkit_spec/cli/scope.py, packages/devkit-spec/tests/scope/
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: scope tests and lint/type checks; existing mutation regression tests.
- [ ] **Task 2**: Verify actual Linux/macOS compatibility and unelevated sandbox queries; record evidence.
  - **_Boundary**: packages/devkit-spec/tests/scope/, docs/materials/2026-10/20261020-scope-registry-sandbox-access/
  - _Requirements: AC-05_
  - **Verification**: platform compatibility smoke and ordinary, --spec, --history CLI smoke.
