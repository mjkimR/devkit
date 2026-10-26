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
(`usecase-writing` instruction) and capabilities own behavior contracts. A kind is identified only by its ID prefix;
registering one touches the ID grammar, the rules' directory and stem logic, relation-field typing, templates, seeds
and the viewer (`MAT-ux-documentation-planning-spike` §1). Practice separates screens (purpose, content, states,
interactions, exits) from flows (a screen inventory with a transition table) (`MAT-ux-documentation-practice` §1).

## 2. Decision Drivers

- One contract per fact: transitions are not written in two documents.
- Few kinds, prefixes and relation fields.
- A text contract owned by devkit and independent of the project's wireframe medium.
- Checkable structure: element, states, interactions and targets in fixed places.

## 3. Considered Options

- **One `UX` kind of interface elements, the use case as the flow**: one kind and one template; the flow graph is
  derived from the interactions' targets; no single overview of navigation.
- **Two kinds, `SCR` and `FLOW`**: an explicit overview; two kinds, two templates, and transitions repeated in the
  screens and the flow.
- **One kind with two document shapes told apart by frontmatter**: one kind, but each shape has its own sections and
  rules, so the template and every reader carry two schemas.
- **Keep the current state** (free-form materials or capability sections): no traceability and nothing to check.

## 4. Decision Outcome

Decided by the user (`ux-document-set` and `ux-objects`):

- One kind `ux`, prefix `UX`, at `docs/ux/<area>/UX-<slug>.md` and `docs/packages/<name>/ux/<area>/UX-<slug>.md`,
  statuses `draft`, `active` and `deprecated` (no terminal status, so `ADR-terminal-statuses-are-historical` needs no
  new entry). It is registered as a row of the kind definition table of `PROP-table-driven-document-kinds` (accepted).
  Visual style is not restated in UX documents; a screen refers to the project's steering style files.
- Frontmatter `element` is `screen`, `modal` or `panel`, a small value inside one schema that only the UX link rule
  (`RULE-ux-links` of `PADR-ux-step-links-and-coverage`) reads and validates; relation fields `usecases` (UC IDs) and `capabilities` (CAP IDs).
- Sections: Purpose, Content (prose region rules and a content tree with conditions next to its nodes; no
  character-cell layouts), States, Interactions (`Trigger | Step | From | To | Target | Capability | Feedback`) and an
  optional Evidence section naming the project's own wireframe, mock-up or screenshot.
- Objects are named by glossary terms. Their representations and calls to action per role live in the steering file
  `docs/steering/ux-objects.md` (one topic, under the steering caps of `PROP-foundation-documents`), scoped to
  the objects the use cases touch; the glossary's term table, its Owner check and its 24576-byte budget stay
  untouched, and devkit's own glossary gains only the new terms. The `ux-writing` instruction creates the file with the
  project's first UX document; `docs-skeleton` seeds nothing, so projects without an interface never carry it.
- The register meets the steering caps: its rows hold only the object, role, representation names and call-to-action
  names; at the 24576-byte body cap it keeps only the objects of use cases with UX documents; when no steering slot
  is free, the review records R6 as not applicable with the reason.
- The `ux-writing` instruction asks for two or three contrasting candidates where a screen's arrangement is open, in
  Planning only (proposal Planning, or inline Planning before `plan-intent` at spec depth); in Development the
  recommended candidate is taken and the others are recorded as an assumption in `spec.md`.

## 5. Consequences

- Positive: one place per transition; the reviewer and the rules read one table shape.
- Negative: no written overview of navigation across use cases.
- Follow-up: a derived navigation listing (from the targets) if projects report that screens alone are hard to
  navigate.
- Negative: a project with an interface spends one of its ten steering files on the register.

## 6. Confirmation

`RULE-id-convention` for the location, `RULE-document-reference` for the field kinds, `RULE-ux-links` of
`PADR-ux-step-links-and-coverage` for `element` and the Interactions table shape, and the template's skeleton check.
