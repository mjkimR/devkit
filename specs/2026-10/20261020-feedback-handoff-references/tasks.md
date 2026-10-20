---
id: TASKS-feedback-handoff-references
spec: SPEC-feedback-handoff-references
plan: PLAN-feedback-handoff-references
---

# Tasks: `SPEC-feedback-handoff-references`

- [x] **Task 1**: Preserve generic directory spans and test concrete reference preservation.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/proposals/rewrite.py`, `packages/devkit-spec/tests/proposals/test_proposal_handoff.py`
  - _Requirements: AC-01, AC-03_
- [x] **Task 2**: Pin dropped-record citations only with verified committed evidence, with regression coverage.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/proposals/handoff.py`, `packages/devkit-spec/src/devkit_spec/proposals/history.py`, `packages/devkit-spec/tests/proposals/test_proposal_handoff_records.py`
  - _Requirements: AC-02, AC-03, AC-04_
- [x] **Task 3**: Repair two existing ADR citations and verify their historical source.
  - **_Boundary**: `docs/decisions/2026-10/20261020-reverify-closes-challenger-rounds.md`, `docs/decisions/2026-10/20261020-proposal-boundaries-name-existing-paths.md`
  - _Requirements: AC-05_

Reconciliation includes `docs/capabilities/delivery/CAP-DLV-proposal-incubation.md` and the authorized direct-fix
sources `specs/2026-10/20261020-draft-direct-acceptance/feedback/handoff-rewrites-generic-materials-span.md` and
`specs/2026-10/20261020-envelope-record-gaps/feedback/promoted-adr-cites-deleted-proposal-envelope.md`.
