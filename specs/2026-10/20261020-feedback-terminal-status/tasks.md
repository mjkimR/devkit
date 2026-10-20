---
id: TASKS-feedback-terminal-status
spec: SPEC-feedback-terminal-status
plan: PLAN-feedback-terminal-status
---

# Task Breakdown: `SPEC-feedback-terminal-status`

- [x] **Task 1**: Correct the lifecycle policy and its agent-facing instructions.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle, docs/decisions/2026-10/20261019-feedback-resolution-lifecycle.md, docs/decisions/2026-10/20261020-feedback-terminal-outcomes.md
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: independent semantic review and governance checks.
- [x] **Task 2**: Restrict implicit worker source scope to open feedback with regression coverage.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/worker/inputs.py, packages/devkit-spec/tests/test_worker_inspect.py
  - _Requirements: AC-03_
  - **Verification**: worker inspection regression tests, lint and type checks.
- [x] **Task 3**: Reconcile the four capability contracts and verify the accumulated change.
  - **_Boundary**: docs/glossary.md, docs/capabilities/documents/CAP-DOCS-document-model.md, docs/capabilities/harness/CAP-HARN-agent-guidance.md, docs/capabilities/delivery/CAP-DLV-delivery-workflows.md, docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: affected tests, cumulative rules, independent reconcile review.
