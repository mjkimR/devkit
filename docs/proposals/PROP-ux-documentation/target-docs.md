---
id: PROP-ux-documentation-target
title: Target Living Spec Structure for PROP-ux-documentation
status: draft
proposal: PROP-ux-documentation
created_at: 2026-10-26
# The Living Spec files this proposal changes, one "- file: <workspace-relative path>" each;
# devkit spec scope compare reads them to find overlaps with other work.
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
  - file: docs/capabilities/documents/CAP-DOCS-namespaces.md
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
  - file: docs/glossary.md
---

# [Blueprint] PROP-ux-documentation: Target Living Spec Structure for UX documents, authoring guidance and use-case-driven review

This blueprint follows the Planning recommendations; the user's answers recorded for `worker-01.yaml` may change it.
It assumes `PROP-table-driven-document-kinds` has landed (its kind definition table is where the UX row goes) and
names the glossary at `docs/glossary.md`, which becomes `docs/foundation/glossary.md` if `PROP-foundation-documents`
lands first.

---

## 1. System Capabilities Plan (docs/capabilities/)

- `CAP-DOCS-document-model`: §3.2 gains the `UX` prefix, kind `ux` and location `docs/ux/<area>/UX-<slug>.md`;
  §3.3 rule 2 gains `usecases` and `capabilities` on UX documents and the `element` value; the UX row is stated as a
  row of the kind definition table.
- `CAP-DOCS-namespaces`: the namespace layout lists `ux/` next to `capabilities/` and `usecases/`.
- `CAP-GOV-spec-rules`: sections for the error-severity UX link rule (element, step keys, `usecases` agreement,
  targets, exits, modal close, reachability) and the warning-severity UX coverage rule (steps without a screen,
  interactions without a step), with their codes, and the UX rows of `RULE-id-convention` and
  `RULE-document-reference`.
- `CAP-DLV-delivery-workflows`: the `ux-reviewer` role contract and the `spec-ux-review` skill, the `ux-review`
  envelope kind outside the P1-P3 loop with its closing record, its placement (Planning, after `specify` at spec
  depth), its round cap and its line in the effort table.
- `CAP-VIEW-repository-viewer`: UX documents form their own book group and their IDs link in rendered pages.

## 2. Use Cases Plan (docs/usecases/)

Screens of a proposal are drafted here in the UX template's shape, with the use case step citations they need, before
Development (`PADR-ux-drafts-before-code`). This proposal drafts none: no use case of this repository changes: devkit's own interface (the viewer) gains UX documents only by a later
decision. The `usecase` template and the `usecase-writing` instruction allow a UX ID in a step.

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

- ADRs promoted from `PADR-ux-screen-documents`, `PADR-ux-step-links-and-coverage`, `PADR-ux-review-before-code` and
  `PADR-ux-drafts-before-code`.
- `docs/architecture/`: only if the building-block view lists document kinds or roles by count; checked at
  Development.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- `spec` bundle: a `ux` template, a `ux-writing` instruction (contrasting candidates in Planning, no character-cell
  layouts, medium left to the project), the `ux-reviewer` subagent and `spec-ux-review` skill, the two UX rules with
  their guides, a `docs/ux/` seed and a UX object table header in the seeded glossary of `docs-skeleton`, a Screens
  draft section in the target-docs blueprint and in `spec-specify`, and the move of drafts into `docs/ux/` in
  `spec-sync`, with new IDs in drafts written as plain text.
- `sdd-proposal` and the planning reference: the acceptance request lists `ux-review` rounds and their open findings.
- `docs/glossary.md`: the terms "UX document" and "UX object table" only.

---

## 5. System Before & After Comparison (Before & After)

| | Before | After |
| --- | --- | --- |
| Screens | Free-form materials or capability sections | `UX-*` documents linked to use case steps and capabilities |
| Coverage | None | The UX coverage rule over steps, interactions and targets |
| UX review | The author's own judgment | An isolated `ux-reviewer` walkthrough and rubric before code |
