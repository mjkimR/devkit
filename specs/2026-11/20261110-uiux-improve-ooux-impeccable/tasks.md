---
id: TASKS-uiux-improve-ooux-impeccable
spec: SPEC-uiux-improve-ooux-impeccable
plan: PLAN-uiux-improve-ooux-impeccable
---

# Task Breakdown: `SPEC-uiux-improve-ooux-impeccable` OOUX-framed UI/UX improvement and Impeccable delegation

## Phase 1: Rename

- [ ] **Task 1**: Clean-break rename of the bundle, skill, module, entry point, data root and test paths, keeping every existing assertion with the new paths.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/uiux_improve/`, `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/`, `packages/devkit-catalog/pyproject.toml`, `.devkit/architecture.toml`, `packages/devkit-catalog/tests/integration/bundles/test_uiux_improve.py`, `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`, `packages/devkit-catalog/tests/e2e/bundles/uiux_improve/`, `packages/devkit-catalog/tests/e2e/bundles/app_uiux_improve/`
  - _Requirements: AC-07, AC-08_
  - **Verification**: `just test devkit-catalog packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`; AC-07 `rg` scan after Task 4.

## Phase 2: Instructions and guide

- [ ] **Task 2**: Rewrite `SKILL.md`, `references/design-guidance.md` and `references/orchestration.md` for proportionate ORCA framing, conditional OOUX sources, baseline craft checks, user-selected Impeccable delegation, routing, acceptance, project files and user-requested setup and cleanup, with `assert_rule` tests.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/`, `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-08, AC-09, AC-10_
  - **Verification**: `just test devkit-catalog packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`; `uv run devkit rules check --phase hygiene` on the skill directory; agent-asset ID scan.
- [ ] **Task 3**: Add the human usage guide `bundle/README.md`, link it from the catalog README and assert its contents and its absence from agent-read files, the managed set and projections in the integration and E2E tests.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/README.md`, `packages/devkit-catalog/README.md`, `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`, `packages/devkit-catalog/tests/e2e/bundles/app_uiux_improve/`
  - _Requirements: AC-11_
  - **Verification**: `just test devkit-catalog packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`; `just test-affected --tier e2e`.

## Phase 3: References

- [ ] **Task 4**: Rename the bundle in the installation guide, the catalog README section, the component description and the clause 1 bundle name of the superseded-in-part decision; the capability and use-case restatement lands with the reconcile.
  - **_Boundary**: `guides/install/bundle-recommendations.md`, `packages/devkit-catalog/README.md`, `docs/architecture/ARCH-05-2-components.md`, `docs/decisions/2026-11/20261105-uiux-improvement-workflow-boundary.md`, `docs/capabilities/delivery/CAP-DLV-uiux-improvement.md`, `docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md`
  - _Requirements: AC-07_
  - **Verification**: AC-07 `rg` scan reports no match; `just rules-check`.
