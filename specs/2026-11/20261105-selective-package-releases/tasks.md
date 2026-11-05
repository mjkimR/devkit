---
id: TASKS-selective-package-releases
spec: SPEC-selective-package-releases
plan: PLAN-selective-package-releases
---

# Task Breakdown: `SPEC-selective-package-releases`

- [x] **Task 1**: Selective canonical identities, dependency closure, preparation and bootstrap with regression tests.
  - **_Boundary**: `scripts/version.py`, `scripts/releases/`, `packages/devkit/tests/integration/package/test_version_script.py`, `packages/devkit/tests/integration/package/test_lockstep.py`, `packages/devkit/tests/integration/package/test_selective_releases.py`, `justfile`, `uv.lock`, `packages/devkit-advisory/pyproject.toml`, `packages/devkit-catalog/pyproject.toml`, `packages/devkit-cli/pyproject.toml`, `packages/devkit-core/pyproject.toml`, `packages/devkit-dist/pyproject.toml`, `packages/devkit-docs/pyproject.toml`, `packages/devkit-mcp/pyproject.toml`, `packages/devkit-spec/pyproject.toml`, `packages/devkit-starter/pyproject.toml`, `packages/devkit-viewer/pyproject.toml`, `packages/devkit/pyproject.toml`, `tools/devkit-dev/pyproject.toml`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-06_
  - **Verification**: `uv run pytest packages/devkit/tests/integration/package/test_selective_releases.py packages/devkit/tests/integration/package/test_version_script.py packages/devkit/tests/integration/package/test_lockstep.py`

- [x] **Task 2**: Inventory-selected release builds, consumer commands and resumable immutable publication with consumer tests.
  - **_Boundary**: `scripts/release.sh`, `scripts/releases/`, `.github/workflows/release.yml`, `packages/devkit/tests/integration/package/test_selective_releases.py`, `tools/devkit-dev/tests/integration/test_handbook_script.py`
  - _Requirements: AC-02, AC-03, AC-05, AC-06_
  - **Verification**: `just test-affected --base 0e17cd72d96d5111e39731291241472d7cd3f87b`

- [x] **Task 3**: Align release/install contracts and quick references with actual package versions and complete inventories.
  - **_Boundary**: `docs/architecture/ARCH-07-deployment.md`, `docs/architecture/ARCH-01-introduction-and-goals.md`, `docs/architecture/ARCH-05-1-containers.md`, `docs/architecture/ARCH-05-3-command-plugins.md`, `docs/capabilities/cli/CAP-CLI-agent-cli-toolkit.md`, `docs/capabilities/distribution/CAP-DIST-content-packages.md`, `docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md`, `docs/decisions/2026-11/20261102-package-ownership-and-release-version.md`, `docs/decisions/2026-11/20261105-selective-package-versions.md`, `docs/development/reference/distribution.md`, `docs/development/reference/advisory.md`, `docs/steering/glossary.md`, `README.md`, `packages/devkit/README.md`, `packages/devkit-dist/README.md`, `packages/devkit-cli/README.md`, `packages/devkit-advisory/README.md`, `packages/devkit-starter/README.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `uv run devkit rules check`
