---
id: TASKS-cloud-research-handoff
spec: SPEC-cloud-research-handoff
plan: PLAN-cloud-research-handoff
---

# Task Breakdown: `SPEC-cloud-research-handoff`

## Implementation

- [ ] **Task 1**: Ship the optional cloud request/intake/resume procedure and focused distribution contracts.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/SKILL.md`, `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/references/cloud-handoff.md`, `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/references/workspace.md`, `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/skills/deep-research/references/synthesis.md`, `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: focused catalog integration tests and semantic review of request/return/resume examples.
- [ ] **Task 2**: Verify installed cloud guidance and retained request/report preservation without devkit-spec.
  - **_Boundary**: `packages/devkit-catalog/tests/e2e/bundles/deep_research/test_installed_consumer.py`
  - _Requirements: AC-02, AC-06_
  - **Verification**: built-wheel installed consumer test and affected-test selector.
