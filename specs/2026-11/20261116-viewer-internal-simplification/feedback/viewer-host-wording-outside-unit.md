---
id: FB-viewer-host-wording-outside-unit
title: Viewer documents outside the internal-viewer unit still describe library hosts
scope: repo
kind: suggestion
category: instruction-conflict
target: docs/ux/viewer/UX-view-decision.md
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-11-16
---

# [FB-viewer-host-wording-outside-unit] Viewer documents outside the internal-viewer unit still describe library hosts

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `ADR-internal-repository-viewer` made the viewer a one-host internal tool and
  `SPEC-viewer-internal-simplification` updated the documents inside its boundary. Several viewer documents outside
  that boundary keep wording written for library hosts.
- **Proposed Procedure**: In a wording pass, reword `UX-view-decision` ("host screens", "Existing host navigation",
  "where the host offers it") to the page's own navigation, and mark the "Both dashboard routes" bullet and library-host
  drivers of `ADR-viewer-namespace-roadmap-discovery` and the library-host drivers and consequences of
  `ADR-viewer-indexed-decision-supersession` as history. No decision changes.
- **Expected Benefit**: A reader no longer infers an embedding host or generic tree/blob discovery the viewer dropped.
- **Cost & Risk**: Wording only; the ADR edits must keep each decision unchanged.
- **Attempted**: Hypothesis; the reconcile-reviewer of the unit judged none of these a contract mismatch.

## Evidence

```text
docs/ux/viewer/UX-view-decision.md:21,26,48 host wording
docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md "Both dashboard routes" decision bullet
docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md drivers and consequences name library hosts
```

## Disposition

Resolved by `SPEC-viewer-host-wording`. `UX-view-decision` now names the page's own navigation, the Read, Files and
proposal detail views and the document header's raw control; `rg -n -i host` finds no match in it. The library-host
context, driver and "Both dashboard routes" bullet of `ADR-viewer-namespace-roadmap-discovery` and the library-host
driver, option and consequence of `ADR-viewer-indexed-decision-supersession` carry history notes citing
`ADR-internal-repository-viewer`; no decision clause changed, and the Decision Outcome of the second ADR is
byte-identical to the base. The unit's self-review (low effort) passed with no findings and `devkit rules check --ci`
reported no violation.
