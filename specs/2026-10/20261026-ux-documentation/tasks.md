---
id: TASKS-ux-documentation
spec: SPEC-ux-documentation
plan: PLAN-ux-documentation
---

# Task Breakdown: `SPEC-ux-documentation` UX documents, authoring guidance and use-case-driven review

## Phase 1: Implementation

- [x] **Task 1.1**: The UX kind row and its `RULE-id-convention` grammar, with the kind, index, list and search tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/id_convention/, packages/devkit-spec/tests/
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test devkit-spec tests/unit/features/documents tests/integration/features/documents` and `uv run devkit rules test packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/id_convention`
- [x] **Task 1.2**: `RULE-ux-links` and `RULE-ux-coverage` with the shared UX model service, guides, manifest assets and rule tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/governance/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/ux_links/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/ux_coverage/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml, packages/devkit-spec/tests/
  - _Requirements: AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10_
  - **Verification**: `uv run devkit rules test packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/ux_links` and the same for `ux_coverage`
- [x] **Task 1.3**: Template, seed, `ux-writing` and `usecase-writing` guidance, with guidance tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/, packages/devkit-spec/tests/
  - _Requirements: AC-11, AC-12_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec`
- [x] **Task 1.4**: The `ux-reviewer` role, the `spec-ux-review` skill and the workflow guidance (specify, sync, effort, proposal acceptance, blueprint), with role-contract and guidance tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/, packages/devkit-spec/src/devkit_spec/features/proposals/, packages/devkit-spec/tests/, .devkit/installation.json, AGENTS.md
  - _Requirements: AC-13, AC-14_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec tests/integration/features/proposals` and `uv run devkit sync --check`
- [x] **Task 1.5**: Viewer UX book group and reference pattern, test and rebuilt static page
  - **_Boundary**: packages/devkit-viewer/frontend/src/lib/, packages/devkit-viewer/src/devkit_viewer/static/
  - _Requirements: AC-03_
  - **Verification**: `just viewer test`, `just viewer check`, `just viewer lint`, `just viewer build`
- [ ] **Task 1.6**: Living Spec capabilities and the glossary terms
  - **_Boundary**: docs/capabilities/documents/, docs/capabilities/governance/, docs/capabilities/delivery/, docs/capabilities/viewer/, docs/steering/glossary.md
  - _Requirements: AC-15_
  - **Verification**: `uv run devkit rules check` and `uv run devkit sync --check`
