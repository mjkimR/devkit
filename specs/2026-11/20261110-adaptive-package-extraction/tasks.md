---
id: TASKS-adaptive-package-extraction
spec: SPEC-adaptive-package-extraction
plan: PLAN-adaptive-package-extraction
---

# Task Breakdown: `SPEC-adaptive-package-extraction`

- [ ] **Task 1**: Extract the bundle, tests and repository wiring
  - **_Boundary**: `packages/devkit-adaptive/`, `packages/devkit-catalog/`, `tools/devkit-dev/tests/integration/test_bundle_citations.py`, `tests/e2e/smoke.sh`, `scripts/_lib.sh`, `pyproject.toml`, `uv.lock`, `.devkit/architecture.toml`, `.github/workflows/ci.yml`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-06_
  - **Verification**: package tests, smoke, affected tests, lint, types, rules, bundle tree identity.
- [ ] **Task 2**: Preserve moved bundle release versions with regression coverage
  - **_Boundary**: `scripts/releases/prepare.py`, `packages/devkit/tests/integration/package/test_selective_releases.py`
  - _Requirements: AC-08_
  - **Verification**: selective-release integration tests.
- [ ] **Task 3**: Update ownership documentation and fresh-install guides
  - **_Boundary**: `AGENTS.md`, `README.md`, `guides/INSTALL_GUIDE.md`, `guides/install/new-repository.md`, `guides/install/existing-repository.md`, `guides/install/adaptive-dev-sdd-adoption.md`, `guides/install/bundle-recommendations.md`, `docs/capabilities/delivery/CAP-DLV-adaptive-development.md`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/usecases/delivery/UC-advance-an-idea.md`, `docs/usecases/delivery/UC-import-third-party-agent-assets.md`, `docs/architecture/ARCH-05-1-containers.md`, `docs/architecture/ARCH-05-2-components.md`, `docs/architecture/ARCH-07-deployment.md`, `docs/decisions/2026-11/20261102-adaptive-development-and-research.md`, `docs/decisions/2026-11/20261106-skill-local-swarm-roles.md`, `docs/decisions/2026-11/20261110-adaptive-dev-distribution.md`
  - _Requirements: AC-07_
  - **Verification**: rules, stale-path search and comparison with target-docs.
