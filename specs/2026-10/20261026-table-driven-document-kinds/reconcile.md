---
reconcile_id: REC-table-driven-document-kinds
spec: SPEC-table-driven-document-kinds
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
---

# [REC-table-driven-document-kinds] Reconcile: Table-driven document kind definitions

## Living Spec changes

- `CAP-DOCS-document-model` section 3.2: the kind definition table is the single definition of kinds, with the facts
  each row holds and the `KindTableError` failure for an inconsistent table or a missing fact; the prefix and
  location table is unchanged. Section 4.4 names `definitions()`, `definition(kind)`, `relation_prefixes()`,
  `KindDefinition` and `KindTableError`, and that `PREFIXES` and `TERMINAL_STATUSES` derive from the rows.
- `CAP-GOV-spec-rules` section 3.2: a new shared-behavior item, "Kind facts", says the rules read their per-kind
  facts from the table when they run, that no rule code, message or remediation changed, and that a Living Spec kind
  without a grammar or an identifier target without a remediation fails the run. "Tuning" becomes item 9; nothing
  cites the item numbers.
- `ARCH-05-2-components`: one sentence says the documents feature owns the kind definitions every other feature reads.
- The rule guides under the `spec` bundle name no constant this change removed (`_LIVING_SPEC`, `_LIVING_DIRECTORIES`,
  `REQUIRED`, `ANCHORS`, `_KINDS`, `EXPECTED_PREFIX`, `SCOPE`, `NAMESPACE_SCOPE`), so the bundle and
  `.devkit/installation.json` are unchanged. No viewer document changes.

## Entrypoints

`CAP-DOCS-document-model` already lists `features/documents/` and `CAP-GOV-spec-rules` lists `features/governance/`
and the bundle rules, which cover every changed file; `entrypoints/services/paths.py` belongs to
`CAP-TRACE-code-entrypoints`, whose behavior is unchanged, so no entrypoint is added.

## Source feedback

- `FB-milestone-path-remediation-dated`: already resolved by `SPEC-link-prefixes-and-milestone-remediation`; this
  unit keeps that remediation text byte-for-byte (characterization).
- `FB-viewer-link-prefixes-drift`: out of scope (viewer); resolved by its separate bugfix, nothing to record here.

## Deferred work

None. `PROP-ux-documentation` adds its kind as a member, a row, a path grammar and templates on top of this table;
`PROP-foundation-documents` adds no row.
