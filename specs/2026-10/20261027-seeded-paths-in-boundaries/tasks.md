---
id: TASKS-seeded-paths-in-boundaries
spec: SPEC-seeded-paths-in-boundaries
plan: PLAN-seeded-paths-in-boundaries
---

# Task Breakdown: `SPEC-seeded-paths-in-boundaries` Seeded and synced paths in proposal boundaries

## Phase 1: Implementation
- [ ] **Task 1.1**: Rewrite the delegation wording for change sync outputs and pin it in the guidance test
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/worker.md, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja, packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py, .devkit/installation.json
  - _Requirements: AC-01, AC-02, AC-03, AC-05_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`; `uv run devkit sync --check`
- [ ] **Task 1.2**: State the rule in the delivery capability
  - **_Boundary**: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  - _Requirements: AC-04_
  - **Verification**: `just rules-check`
