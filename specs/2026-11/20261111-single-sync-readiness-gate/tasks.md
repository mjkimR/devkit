---
id: TASKS-single-sync-readiness-gate
spec: SPEC-single-sync-readiness-gate
plan: PLAN-single-sync-readiness-gate
---

# Task Breakdown: `SPEC-single-sync-readiness-gate` One readiness gate for a synchronized checkout

## Phase 1: Contract and reference

- [ ] **Task 1.1**: State the readiness gate in the capability and the reference
  - **_Boundary**: `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `docs/development/reference/distribution.md`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `rg -n "remains the check that says whether a sync is needed" docs/` finds nothing; `uv run devkit rules check docs/capabilities/distribution docs/development/reference/distribution.md`

## Phase 2: Completion criteria, guides and help

- [ ] **Task 2.1**: Completion criteria name the single gate
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/instructions/consumption.md`, `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/instructions/in-repo-bundle.md`, `packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/playbooks/agent-asset-conversion/references/project-bundle.md`, `docs/usecases/delivery/UC-import-third-party-agent-assets.md`
  - _Requirements: AC-03, AC-07_
  - **Verification**: `rg -n "devkit status.{0,60}exit" packages/*/src/*/bundles guides docs/usecases` finds nothing; `uv run devkit bundle validate` on both bundles exits `0`

- [ ] **Task 2.2**: Guides present status as diagnosis
  - **_Boundary**: `guides/INSTALL_GUIDE.md`, `guides/install/existing-repository.md`
  - _Requirements: AC-04_
  - **Verification**: read Step 5 and "Already installed" against `guides/install/mcp.md`; `git diff --check`

- [ ] **Task 2.3**: The status help names the gate, with a test
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/cli/selection.py`, `packages/devkit-dist/tests/integration/features/distribution/test_cli_contract.py`
  - _Requirements: AC-05, AC-06_
  - **Verification**: `uv run pytest packages/devkit-dist/tests/integration/features/distribution/test_cli_contract.py`; `just test-dist`; `just test-affected`
