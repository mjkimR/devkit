---
reconcile_id: REC-ux-documentation
spec: SPEC-ux-documentation
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-namespaces.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
---

# [REC-ux-documentation] Reconcile: UX documents, authoring guidance and use-case-driven review

## Living Spec changes

- `CAP-DOCS-document-model`: the `UX` row of the prefix table (section 3.2) and a paragraph stating the `ux` row's
  facts (Living Spec, area-scoped, summary always, heading token, no `entrypoints`, no terminal status, no relation
  field taking its IDs); rule 3.1.6 requires a summary on UX documents; rule 3.3.2 names a UX document's `usecases`,
  `capabilities` and its scalar `element`; the alias field and renaming lists name `UX`; section 4.1 gains `element`
  and `area` covers UX documents.
- `CAP-DOCS-namespaces` section 3.4: the rules check a namespace's `ux/` directory, and the UX rules read its UX
  documents and use cases as the global ones.
- `CAP-DOCS-document-lookup` section 3.4: `list` accepts the `ux` kind.
- `CAP-GOV-spec-rules`: fourteen rules; catalog rows for `RULE-ux-links` and `RULE-ux-coverage` (a warning); the UX
  stem of `RULE-id-convention`; the UX scope of `RULE-spec-format` and `RULE-document-summary`; the UX fields of
  `RULE-document-reference`; sections 3.15 and 3.16 with the step model, every report, the placement on the UX
  document or the use case, and the coverage warning's placement; `related` names `spec:ux-writing` and
  `spec:usecase-writing` for the UX rules.
- `CAP-DLV-delivery-workflows`: seven role contracts and five read-only roles; rule 15 places the optional UX review
  (Planning at `spike`, or inside `specify` / `characterize` before the plan), its walkthrough and six-item rubric, no
  severity, at most two rounds, the closing envelope, the effort recommendation and the `ux-review` rounds in the
  `plan-accept` request; section 4.5 the `ux-review` envelope kind; section 4.6 the `ux-reviewer` row and its
  delegation without a stage.
- `CAP-VIEW-repository-viewer` section 4.3: the book's chapter groups in order, UX included, and ID links for every
  indexed ID, UX included.
- `docs/steering/glossary.md`: the rows **UX document** and **UX object register** (body 9351 bytes, under the 24576
  cap).
- No change: `docs/usecases/` (no use case of this repository changes; Non-Goal 7) and `docs/architecture/` (no
  building-block view counts document kinds or roles).
- The handed-off ADRs (`ADR-ux-screen-documents`, `ADR-ux-step-links-and-coverage`, `ADR-ux-review-before-code`,
  `ADR-ux-drafts-before-code`) hold as delivered; this spec drafts no screens, so there is no drafted screen needing a
  `docs/ux/` target.

## Entrypoints

`CAP-GOV-spec-rules` lists `features/governance/` and the bundle `rules/`, which hold both UX rules and the shared
`services/ux.py`; `CAP-DOCS-document-model` lists `features/documents/`, which holds the kind row. No entrypoint
changes.

## Source feedback

None: the proposal's two feedback records are resolved.

## Deferred work

- `docs/README.md` (the repository's directory map) has no `ux/` row, and the subagent, rule, instruction and skill
  lists of `CAP-HARN-agent-guidance` section 4.1 do not name the new assets (they already omitted
  `RULE-steering-documents`). Both paths are outside this unit's write scope; `FB-agent-guidance-asset-list-drifts`
  records them for the Host.
- `docs/ux/README.md` is seeded into this repository by `devkit sync` (the `docs-skeleton` preset is selected) and is
  outside the write scope; it is left uncommitted and named as the problem of this run's `worker` envelope, because
  `devkit sync --check` exits `1` until it is committed.
