---
id: TASKS-ux-writing-non-page-surfaces
spec: SPEC-ux-writing-non-page-surfaces
plan: PLAN-ux-writing-non-page-surfaces
---

# Task Breakdown: `SPEC-ux-writing-non-page-surfaces` UX writing guidance for surfaces beyond pages and forms

## Phase 1: Instructions and template

- [ ] **Task 1.1**: Add the `Surfaces beyond pages and forms` section to `ux-writing`, extend its description, and
  pin each criterion in the guidance tests
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/ux-writing.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-06, AC-07, AC-08, AC-09_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec`;
    `uv run devkit rules check --phase hygiene packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/ux-writing.md`;
    the `rg` command of AC-09
- [ ] **Task 1.2**: Add the long-running and judged step criterion to `usecase-writing`, with its guidance test
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/usecase-writing.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py`
  - _Requirements: AC-05, AC-08, AC-09_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec`;
    `uv run devkit rules check --phase hygiene packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/usecase-writing.md`
- [ ] **Task 1.3**: Clarify the `ux` template's Interactions comment, keeping the pinned lines
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/ux.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py`
  - _Requirements: AC-02_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec`

## Phase 2: Rule behavior the guidance relies on

- [ ] **Task 2.1**: Pin that a `screen` and a `panel` with `usecases: []` and a header-only Interactions table pass
  both UX rules
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_links/tests/test_rule.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_coverage/tests/test_rule.py`
  - _Requirements: AC-06_
  - **Verification**: `just test devkit-docs packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_links/tests packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_coverage/tests`
