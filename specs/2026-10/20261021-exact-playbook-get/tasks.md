---
id: TASKS-exact-playbook-get
spec: SPEC-exact-playbook-get
plan: PLAN-exact-playbook-get
---

# Task Breakdown: `SPEC-exact-playbook-get`

- [x] **Task 1**: Exact receipt-backed retrieval, result model and CLI with integrity and output tests
  - **_Boundary**: packages/devkit-dist/src/devkit/distribution/, packages/devkit-dist/tests/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: just lint-check dist; just check dist; just test-affected; just test-dist
- [x] **Task 2**: Align consumption guidance and generated playbook skill with exact invocation and external execution
  - **_Boundary**: packages/devkit-dist/src/devkit/distribution/, packages/devkit-dist/tests/, docs/capabilities/distribution/, docs/architecture/, docs/decisions/, docs/development/reference/, guides/
  - _Requirements: AC-06_
  - **Verification**: focused generated-skill tests and governance checks
