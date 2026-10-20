---
id: TASKS-response-style-survey
spec: SPEC-response-style-survey
plan: PLAN-response-style-survey
---

# Task Breakdown: `SPEC-response-style-survey`

- [ ] **Task 1**: Apply the accepted skill and pointer with deployment and consumer smoke assertions.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/response_style/`, `packages/devkit-catalog/tests/test_bundles.py`, `scripts/smoke.sh`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test-affected`, `just smoke`, lint, types, example-based review and UTF-8 byte count.
