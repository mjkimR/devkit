---
id: TASKS-lifecycle-feedback-fixes
spec: SPEC-lifecycle-feedback-fixes
plan: PLAN-lifecycle-feedback-fixes
---

# Task Breakdown: `SPEC-lifecycle-feedback-fixes` Fix four lifecycle feedback items

## Phase 1: Implementation

- [ ] **Task 1.1**: Concrete unsupported-anchor fix in envelope commit, with its test
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/workflow/services/envelope/commit.py`,
    `packages/devkit/tests/unit/features/workflow/test_envelope_commit_policy.py`
  - _Requirements: AC-01_
  - **Verification**: `just test devkit tests/integration/package/test_agent_output_contract.py tests/unit/features/workflow/test_envelope_commit_policy.py`
- [ ] **Task 1.2**: Locked restore first in the stale local render fix, with its test and documentation
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/local_render.py`,
    `packages/devkit-dist/tests/integration/features/distribution/test_local_config.py`,
    `docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md`, `docs/development/reference/distribution.md`
  - _Requirements: AC-02, AC-05_
  - **Verification**: `just test devkit-dist tests/integration/features/distribution/test_local_config.py`
- [ ] **Task 1.3**: Write-time stage check of `envelope worker`, with tests and the capability passage
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/workflow/usecases/envelopes.py`,
    `packages/devkit/tests/integration/features/workflow/`, `docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md`
  - _Requirements: AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit tests/integration/features/workflow`
- [ ] **Task 1.4**: Rename reference writes in the document model and the proposal template, synced
  - **_Boundary**: `docs/capabilities/documents/CAP-DOCS-document-model.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/templates/proposal.md`,
    `.devkit/installation.json`
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit sync --check` and `just rules-check`
