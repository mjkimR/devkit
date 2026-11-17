---
reconcile_id: REC-viewer-host-wording
status: resolved
targets:
  - file: docs/ux/viewer/UX-view-decision.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md
    resolution: modified
formal_docs:
  design: "none: wording-only change to one UX document and two ADRs; no viewer source or mechanism changed"
  domain: "none: no domain concept, identity or lifecycle is introduced or renamed"
  operations: "none: no runbook, symptom or action owner is affected"
---

# Reconciliation: `SPEC-viewer-host-wording`

## Contract comparison

- `UX-view-decision` (AC-01): "host screens", "Existing host navigation" and "where the host offers it" now read as
  the Read, Files and proposal detail views, the page's own navigation and the document header's raw control. This
  matches `CAP-VIEW-repository-viewer` and `ADR-internal-repository-viewer`, under which `devkit viewer serve` is
  the only host. The content tree, states and interaction rows keep their elements, targets and capability links.
- `ADR-viewer-namespace-roadmap-discovery` (AC-02): history notes mark the library-host context, the generic
  data-source driver and the two-route reading of the "Both dashboard routes" bullet. The bullet's structural-root
  rule still matches `CAP-VIEW-repository-viewer` section 5 (dashboard and roadmap discovery). The existing
  partial-supersession pointer is unchanged; no outcome clause was added, removed or reworded.
- `ADR-viewer-indexed-decision-supersession` (AC-03): history notes mark the library-host driver, the library-host
  cost of the rejected server-endpoint option and the "Both hosts" consequence. The Decision Outcome section is
  byte-identical to the base, so `CAP-VIEW-repository-viewer` section 4.4 needs no change.
- Capabilities, use cases, architecture and glossary: unaffected; the change states no new behavior.

## Source feedback

- `FB-viewer-host-wording-outside-unit`: resolved; the whole proposed procedure is applied and verified by the
  checks above. Disposition appended to its file.

## Deferred work

Not part of this unit, and reported to the Host as feedback candidates:

- The frontmatter summaries of `ADR-viewer-namespace-roadmap-discovery` ("across local and library sources") and
  `ADR-viewer-indexed-decision-supersession` ("across hosts") still name library sources or hosts. They are left as
  decision-time summaries.
- The `.gitignore` and `ADR-package-ownership-and-release-version` items already listed in the deferred work of
  `SPEC-viewer-internal-simplification` are outside this unit's source feedback.
