---
id: TASKS-derived-reference-scope-extension
spec: SPEC-derived-reference-scope-extension
plan: PLAN-derived-reference-scope-extension
---

# Task Breakdown: `SPEC-derived-reference-scope-extension` Derived reference documents as recorded worker scope extensions

## Phase 1: Implementation

- [x] **Task 1.1**: Record the decision and restate the derived reference class in the delivery roles capability
  - **_Boundary**: `docs/decisions/2026-11/20261111-derived-reference-documents-as-worker-scope-extensions.md`, `docs/decisions/2026-11/20261104-recorded-adjacent-path-extensions-for-development-workers.md`, `docs/capabilities/delivery/CAP-DLV-delivery-roles.md`
  - _Requirements: AC-01_
  - **Verification**: `uv run devkit rules check`

- [x] **Task 1.2**: Ship the class in worker, review and Host guidance and cover inspection with regression tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/references/scope-extension.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/worker.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_scope_extension_guidance.py`, `packages/devkit-spec/tests/integration/features/worker/test_scope_extensions.py`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-02, AC-03_
  - **Verification**: the two pytest files and `uv run devkit sync --check`
