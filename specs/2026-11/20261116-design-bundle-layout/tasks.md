---
id: TASKS-design-bundle-layout
spec: SPEC-design-bundle-layout
plan: PLAN-design-bundle-layout
---

# Task Breakdown: `SPEC-design-bundle-layout` Area-scoped directory bundles for formal design documents

- [ ] **Task 1**: Kind layout fact, layout-aware governance, search pin, docs bundle assets and their tests
  - **_Boundary**: `packages/devkit-docs/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-06_
  - **Verification**: devkit-docs unit, rule and integration tests; `just test-affected`; lint and type checks.

- [ ] **Task 2**: Living Spec contracts, ADR, document migration and viewer follow-up
  - **_Boundary**: `docs/capabilities/documents/`, `docs/capabilities/traceability/`, `docs/capabilities/governance/CAP-GOV-spec-rules.md`, `docs/designs/`, `docs/domain/`, `docs/decisions/`, `docs/README.md`, `specs/2026-11/20261116-design-bundle-layout/`
  - _Requirements: AC-05, AC-06, AC-07_
  - **Verification**: `uv run devkit rules check`; `devkit docs resolve` and `refs` for the four moved IDs; the AC-06 search.

- [ ] **Task 3**: Landed lifecycle consumers in the spec and adaptive bundles and their tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/SKILL.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/brownfield-adoption/references/migration.md`, `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`, `packages/devkit-spec/tests/`, `packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/references/documents.md`, `packages/devkit-adaptive/tests/`, `.devkit/installation.json`
  - _Requirements: AC-04, AC-06_
  - **Verification**: devkit-spec entrypoint integration test, spec and adaptive lifecycle end-to-end scenarios, `just test-affected`.
