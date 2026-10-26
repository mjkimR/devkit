---
id: PROP-table-driven-document-kinds-target
title: Table-driven document kind Living Spec targets
summary: "Maps the kind definition table to the Living Spec documents Development reconciles, leaving every documented ID, path, rule code and message unchanged."
status: draft
proposal: PROP-table-driven-document-kinds
created_at: 2026-10-26
---

# [PROP-table-driven-document-kinds-target] Table-driven document kind reconciliation targets

- `CAP-DOCS-document-model`: section 3.2 states that one definition row per kind in the documents models is the
  single source of the prefix, kind order, Living Spec directory and the per-kind facts the rules read; the
  prefix and location table stays as written. Section 4.4 names the table beside `Kind`, `is_id` and `kind_of`.
- `CAP-GOV-spec-rules` (and the rule guides under the `spec` bundle only if they name a constant this change
  removes): the rules read Living Spec membership, summary requirement, entrypoint-bearing kinds and relation-field
  prefixes from the table; rule codes, messages and remediations do not change.
- `ARCH-05-2-components`: the devkit-spec paragraph beside the proposal and policy feature ownership gains one
  sentence that the documents feature owns the kind definitions every other feature reads; no new ARCH document.
- No viewer document changes: the viewer is out of scope.

Promote `PADR-kind-definition-table-keyed-on-the-declared-kind-enum` through normal handoff; it supersedes no ADR.
No current Living Spec is edited during Planning. `PROP-ux-documentation` and `PROP-foundation-documents` edit
`CAP-DOCS-document-model` too; the change that lands later rebases its edits on the earlier one.
