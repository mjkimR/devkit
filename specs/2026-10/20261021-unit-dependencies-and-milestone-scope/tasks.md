---
id: TASKS-unit-dependencies-and-milestone-scope
spec: SPEC-unit-dependencies-and-milestone-scope
plan: PLAN-unit-dependencies-and-milestone-scope
---

# Task Breakdown: `SPEC-unit-dependencies-and-milestone-scope`

- [x] **Task 1**: Typed dependency parsing, reference validation and projected handoff, with regression tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/, packages/devkit-spec/tests/
  - _Requirements: AC-01, AC-02_
- [x] **Task 2**: Proposal-only milestone membership and removed spec creation inputs, with tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/, packages/devkit-spec/tests/
  - _Requirements: AC-04_
- [x] **Task 3**: Base recommendation, lifecycle repair and coarse milestone guidance, with contract fixtures
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/, packages/devkit-spec/tests/, docs/roadmap/README.md
  - _Requirements: AC-03, AC-05_

- [x] **Task 4**: Align the viewer membership consumer with direct PROP ownership, preserving proposal branch and milestone history behavior
  - **_Boundary**: packages/devkit-viewer/frontend/src/lib/roadmap.ts, packages/devkit-viewer/frontend/src/lib/roadmap.test.ts, packages/devkit-viewer/frontend/src/lib/RoadmapView.test.ts, packages/devkit-viewer/src/devkit_viewer/static/, docs/capabilities/viewer/CAP-VIEW-repository-viewer.md, docs/architecture/ARCH-01-introduction-and-goals.md, packages/devkit-spec/README.md
  - _Requirements: AC-04_
  - **Verification**: just viewer lint, just viewer check, just viewer test, just viewer build; Host generated-artifact check
