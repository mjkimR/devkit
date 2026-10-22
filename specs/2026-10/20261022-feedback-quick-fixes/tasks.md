---
id: TASKS-feedback-quick-fixes
spec: SPEC-feedback-quick-fixes
plan: PLAN-feedback-quick-fixes
---

# Task Breakdown: `SPEC-feedback-quick-fixes` Feedback Quick Fixes

## Phase 1: Implementation

- [x] **Task 1.1**: Refuse unsupported presentation languages
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/project/`, `packages/devkit-dist/tests/integration/features/project/test_presentation.py`, `packages/devkit-dist/tests/integration/features/distribution/test_local_config.py`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test devkit-dist packages/devkit-dist/tests/integration/features/project/test_presentation.py packages/devkit-dist/tests/integration/features/distribution/test_local_config.py`
- [x] **Task 1.2**: Accept and list module short names
  - **_Boundary**: `scripts/_lib.sh`, `README.md`
  - _Requirements: AC-03_
  - **Verification**: `just lint-check agt`; `bash scripts/module.sh lint-check nope` prints `Module short names:` and exits 1
- [x] **Task 1.3**: Name worktree skill and instruction paths in nested-role payloads
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/`, `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`
  - _Requirements: AC-04_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`
- [x] **Task 1.4**: Clarify that a condition-free spike completion is not Planning evidence
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/workflow-signals.md.jinja`, `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`
  - _Requirements: AC-05_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`

## Phase 2: Projection and Living Spec

- [x] **Task 2.1**: Re-project bundle assets and reconcile capabilities and source feedback
  - **_Boundary**: `.claude/`, `.agents/`, `.codex/`, `.devkit/managed/`, `.devkit/installation.json` (through `uv run devkit sync` only), `docs/capabilities/distribution/`, `docs/capabilities/integration/CAP-INT-mcp-services.md`, `docs/capabilities/delivery/`, the four source feedback files
  - _Requirements: AC-01, AC-03, AC-04, AC-05_
  - **Verification**: `uv run devkit status`; `uv run devkit rules check specs/2026-10/20261022-feedback-quick-fixes`
