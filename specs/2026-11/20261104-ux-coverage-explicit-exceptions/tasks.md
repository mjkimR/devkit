---
id: TASKS-ux-coverage-explicit-exceptions
spec: SPEC-ux-coverage-explicit-exceptions
plan: PLAN-ux-coverage-explicit-exceptions
---

# Task Breakdown: `SPEC-ux-coverage-explicit-exceptions` Recognize explicit global and off-screen UX coverage exceptions

## Phase 1: Model and rules

- [ ] **Task 1**: Parse the `global:` cell and the `off screen:` phrase in the shared UX model, with parser tests
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/services/ux.py`, `packages/devkit-docs/tests/integration/features/governance/test_ux_repository_usecases.py`
  - _Requirements: AC-01, AC-03, AC-07, AC-09_
  - **Verification**: `just test devkit-docs packages/devkit-docs/tests/integration/features/governance/test_ux_repository_usecases.py`
- [ ] **Task 2**: Honor the classifications, report the defective forms and target steps on the use case in `RULE-ux-coverage`, with rule tests
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/usecases/ux_coverage.py`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_coverage/tests/test_rule.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-09, AC-10_
  - **Verification**: `uv run devkit rules test RULE-ux-coverage`
- [ ] **Task 3**: Keep every `RULE-ux-links` error with a classified row present; update its docstring and the invalid-cell remediation text, with rule tests
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/usecases/ux_links.py` (text only), `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_links/tests/test_rule.py`
  - _Requirements: AC-07, AC-08, AC-09_
  - **Verification**: `uv run devkit rules test RULE-ux-links`

## Phase 2: Guidance

- [ ] **Task 4**: Rule guides, writing instructions, the `ux` template and `CAP-GOV-spec-rules`, then regenerate the managed copies
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_coverage/guide.md`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_links/guide.md`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/ux-writing.md`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/usecase-writing.md`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/ux.md`, `docs/capabilities/governance/CAP-GOV-spec-rules.md`, `.devkit/managed/docs/` (regenerated), `.devkit/installation.json`
  - _Requirements: AC-11_
  - **Verification**: the AC-11 `grep` lines; `uv run devkit sync --check`; `uv run devkit generated check`; `uv run devkit rules check docs/`
