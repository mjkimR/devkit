---
id: TASKS-retire-legacy-integration-provider-key
spec: SPEC-retire-legacy-integration-provider-key
plan: PLAN-retire-legacy-integration-provider-key
---

# Task Breakdown: `SPEC-retire-legacy-integration-provider-key` Reject the legacy [integration] provider key

## Phase 1: Implementation

- [x] **Task 1.1**: Refuse every `[integration]` key, the retired `provider` with its deletion fix, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/integration/services/providers.py`, `packages/devkit/tests/integration/features/integration/`, `packages/devkit/tests/e2e/features/integration/`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test devkit tests/integration/features/integration tests/e2e/features/integration`
- [x] **Task 1.2**: Living Spec and quick references state that `[integration]` accepts no keys
  - **_Boundary**: `docs/capabilities/integration/CAP-INT-mcp-services.md`, `docs/capabilities/delivery/CAP-DLV-project-policy.md`, `docs/capabilities/delivery/CAP-DLV-sdd-baseline-adoption.md`, `docs/usecases/delivery/UC-adopt-sdd-from-adaptive-development.md`, `docs/development/reference/integration.md`, `packages/devkit/README.md`
  - _Requirements: AC-04_
  - **Verification**: the AC-04 `rg` prints nothing and `uv run devkit rules check --ci --base main` passes
