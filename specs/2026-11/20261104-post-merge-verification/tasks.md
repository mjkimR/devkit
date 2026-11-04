---
id: TASKS-post-merge-verification
spec: SPEC-post-merge-verification
plan: PLAN-post-merge-verification
---

# Task breakdown: post-merge verification

- [x] **Task 1**: Reduce generic integration to approved Git effects, preserve guards and add regression coverage.
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/integration/`, `packages/devkit/src/devkit_agt/features/worktree/`, `packages/devkit/pyproject.toml`, `packages/devkit/tests/integration/features/integration/`, `packages/devkit/tests/e2e/features/integration/`, `packages/devkit/tests/integration/features/worktree/`, `packages/devkit/tests/integration/package/test_config_tables.py`, `.devkit/config.toml`, `docs/architecture/ARCH-04-1-ecosystem-boundaries.md` (scope extension: Host-authorized alignment of CAP-INT-mcp-services ownership with removed readiness provider and retained acceptance cleanup), `docs/decisions/2026-11/20261102-adaptive-development-and-research.md` (scope extension: Host-authorized partial supersession of CAP-DLV-adaptive-development provider readiness and activation clauses), `docs/decisions/2026-11/20261104-post-merge-verification.md`, `docs/architecture/ARCH-04-2-delivery-policy.md` (scope extension: Host-authorized alignment of CAP-INT-mcp-services readiness ownership with final Host checks and retained Git policy), `packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py` (scope extension: Host-authorized migration of installed consumer fixture for the reduced integration CLI and verification state)
  - _Requirements: AC-01, AC-02, AC-05, AC-06, AC-07, AC-09_
  - **Verification**: Integration service, CLI and PR tests; lint and types.

- [x] **Task 2**: Preserve proposal eligibility and yield acceptance before fresh-process handoff, with tests.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/delivery/`, `packages/devkit-spec/src/devkit_spec/features/policy/`, `packages/devkit-spec/pyproject.toml`, `packages/devkit-spec/tests/integration/features/delivery/`, `packages/devkit-spec/tests/integration/features/proposals/`, `packages/devkit-spec/tests/integration/features/policy/`, `packages/devkit-spec/tests/e2e/features/delivery/`, `packages/devkit-spec/tests/e2e/package/test_package.py`, `packages/devkit-spec/tests/support/spec_support/delivery.py`, `packages/devkit-spec/tests/integration/package/test_help_and_notices.py`, `uv.lock`
  - _Requirements: AC-02, AC-06, AC-07, AC-09_
  - **Verification**: Proposal acceptance and composed output regressions; lint and types.

- [x] **Task 3**: Specify and verify the Host final-check sequence and consumer guidance.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/`, `packages/devkit-spec/tests/integration/bundles/spec/`, `docs/development/`, `AGENTS.md`, `guides/`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-03, AC-04, AC-06, AC-07, AC-08_
  - **Verification**: Guidance regressions, lifecycle walkthrough, sync and rules checks.
