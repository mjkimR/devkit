---
id: TASKS-link-prefixes-and-milestone-remediation
spec: SPEC-link-prefixes-and-milestone-remediation
plan: PLAN-link-prefixes-and-milestone-remediation
---

# [TASKS-link-prefixes-and-milestone-remediation] Viewer ID link prefixes and milestone path remediation

- [x] **Task 1**: Viewer prose reference prefixes match `PREFIXES`, with a regression test and the rebuilt page
  - **_Boundary**: `packages/devkit-viewer/frontend/src/lib/api/documents.ts`, `packages/devkit-viewer/frontend/src/lib/documents.test.ts`, `packages/devkit-viewer/src/devkit_viewer/static/`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just viewer test`, `just viewer build`
- [x] **Task 2**: Misplaced milestone remediation names `docs/roadmap/MS-{slug}.md`, with a regression test
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/governance/usecases/id_convention.py`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/id_convention/tests/test_rule.py`
  - _Requirements: AC-03, AC-04_
  - **Verification**: `just test devkit-spec`
