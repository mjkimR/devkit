---
id: TASKS-split-composed-proposal-accept
spec: SPEC-split-composed-proposal-accept
plan: PLAN-split-composed-proposal-accept
---

# Task Breakdown: `SPEC-split-composed-proposal-accept` Split composed Planning acceptance into its own subcommand

## Phase 1: Implementation

- [x] **Task 1.1**: `accept-plan` subcommand, `accept` without `--mode`/`--effort`, emitted commands, with tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/delivery/, packages/devkit-spec/src/devkit_spec/base/errors.py, packages/devkit-spec/tests/, docs/capabilities/delivery/, docs/capabilities/harness/CAP-HARN-command-mount.md, docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md, docs/development/reference/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/e2e/features/delivery packages/devkit-spec/tests/integration/features/delivery packages/devkit-spec/tests/integration/package`
- [x] **Task 1.2**: Spec bundle guidance names `accept-plan`, with the bundle test
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/, packages/devkit-spec/tests/integration/bundles/spec/, .devkit/installation.json (sync output), docs/capabilities/harness/CAP-HARN-agent-guidance.md (scope extension: restates the spec skills' commands, which now name the CAP-DLV-proposal-lifecycle accept-plan route)
  - _Requirements: AC-07_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/integration/bundles/spec` and `uv run devkit sync --check`
