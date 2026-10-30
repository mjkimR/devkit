---
id: TASKS-alias-references-in-quick-references
spec: SPEC-alias-references-in-quick-references
plan: PLAN-alias-references-in-quick-references
---

# Task Breakdown: `SPEC-alias-references-in-quick-references` Check document IDs in quick references and keep rename tables intact

## Phase 1: Rule

- [ ] **Task 1.1**: `quick_references` setting, the quick-reference check and its alias fix, with rule tests
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/usecases/document_reference.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit-docs packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference`, `just check devkit-docs`, `just lint devkit-docs`

- [ ] **Task 1.2**: Rule guide: quick-reference check, `quick_references` setting, Remediation without the stale
  ADR/PADR clause; `devkit sync` outputs
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/guide.md`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`,
    `.devkit/installation.json` (sync output), `AGENTS.md` (sync output)
  - _Requirements: AC-04, AC-06_
  - **Verification**: `uv run devkit rules explain RULE-document-reference`, `uv run devkit sync --check`

## Phase 2: Content and guidance

- [ ] **Task 2.1**: Rewrite the repository's quick-reference alias citations and reword the viewer README sentence
  - **_Boundary**: `docs/development/ci-cd.md`, `docs/development/workflow.md`, `packages/devkit-viewer/README.md`
  - _Requirements: AC-05_
  - **Verification**: `uv run devkit rules fix`, then `uv run devkit rules check` reports no finding

- [ ] **Task 2.2**: `spec-specify` rename sentence with its guidance test
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-specify/SKILL.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py`,
    `.devkit/installation.json` (sync output)
  - _Requirements: AC-07_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py`
