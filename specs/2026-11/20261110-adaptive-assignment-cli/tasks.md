---
id: TASKS-adaptive-assignment-cli
spec: SPEC-adaptive-assignment-cli
plan: PLAN-adaptive-assignment-cli
---

# Task Breakdown

- [ ] **Task 1**: Implement assignment models, ledger/Git/governing repositories, six use cases and CLI with unit/integration tests
  - **_Boundary**: `packages/devkit-adaptive/src/devkit_adaptive/`, `packages/devkit-adaptive/tests/unit/`, `packages/devkit-adaptive/tests/integration/features/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-20, AC-21_
  - **Verification**: `just test adaptive integration/features unit`
- [ ] **Task 2**: Wire package dependencies, entry points, architecture, installed consumer, import isolation, documented codes and smoke
  - **_Boundary**: `packages/devkit-adaptive/pyproject.toml`, `packages/devkit-adaptive/tests/integration/package/`, `packages/devkit-adaptive/tests/e2e/`, `.devkit/architecture.toml`, `uv.lock`, `pyproject.toml`, `scripts/affected_tests.py`, `packages/devkit/tests/e2e/package/test_affected_tests.py`, `tests/e2e/smoke.sh`
  - _Requirements: AC-16, AC-18, AC-19, AC-22_
  - **Verification**: `just smoke`, `just test-affected`
- [ ] **Task 3**: Align bundle guidance and content tests, installation guides, package references and Living Spec
  - **_Boundary**: `packages/devkit-adaptive/tests/integration/bundles/`, `packages/devkit-adaptive/README.md`, `AGENTS.md`, `README.md`, `guides/INSTALL_GUIDE.md`, `guides/install/existing-repository.md`, `guides/install/new-repository.md`, `guides/install/bundle-recommendations.md`, `guides/install/adaptive-dev-sdd-adoption.md`, `docs/capabilities/delivery/CAP-DLV-adaptive-development.md`, `docs/capabilities/delivery/CAP-DLV-adaptive-assignments.md`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/usecases/delivery/UC-advance-an-idea.md`, `docs/architecture/ARCH-05-1-containers.md`, `docs/architecture/ARCH-05-2-components.md`, `docs/architecture/ARCH-07-deployment.md`, `docs/development/reference/adaptive.md`, `docs/development/reference/README.md`, `docs/decisions/2026-11/20261110-adaptive-assignment-commands.md`, `docs/decisions/2026-11/20261110-adaptive-assignment-ledger-storage.md`, `docs/decisions/2026-11/20261110-adaptive-requires-document-system.md`, `docs/decisions/2026-11/20261102-adaptive-development-and-research.md`, `docs/decisions/2026-11/20261110-adaptive-dev-distribution.md`
  - _Requirements: AC-17, AC-23_
  - **Verification**: bundle content tests, `just rules-check`, independent reconcile review
