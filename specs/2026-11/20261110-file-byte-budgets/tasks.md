---
id: TASKS-file-byte-budgets
spec: SPEC-file-byte-budgets
plan: PLAN-file-byte-budgets
---

# Task Breakdown: `SPEC-file-byte-budgets`

- [x] **Task 1**: Replace builtin line counting with snapshot-aware byte budgets and meaningful boundary tests.
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/services/builtins/file_length/`, `packages/devkit/tests/integration/features/rules/workspace/test_snapshot.py`
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: builtin boundary/selection tests and staged-versus-live snapshot regression.
- [x] **Task 2**: Migrate typed-setting examples and rules engine/CLI expectations to bytes.
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/models/settings.py`, `packages/devkit/src/devkit_agt/features/rules/services/testing.py`, `packages/devkit/tests/unit/features/rules/`, `packages/devkit/tests/integration/features/rules/`, `packages/devkit/tests/e2e/features/rules/`
  - _Requirements: AC-03, AC-05_
  - **Verification**: settings errors, check/explain output and unchanged hygiene phase tests.
- [x] **Task 3**: Align repository limits, current documents and shipped consolidation guidance with the decision.
  - **_Boundary**: `.devkit/config.toml`, `docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md`, `docs/capabilities/governance/CAP-GOV-rule-authoring.md`, `docs/development/reference/rules.md`, `docs/decisions/2026-11/20261104-consolidated-record-budgets.md`, `docs/decisions/2026-11/20261110-byte-based-file-budgets.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/adr-consolidation/SKILL.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-consolidation/SKILL.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_consolidated_budget_guidance.py`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-06_
  - **Verification**: source playbook tests, hygiene comparison, document rules and required lint/types/affected checks.
