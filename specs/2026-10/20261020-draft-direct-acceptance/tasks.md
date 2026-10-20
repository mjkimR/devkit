---
id: TASKS-draft-direct-acceptance
spec: SPEC-draft-direct-acceptance
plan: PLAN-draft-direct-acceptance
---

# Task Breakdown: `SPEC-draft-direct-acceptance` Direct acceptance of drafts that need no Planning

- [x] **Task 1**: The accept command: library, base-checkout check, codes and CLI, with tests.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/proposals/, packages/devkit-spec/src/devkit_spec/branches.py,
    packages/devkit-spec/src/devkit_spec/errors.py, packages/devkit-spec/src/devkit_spec/cli/proposals.py,
    packages/devkit-spec/tests/proposals/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: `just test devkit-spec tests/proposals/test_proposal_accept.py`
- [x] **Task 2**: The handoff guard, the carried note and the not-approved directive, with tests.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/proposals/handoff.py,
    packages/devkit-spec/src/devkit_spec/errors.py, packages/devkit-spec/tests/proposals/
  - _Requirements: AC-09, AC-10, AC-11_
- [ ] **Task 3**: Guidance, scaffold lifecycle line and seed README for the direct acceptance and the session
  reclassification, with a guidance test.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/, packages/devkit-spec/src/devkit_spec/proposals/scaffold.py,
    packages/devkit-spec/tests/
  - _Requirements: AC-12_
