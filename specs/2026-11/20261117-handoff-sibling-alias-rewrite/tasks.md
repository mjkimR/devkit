---
id: TASKS-handoff-sibling-alias-rewrite
spec: SPEC-handoff-sibling-alias-rewrite
plan: PLAN-handoff-sibling-alias-rewrite
---

# Tasks: `SPEC-handoff-sibling-alias-rewrite`

- [x] **Task 1**: Reproduce the stale sibling alias with regression tests, then rewrite alias references in the carried and promoted files inside the handoff.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/services/rewrite.py`, `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py`, `packages/devkit-spec/tests/integration/features/proposals/test_proposal_aliases.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: Proposals integration tests, lint, types, CI rules and affected tests.
- [x] **Task 2**: State the guarantee in the Living Spec and resolve the source feedback.
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md`, `docs/designs/delivery/DESIGN-proposal-handoff/design.md`, `specs/2026-11/20261117-adr-body-metadata-removal/feedback/handoff-leaves-stale-sibling-proposal-aliases.md`
  - _Requirements: AC-01, AC-02_
  - **Verification**: CI rules over the changed documents.
