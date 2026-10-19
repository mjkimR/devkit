---
id: TASKS-summary-length-guard
spec: SPEC-summary-length-guard
plan: PLAN-summary-length-guard
---

# Tasks: Summary length guard

- [ ] T1: Reproduce and fix the shared summary length boundary across library and CLI creation paths.
  - _Boundary: packages/devkit-spec/src/devkit_spec/proposals/scaffold.py, packages/devkit-spec/tests/proposals/test_proposal_summary.py_
  - _Requirements: AC-01, AC-02, AC-03_
- [ ] T2: Reconcile the creation option and error contracts with the enforced summary limit.
  - _Boundary: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md, docs/capabilities/delivery/CAP-DLV-spec-bundles.md_
  - _Requirements: AC-01, AC-02, AC-03_
