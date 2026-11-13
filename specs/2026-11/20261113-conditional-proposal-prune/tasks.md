---
id: TASKS-conditional-proposal-prune
spec: SPEC-conditional-proposal-prune
plan: PLAN-conditional-proposal-prune
---

# Task Breakdown: `SPEC-conditional-proposal-prune`

- [ ] **Task 1**: Select proposal cleanup from pinned committed history and preserve exact target validation, with integration and E2E regressions.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/cleanup.py`, `packages/devkit-spec/tests/integration/features/delivery/test_cleanup.py`, `packages/devkit-spec/tests/e2e/features/delivery/test_integration.py`, `docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md`, `specs/2026-11/feedback/20261113-integration-prune-without-proposal.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: targeted cleanup integration/E2E, lint, type checks and affected tests; pinned before/after target counts and unchanged handoff/retry identity.
