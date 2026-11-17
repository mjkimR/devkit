---
id: TASKS-viewer-adr-summary-wording
spec: SPEC-viewer-adr-summary-wording
plan: PLAN-viewer-adr-summary-wording
---

# Task Breakdown: `SPEC-viewer-adr-summary-wording` Reword viewer ADR summaries that name library hosts

## Phase 1: Implementation

- [x] **Task 1.1**: Reword the namespace roadmap ADR summary
  - **_Boundary**: `docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md`
  - _Requirements: AC-01, AC-03, AC-04_
  - **Verification**: `rg -n -i "^summary:.*(library|host)" docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md` exits 1
- [x] **Task 1.2**: Reword the indexed supersession ADR summary
  - **_Boundary**: `docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md`
  - _Requirements: AC-02, AC-03, AC-04_
  - **Verification**: `rg -n -i "^summary:.*(library|hosts)" docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md` exits 1
- [ ] **Task 1.3**: Resolve the source feedback
  - **_Boundary**: `specs/2026-11/20261117-viewer-host-wording/feedback/viewer-adr-summaries-name-library-hosts.md`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit rules check --ci --base main` exits 0
