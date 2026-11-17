---
id: TASKS-viewer-host-wording
spec: SPEC-viewer-host-wording
plan: PLAN-viewer-host-wording
---

# Task Breakdown: `SPEC-viewer-host-wording` Reword viewer documents still written for library hosts

## Phase 1: Implementation

- [ ] **Task 1.1**: Reword `UX-view-decision` to the viewer page's own navigation
  - **_Boundary**: `docs/ux/viewer/UX-view-decision.md`
  - _Requirements: AC-01, AC-04_
  - **Verification**: `rg -n -i "host" docs/ux/viewer/UX-view-decision.md` prints nothing; `uv run devkit rules check`
- [ ] **Task 1.2**: Mark library-host parts of the two viewer ADRs as history
  - **_Boundary**: `docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md`, `docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md`, `specs/2026-11/20261116-viewer-internal-simplification/feedback/viewer-host-wording-outside-unit.md`
  - _Requirements: AC-02, AC-03, AC-04_
  - **Verification**: `git diff main -- docs/decisions/` shows unchanged outcome clauses; `uv run devkit rules check`
