---
reconcile_id: REC-design-bundle-layout
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-namespaces.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
    resolution: modified
  - file: docs/README.md
    resolution: modified
  - file: docs/decisions/2026-11/20261116-area-scoped-design-bundles.md
    resolution: modified
  - file: docs/decisions/2026-11/20261116-formal-role-document-identities.md
    resolution: modified
  - file: docs/designs/distribution/DESIGN-distribution-transactions/design.md
    resolution: modified
  - file: docs/designs/distribution/DESIGN-distribution-file-directory-replacement/design.md
    resolution: modified
  - file: docs/domain/distribution/DOMAIN-bundle-selection-and-installation.md
    resolution: modified
  - file: docs/domain/delivery/DOMAIN-delivery-relationships.md
    resolution: modified
---

# Design bundle layout reconciliation

## Path grammar contracts

`ADR-area-scoped-design-bundles` records the layout and supersedes in part the flat canonical path clause for
design and domain documents and the `<ID>/artifacts/` support clause for design documents of
`ADR-formal-role-document-identities`, whose pointer sentence carries the same scope. `CAP-DOCS-document-model`
owns the kind table's layout fact (`flat`, `area`, `area-bundle` with its anchor), the derived `area_scoped`, the
bundle and area paths, support at any depth, strays, orphans and the `README.md` scope; the implementation is
`devkit_docs.features.documents.models.kinds` and `devkit_docs.features.governance.services.role_artifacts`.
`CAP-GOV-spec-rules` owns the rule behavior: the `RULE-id-convention` bundle and area grammar, off-grammar
non-Markdown reports (dotfiles excepted), and `RULE-spec-format` leaving support out of scope while deriving a
bundle anchor's ID from its directory. `CAP-DOCS-documentation-ownership` and `CAP-DOCS-namespaces` restate the
per-kind homes and support locations, `CAP-TRACE-code-entrypoints` makes bundle `design.md` anchors
entrypoint-bearing and keeps README and support paths ineligible, and `CAP-DOCS-document-search` removes the bundle
anchor file name from the exact-match pin. `docs/README.md` names the three role homes. Each statement was compared
with the code and rule tests at the review-03 head.

## Moved formal documents

| Removed path | Replacement | Identity check |
| :--- | :--- | :--- |
| `docs/designs/DESIGN-distribution-transactions.md` | `docs/designs/distribution/DESIGN-distribution-transactions/design.md` | `devkit docs resolve` returns the new path; incoming refs from `CAP-DIST-sync-and-transactions` and the peer design remain |
| `docs/designs/DESIGN-distribution-file-directory-replacement.md` | `docs/designs/distribution/DESIGN-distribution-file-directory-replacement/design.md` | Resolves; `devkit docs list design --file` on its `transaction.py` entrypoint returns it; its relative source link now climbs two more levels and the target exists |
| `docs/domain/DOMAIN-bundle-selection-and-installation.md` | `docs/domain/distribution/DOMAIN-bundle-selection-and-installation.md` | Resolves; incoming ref from `CAP-DIST-sync-and-transactions` remains |
| `docs/domain/DOMAIN-delivery-relationships.md` | `docs/domain/delivery/DOMAIN-delivery-relationships.md` | Resolves; incoming ref from `CAP-DLV-proposal-lifecycle` remains |

The handoff promoted `docs/proposals/PROP-design-bundle-layout/decisions/PADR-area-scoped-design-bundles.md` to
`docs/decisions/2026-11/20261116-area-scoped-design-bundles.md` as `ADR-area-scoped-design-bundles` (accepted), and
moved the proposal anchor and its feedback into this spec unit; no ordinary link named the old paths.

Each moved file gained `area` equal to its area directory; no body statement changed. None had support files, and
no ordinary Markdown link pointed at the old paths. Completed specs and materials that name the old paths stay as
history.

## Design, domain and operations impact

- Design: both designs moved without statement changes; their mechanisms (distribution transactions and file and
  directory replacement) are unaffected by this change, which touches documentation governance only.
- Domain: both documents moved without statement changes; no domain concept, identity or relationship changed.
- Operations: no operations document exists and the grammar stays flat; no action.
- No new design document is warranted: the layout mechanism is owned by `CAP-DOCS-document-model` and the ADR.

## Lifecycle consumers

The spec-sync skill, the brownfield migration reference, the proposal scaffold text and the adaptive documents
reference state the per-kind support location; lifecycle behavior is unchanged and their end-to-end scenarios pass
on bundle and area paths. These are bundle assets, not Living Spec files.

## Deferred work

`FB-viewer-adopts-bundle-grammar` records the viewer's adoption of the bundle grammar for
`PROP-design-document-viewer`, which continues its Development on the flat grammar.
`FB-draft-precedence-claim-unenforced` records the Planning observation about unenforced precedence claims.

## Entrypoints

`devkit spec entrypoints derive` proposed whole-boundary candidates (package roots, test trees and bundle assets)
for each modified capability and both designs; none was applied. The changed code is already reached by existing
entrypoints: `CAP-DOCS-document-model` names `packages/devkit-docs/src/devkit_docs/features/documents/` (kind
table, search), `CAP-GOV-spec-rules` names `packages/devkit-docs/src/devkit_docs/features/governance/`
(`role_artifacts`, `id_convention`, `spec_format`, `entrypoint_paths`), `CAP-DOCS-document-search` names
`search.py` and `CAP-TRACE-code-entrypoints` names `code_entrypoints.py`. Test trees and bundle assets are not
doorways, and the two designs moved without mechanism changes, so their entrypoints stay as they are.
