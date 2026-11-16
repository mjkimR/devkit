---
id: TASKS-formal-doc-authoring-checkpoints
spec: SPEC-formal-doc-authoring-checkpoints
plan: PLAN-formal-doc-authoring-checkpoints
---

# Task Breakdown: `SPEC-formal-doc-authoring-checkpoints` Formal documentation checkpoints: route facts, review reimplementability, record assessments

## Phase 1: Implementation

- [ ] **Task 1.1**: Docs bundle guidance, reference template and template-list pins
  - **_Boundary**: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/, packages/devkit-docs/tests/integration/bundles/docs/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/AGENTS.md.jinja, packages/devkit-spec/tests/integration/bundles/spec/
  - _Requirements: AC-01, AC-02_
  - **Verification**: `uv run pytest packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py`

- [ ] **Task 1.2**: `RULE-reconcile-contract` formal_docs form and newly-resolved coverage, with guide, tests and fixtures
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/governance/usecases/reconcile_contract.py, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/reconcile_contract/, packages/devkit-spec/tests/integration/features/governance/, packages/devkit-spec/tests/integration/features/worker/test_worker_inspect.py, packages/devkit-spec/tests/e2e/bundles/spec/test_formal_document_lifecycle_scenarios.py
  - _Requirements: AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `uv run pytest packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/reconcile_contract/tests` and `uv run devkit rules check specs/` compared with the base

- [ ] **Task 1.3**: Spec bundle sync, reviewer, plan and review wording
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/reconcile-reviewer.md, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-plan/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/, packages/devkit-spec/tests/integration/bundles/spec/
  - _Requirements: AC-07_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/integration/bundles/spec` and `uv run devkit rules check --phase hygiene packages/devkit-spec/src/devkit_spec/bundles/spec/bundle`

- [ ] **Task 1.4**: Living Spec capabilities and deferred-work feedback
  - **_Boundary**: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md, docs/capabilities/documents/CAP-DOCS-document-model.md, docs/capabilities/governance/CAP-GOV-spec-rules.md, docs/capabilities/delivery/CAP-DLV-delivery-workflows.md, specs/2026-11/20261116-formal-doc-authoring-checkpoints/
  - _Requirements: AC-06, AC-08_
  - **Verification**: `uv run devkit rules check --ci --base a7d96154e`
