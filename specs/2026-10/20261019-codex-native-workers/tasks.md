---
id: TASKS-codex-native-workers
spec: SPEC-codex-native-workers
plan: PLAN-codex-native-workers
---

# Task Breakdown: `SPEC-codex-native-workers`

- [ ] **Task 1**: Enable Codex worker projection and explicit operation/failure contracts with actual projection tests.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/subagents/planning-worker.md,
    packages/devkit-spec/src/devkit_spec/bundle/subagents/development-worker.md,
    packages/devkit-spec/tests/test_role_contracts.py
  - _Requirements: AC-01, AC-03, AC-04_
- [ ] **Task 2**: Align caller, orchestration and records with trust-aware invocation and truthful partial returns.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/SKILL.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/references/hosts.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/references/payload.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/references/worker.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec-orchestrate/SKILL.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/worker-records.md,
    packages/devkit-spec/tests/test_role_contracts.py
  - _Requirements: AC-02, AC-03, AC-04, AC-05_
- [ ] **Task 3**: Deploy the source contracts and verify packaging, projection budgets and governance.
  - **_Boundary**: .devkit/installation.json, docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: role/projection tests, bundle budgets, lint/types, rules, sync/status and consumer smoke.
