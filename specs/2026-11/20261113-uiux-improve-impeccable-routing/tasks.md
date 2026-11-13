---
id: TASKS-uiux-improve-impeccable-routing
spec: SPEC-uiux-improve-impeccable-routing
plan: PLAN-uiux-improve-impeccable-routing
---

# Task Breakdown: `SPEC-uiux-improve-impeccable-routing`

- [x] **Task 1**: Implement the bounded question relay and fallbacks with contract assertions
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/`, `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`, `docs/capabilities/delivery/CAP-DLV-uiux-improvement.md`, `docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md`, `docs/decisions/2026-11/20261113-impeccable-question-relay.md`, `docs/decisions/2026-11/20261110-impeccable-session-authority.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: focused catalog integration, `just lint-check devkit-catalog`, `just check devkit-catalog`, `just test-affected --base 49326e950da64ff92cc23bbd128d9e68d0bcec80 --tier all`, cumulative CI rules and sync check
