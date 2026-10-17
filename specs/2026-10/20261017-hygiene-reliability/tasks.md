---
id: TASKS-hygiene-reliability
spec: SPEC-hygiene-reliability
plan: PLAN-hygiene-reliability
---

# Task Breakdown: Hygiene reliability

- [ ] **Task 1**: Preserve automatic hook fallbacks with regression coverage.
  - **_Boundary**: `packages/devkit/src/devkit/gate/hooks/hooks.py`, `packages/devkit/src/devkit/gate/hooks/local_config.py`, `packages/devkit/tests/gate/test_local_config.py`
  - _Requirements: AC-01, AC-02_
- [ ] **Task 2**: Resolve scope revisions before writing envelopes, with CLI regression coverage.
  - **_Boundary**: `packages/devkit/src/devkit/workflow/cli/envelope.py`, `packages/devkit/tests/workflow/test_layouts_and_authoring.py`
  - _Requirements: AC-03, AC-04_
- [ ] **Task 3**: Preserve optional finding severity with round-trip and invalid-input tests.
  - **_Boundary**: `packages/devkit/src/devkit/workflow/unit/envelope/model.py`, `packages/devkit/src/devkit/workflow/unit/envelope/authoring.py`, `packages/devkit/tests/workflow/test_layouts_and_authoring.py`
  - _Requirements: AC-05_
- [ ] **Task 4**: Split the library reference and repair inbound links.
  - **_Boundary**: `docs/development/reference/rules.md`, `docs/development/reference/rules-library.md`, `docs/capabilities/governance/CAP-GOV-rule-authoring.md`
  - _Requirements: AC-06_
