---
id: TASKS-milestone-archive
spec: SPEC-milestone-archive
plan: PLAN-milestone-archive
---

# Task Breakdown: `SPEC-milestone-archive`

- [ ] **Task 1**: Support canonical archive placement and proposal membership, with document identity/history regressions.
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/documents/`, `packages/devkit-docs/src/devkit_docs/features/governance/`, `packages/devkit-docs/tests/`, `packages/devkit-docs/src/devkit_docs/bundles/`, `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/roadmap.py`, `packages/devkit-spec/tests/integration/features/proposals/test_roadmap.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: focused document and proposal tests, then affected tests.
- [ ] **Task 2**: Include archived milestone headers, loader paths, counts, readiness and detail links in the viewer.
  - **_Boundary**: `packages/devkit-viewer/src/`, `packages/devkit-viewer/tests/`, `packages/devkit-viewer/frontend/`
  - _Requirements: AC-04, AC-05_
  - **Verification**: backend archive fixtures and frontend loader/extraction/roadmap/detail tests; viewer lint/check/test/build.
- [ ] **Task 3**: Reflect lifecycle movement in installed guidance and contracts, with semantic transition fixtures.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/backlog.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/milestone-completion.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/roadmap-catalog.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/next-work.md`, `packages/devkit-spec/tests/integration/bundles/spec/`, `packages/devkit-docs/src/devkit_docs/bundles/`, `packages/devkit-docs/README.md`, `packages/devkit-spec/README.md`, `packages/devkit-viewer/README.md`, `docs/capabilities/documents/`, `docs/capabilities/governance/CAP-GOV-spec-rules.md`, `docs/capabilities/delivery/CAP-DLV-proposal-incubation.md`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/capabilities/viewer/`, `docs/usecases/documents/`, `docs/usecases/delivery/`, `docs/decisions/2026-10/20261028-archive-terminal-milestones-in-roadmap.md`
  - _Requirements: AC-06_
  - **Verification**: rendered guidance scenarios and real synthetic close/drop/reopen/merge file-state exercises.
- [ ] **Task 4**: Move the approved four-file batch only after reader verification and deliver complete checks.
  - **_Boundary**: `docs/roadmap/MS-backlog-subagent-roles.md`, `docs/roadmap/MS-idea-incubation.md`, `docs/roadmap/MS-maintenance-operations.md`, `docs/roadmap/MS-ux-documentation.md`, `docs/roadmap/_archive/MS-backlog-subagent-roles.md`, `docs/roadmap/_archive/MS-idea-incubation.md`, `docs/roadmap/_archive/MS-maintenance-operations.md`, `docs/roadmap/_archive/MS-ux-documentation.md`, `docs/materials/2026-10/20261028-milestone-archive/`, `specs/2026-10/20261028-milestone-archive/`
  - _Requirements: AC-07, AC-08_
  - **Verification**: exact byte comparison, affected tests, lint/types, consumer smoke, frontend and cumulative rules.
