---
id: TASKS-uiux-improve-impeccable-context-links
spec: SPEC-uiux-improve-impeccable-context-links
plan: PLAN-uiux-improve-impeccable-context-links
---

# Task Breakdown: `SPEC-uiux-improve-impeccable-context-links`

- [ ] **Task 1**: Implement bounded POSIX linking/checking and its filesystem/Git regression matrix.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/scripts/`, `packages/devkit-catalog/tests/integration/bundles/test_impeccable_context_links.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: shell syntax and helper subprocess tests in sh/dash with available macOS/GNU utilities.
- [ ] **Task 2**: Ship the script unchanged through projection and document bounded setup/recovery.
  - **_Boundary**: `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`, `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/README.md`, `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/references/orchestration.md`, `docs/capabilities/delivery/CAP-DLV-uiux-improvement.md`, `docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md`, `docs/decisions/2026-11/20261113-impeccable-context-links.md`, `docs/decisions/2026-11/20261110-impeccable-session-authority.md`
  - _Requirements: AC-07, AC-08_
  - **Verification**: projection/authority tests and reconciliation against actual helper behavior.
