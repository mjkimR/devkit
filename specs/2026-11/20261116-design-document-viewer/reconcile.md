---
reconcile_id: REC-design-document-viewer
status: pending
targets:
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-release-handbook.md
    resolution: modified
  - file: docs/usecases/viewer/UC-read-formal-document.md
    resolution: modified
  - file: docs/ux/viewer/UX-browse-formal-documents.md
    resolution: modified
  - file: docs/ux/viewer/UX-formal-document-relations.md
    resolution: modified
  - file: docs/ux/viewer/UX-read-supporting-artifact.md
    resolution: modified
  - file: docs/steering/ux-objects.md
    resolution: modified
  - file: docs/development/reference/viewer.md
    resolution: modified
  - file: docs/materials/2026-11/20261116-design-document-viewer/support-matrix.md
    resolution: modified
  - file: docs/materials/2026-11/20261116-design-document-viewer/development-evidence.md
    resolution: modified
  - file: packages/devkit-viewer/README.md
    resolution: modified
  - file: packages/devkit-viewer/frontend/README.md
    resolution: modified
  - file: docs/usecases/viewer/UC-read-decision-supersession.md
    resolution: waived
    rationale: Existing ADR/PADR decision-only supersession remains unchanged and passes its retained regression suite; formal role context is specified by the new use case.
  - file: docs/ux/viewer/UX-view-decision.md
    resolution: waived
    rationale: Existing decision reading layout and controls retain their contract; the separate formal reference panel and support surfaces are described by the three new UX documents.
  - file: docs/ux/viewer/UX-decision-supersession.md
    resolution: waived
    rationale: Decision supersession resolution and displayed statement semantics remain ADR/PADR-only; the new formal document roles do not acquire this control.
---

# [REC-design-document-viewer] Formal document viewer reconciliation

## Current contract reflection

`CAP-VIEW-repository-viewer` owns canonical/alias identity, explicit chapter order, filtered book search/history,
source-bound hidden-target materialization and contextual Back; shared Read/Files current relations distinguish
provenance and incomplete scans. Eligible indexed documents declaring typed formal-role relations opt into cold
rendered Files context; raw files, supporting artifacts, handbook and unrelated/no-ID files retain their scan
budget. Supporting file reading covers bytes, safe previews, URI fragments, raw/download, cancellation and disposal.

`UC-read-formal-document` and all three drafted UX screens describe the delivered main and exception routes, and
are registered in the root UX object register. The two package READMEs and viewer reference restate the existing
public data-source interface and the newly available reading surfaces. The support matrix and development evidence
map all three kinds, retained UX findings, before/after measurements and actual source/package checks.

`CAP-DLV-release-handbook` records formal source/alias recognition and staleness/citation checks without changing
required CAP/UC coverage, deterministic ADR/SPEC membership or authorizing any handbook refresh.

## Structure, decisions and terminology

The viewer retains its existing frontend ownership and generic backend tree/blob boundary; no package, feature
edge, layer, Python document-engine dependency, architecture declaration or required host callback was added.
Incoming-reference inspection of `CAP-VIEW-repository-viewer` and `CAP-DLV-release-handbook` confirms the existing
architecture/ADR descriptions still apply. No architecture or ADR body requires repair. Existing decision reading
and supersession use case/screens are explicitly waived above because their semantics remain unchanged.

Formal role identity, supporting-artifact ownership and retirement are the delivered core contracts. This unit
consumes their existing terms and does not redefine the glossary or add an independent migration/recovery engine.
The immutable core-contract material remains byte-identical to the selected core delivery.

## Entrypoints

The existing viewer capability entrypoints cover its owned backend/frontend modules. The new use case names
`SddViewer.svelte` and `KnowledgeViews.svelte`, the two starting points for Files and Read. The handbook capability
already names its owning playbook and `scripts/handbook.py`. Derivation is reviewed at this stage; helper/test,
static, document and cross-owner candidates are rejected rather than appended mechanically.

## Completion and source feedback

No required acceptance criterion is deferred, and this unit has no explicitly linked open direct-fix feedback.
All findings in code review rounds 1 and 2 are corrected; fresh round 3 has no findings. The review's independent
probes and the worker's frontend249, affected294, backend/handbook155, public-host and exact wheel100 evidence
remain distinguished by their recorded source identities. Independent reconcile verification is recorded next.

Integration, lifecycle reference transactions and combined landed-head verification remain Host-owned. This
reflection does not close the documentation evolution milestone or adopt later unapproved layout/template work.
