---
id: TASKS-backlog-roadmap-and-issues
spec: SPEC-backlog-roadmap-and-issues
plan: PLAN-backlog-roadmap-and-issues
---

# Task Breakdown: Repository roadmap and Backlog

- [x] **Task 1**: Milestone document model, history and rule validation with regression tests.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/documents/, packages/devkit-spec/src/devkit_spec/rules/, packages/devkit-spec/src/devkit_spec/bundle/rules/, packages/devkit-spec/tests/documents/, packages/devkit-spec/tests/test_cli_documents.py
  - _Requirements: AC-01, AC-02, AC-03_
- [x] **Task 2**: Milestone/decomposition CLI authoring and handoff provenance with tests.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/proposals/, packages/devkit-spec/src/devkit_spec/cli/, packages/devkit-spec/tests/proposals/
  - _Requirements: AC-04_
- [x] **Task 3**: Milestone member hygiene advisories with settled-member tests.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/hygiene.py, packages/devkit-spec/src/devkit_spec/errors.py, packages/devkit-spec/tests/test_hygiene.py
  - _Requirements: AC-05_
- [x] **Task 4**: Backlog and next-work guidance, milestone template and seed documents, with bundle contract verification.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/skills/, packages/devkit-spec/src/devkit_spec/bundle/templates/, packages/devkit-spec/src/devkit_spec/bundle/seed/, packages/devkit-spec/src/devkit_spec/bundle/bundle.toml, packages/devkit-spec/tests/test_role_contracts.py, packages/devkit-spec/tests/test_package.py
  - _Requirements: AC-06, AC-07, AC-08_
