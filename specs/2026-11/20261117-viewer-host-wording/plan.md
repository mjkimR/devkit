---
id: PLAN-viewer-host-wording
spec: SPEC-viewer-host-wording
---

# Technical Plan: `SPEC-viewer-host-wording` Reword viewer documents still written for library hosts

## 1. Constitution & Invariant Review

None. The constitution allows wording repair of an existing ADR without changing its decision; no ADR, architecture
or capability invariant changes. `ADR-internal-repository-viewer` is the cited reason for every history note.

## 2. Architecture Overview & Impact

- `UX-view-decision` (AC-01): replace "host screens" with the Read, Files and proposal detail views, "Existing host
  navigation" with the page's own navigation and "where the host offers it" with the document header's raw control.
  The content tree keeps its elements.
- `ADR-viewer-namespace-roadmap-discovery` (AC-02): mark the library-host sentence of the Context, the generic
  data-source driver and the two-route reading of the "Both dashboard routes" bullet as history; the bullet's
  structural-root rule stays as decided. The existing partial-supersession pointer stays.
- `ADR-viewer-indexed-decision-supersession` (AC-03): mark the host-neutral driver, the "library hosts" rejection
  reason and the "Both hosts" consequence as history. Decision Outcome is untouched.
- Design, domain and operations: unaffected; the change edits wording of one UX document and two ADRs, with no
  mechanism, concept or runbook.

## 3. Verification & Test Plan

- AC-01: `rg -n -i "host" docs/ux/viewer/UX-view-decision.md` prints nothing.
- AC-02, AC-03: `git diff main -- docs/decisions/` reviewed for unchanged outcome clauses; for AC-03 the Decision
  Outcome section diff is empty.
- AC-04: `uv run devkit rules check` on the changed documents and the unit.
- No code changes, so no lint, type or test run is needed.
