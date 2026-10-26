---
id: PADR-ux-screen-documents
title: One UX kind of screen documents
summary: For specifying what a person sees and operates, we add one UX kind whose documents each describe a screen, modal or panel by purpose, content tree, states and interactions, and let use cases carry the flow, to keep one prefix and a text contract, accepting no separate flow document.
proposal: PROP-ux-documentation
status: draft
created_at: 2026-10-26
---

# [PADR-ux-screen-documents] One UX kind of screen documents

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

The Living Spec has no document for what a person sees and operates. Use cases state intent without interface detail
(`usecase-writing` instruction) and capabilities own behavior contracts. A kind is identified only by its ID prefix,
and each prefix needs a row in the kind definition table of `PROP-table-driven-document-kinds`, a template and a
directory (`MAT-ux-documentation-planning-spike` §1). Practice separates screens (purpose, content, states,
interactions, exits) from flows (a screen inventory with a transition table) (`MAT-ux-documentation-practice` §1).

## 2. Decision Drivers

- One contract per fact: transitions are not written in two documents.
- Few rows in the kind table and few relation fields.
- A text contract owned by devkit and independent of the project's wireframe medium.
- Checkable structure: states, interactions and targets in a fixed table.

## 3. Considered Options

- **One `UX` kind of interface elements, the use case as the flow**: one row and one template; the flow graph is
  derived from the interactions' targets; no single overview of navigation.
- **Two kinds, `SCR` and `FLOW`**: an explicit overview; two rows, two templates, and transitions repeated in the
  screens and the flow.
- **One kind with two shapes told apart by frontmatter**: one row, but rules branch on a value the index does not
  model.
- **Keep the current state** (free-form materials or capability sections): no traceability and nothing to check.

## 4. Decision Outcome

Pending the user's answers to `ux-document-set` and `ux-objects` (Planning recommendation):

- One kind `ux`, prefix `UX`, at `docs/ux/<area>/UX-<slug>.md` and `docs/packages/<name>/ux/<area>/UX-<slug>.md`,
  statuses `draft`, `active` and `deprecated` (no terminal status).
- Frontmatter `element` is `screen`, `modal` or `panel`; relation fields `usecases` (UC IDs) and `capabilities`
  (CAP IDs).
- Sections: Purpose, Content (prose region rules and a content tree with conditions next to its nodes; no
  character-cell layouts), States, Interactions (`Trigger | Step | From | To | Target | Capability | Feedback`) and
  an optional Evidence section naming the project's own wireframe, mock-up or screenshot.
- Objects are named by glossary terms; a separate UX object table (representations and calls to action per role)
  joins the glossary under its own header, leaving the five-column term table and its Owner check unchanged.

## 5. Consequences

- Positive: one place per transition; the reviewer and the rules read one table shape.
- Negative: no written overview of navigation across use cases.
- Follow-up: a derived navigation listing (from the targets) if projects report that screens alone are hard to
  navigate.
- Follow-up: the UX object table lands on the glossary path that is current at Development
  (`PROP-foundation-documents` moves it).

## 6. Confirmation

`RULE-id-convention` for the location, `RULE-document-reference` for the field kinds, the UX coverage rule of
`PADR-ux-step-links-and-coverage` for the table shape, and the template's skeleton check.
