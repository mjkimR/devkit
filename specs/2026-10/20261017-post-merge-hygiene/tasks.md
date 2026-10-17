---
id: TASKS-post-merge-hygiene
spec: SPEC-post-merge-hygiene
plan: PLAN-post-merge-hygiene
---

# Task Breakdown: Post-integration hygiene

- [x] **Task 1**: Repair seed metadata and strengthen the existing package regression test.
  - _Boundary: packages/devkit-spec/src/devkit_spec/bundle/seed/docs/architecture/, packages/devkit-spec/tests/test_package.py_
  - _Requirements: AC-01, AC-05_
- [x] **Task 2**: Add SDD wheel consumer verification and release installation instructions.
  - _Boundary: scripts/smoke.sh, scripts/release.sh_
  - _Requirements: AC-02, AC-03, AC-05_
- [x] **Task 3**: Align package, CI and architecture documentation with current behavior.
  - _Boundary: packages/devkit-spec/README.md, README.md, AGENTS.md, docs/development/ci-cd.md, docs/architecture/ARCH-05-1-containers.md, docs/architecture/ARCH-07-deployment.md, docs/capabilities/harness/CAP-HARN-agent-guidance.md, docs/README.md, packages/devkit-spec/src/devkit_spec/bundle/rules/document_reference/guide.md_
  - _Requirements: AC-03, AC-04_
