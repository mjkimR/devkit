---
id: TASKS-test-host-preflight
spec: SPEC-test-host-preflight
plan: PLAN-test-host-preflight
---

# Task Breakdown: `SPEC-test-host-preflight`

- [ ] **Task 1**: Add selected-path loopback preflight and advisory regressions.
  - **_Boundary**: `scripts/check_test_environment.py`, `packages/devkit/tests/integration/package/test_test_environment.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: Run preflight integration tests with injected denials and permitted local bind.
- [ ] **Task 2**: Forward recipe selections and prove affected full/partial routing remains intact.
  - **_Boundary**: `scripts/module.sh`, `packages/devkit/tests/integration/package/test_module_script.py`, `packages/devkit/tests/e2e/package/test_affected_tests.py`
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: Run module recipe and affected selector regressions.
- [ ] **Task 3**: Document conditional dependency network needs and resolve the verified source.
  - **_Boundary**: `docs/development/ci-cd.md`, `specs/2026-11/feedback/20261104-full-suite-host-capabilities.md`
  - _Requirements: AC-04_
  - **Verification**: Compare docs and source disposition with test evidence.
