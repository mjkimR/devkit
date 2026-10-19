---
id: TASKS-role-reasoning-effort-presets
spec: SPEC-role-reasoning-effort-presets
plan: PLAN-role-reasoning-effort-presets
---

# Task Breakdown: `SPEC-role-reasoning-effort-presets` Per-role reasoning effort presets

- [ ] **Task 1**: Preset the reasoning effort in the four reviewer and research contracts and replace the
  challenger's model comment
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundle/subagents/scout.md`,
    `packages/devkit-spec/src/devkit_spec/bundle/subagents/reconcile-reviewer.md`,
    `packages/devkit-spec/src/devkit_spec/bundle/subagents/code-reviewer.md`,
    `packages/devkit-spec/src/devkit_spec/bundle/subagents/challenger.md`
  - _Requirements: AC-01, AC-02, AC-03_
- [ ] **Task 2**: Drift test pinning role, profile and preset for every role contract
  - **_Boundary**: `packages/devkit-spec/tests/test_role_contracts.py`
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: `just test devkit-spec tests/test_role_contracts.py`
- [ ] **Task 3**: Project the presets and confirm the projected agent files
  - **_Boundary**: `.devkit/installation.json`
  - _Requirements: AC-05_
  - **Verification**: `devkit sync`, then `devkit sync --check`
- [ ] **Task 4**: Living Spec statement of the presets in `CAP-DLV-delivery-workflows`
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`
  - _Requirements: AC-06_
