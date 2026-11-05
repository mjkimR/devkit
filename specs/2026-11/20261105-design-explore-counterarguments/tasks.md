---
id: TASKS-design-explore-counterarguments
spec: SPEC-design-explore-counterarguments
plan: PLAN-design-explore-counterarguments
---

# Task Breakdown: `SPEC-design-explore-counterarguments`

- [x] **Task 1**: Make the optional response, evidence fallback and bounded disposition explicit in the existing skill and local roles, with deployed-content verification.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/SKILL.md`, `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/references/orchestration.md`, `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/roles/solution-explorer.md`, `packages/devkit-catalog/src/devkit_catalog/design_explore/bundle/skills/design-explore/roles/design-critic.md`, `packages/devkit-catalog/tests/integration/bundles/test_design_explore.py`, `packages/devkit-catalog/tests/e2e/bundles/design_explore/test_installed_consumer.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: Focused catalog integration and built-wheel consumer tests; semantic review of all five scenarios; catalog lint/types and affected tests.

Living Spec targets: `docs/capabilities/delivery/CAP-DLV-design-exploration.md` and
`docs/usecases/delivery/UC-explore-a-design-problem.md`. The promoted ADR already records the accepted direction;
no decision change is planned.
