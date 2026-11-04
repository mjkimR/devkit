---
id: PADR-explicit-ux-coverage-exception-notation
title: Explicit UX coverage exception notation
summary: For recognizing legitimate UX coverage gaps, we add a reasoned inline classification (a global Step cell and an off-screen step phrase) that RULE-ux-coverage honors, to keep warnings actionable, accepting one more micro-syntax in two documents.
proposal: PROP-ux-coverage-explicit-exceptions
supersedes: [ADR-ux-screens]
status: draft
created_at: 2026-11-04
---

# [PADR-explicit-ux-coverage-exception-notation] Explicit UX coverage exception notation

- **Status**: Draft
- **Date**: 2026-11-04

---

## 1. Context & Problem Statement

`ADR-ux-screens` lets a global control leave its Step cell empty and an off-screen step cite no screen, and makes
`RULE-ux-coverage` a warning so neither blocks a commit. The rule has no way to tell an intended gap from a forgotten
one, so every intended gap warns on every run, in the consumer evidence 40 times at once. The warnings stop
separating defects from decisions, and the cheap way to silence one is an invented citation, which `RULE-ux-links`
cannot distinguish from a true one. A per-item classification with a reason is needed; a global disable, a severity
downgrade or a heuristic on labels would hide the genuine gaps as well.

---

## 2. Decision Drivers

- Only an explicit, per-item classification counts; a blank cell or an uncited step alone never implies one.
- A reason stays beside the item so the owner reviews it where the gap is.
- No key that drifts when steps are renumbered or a trigger is renamed.
- Ordinary linked rows and steps carry no new boilerplate.
- `RULE-ux-links` keeps every contradiction error, and its module stays unchanged.
- A defective classification is as visible as the gap it covers.

---

## 3. Considered Options

- **Inline marker on the item** (selected): the Step cell `global: <reason>`; the step phrase `off screen: <reason>`.
  Lives with the item, no key, one more cell form and one more step phrase (the `resumes at <key>` precedent).
- **A frontmatter map of step key or trigger to reason**: keeps prose clean; dict-valued fields need parsing and the
  keys drift on renumbering, the reason `ADR-ux-screens` rejected the frontmatter step map.
- **A document-level "Coverage exceptions" section keyed by step key or trigger label**: readable in one place; same
  drift, a label match to validate, and the reason sits away from the item.
- **An HTML comment on the row or step**: invisible in rendered views and stripped by the rules' line reader.
- **Keep the current state**: every intended gap keeps warning; the proposal's problem stays.

---

## 4. Decision Outcome

Inline markers, because they alone meet the no-drift and no-boilerplate drivers and reuse the parser's phrase
precedent.

- A global interaction's Step cell is `global: <reason>`: lower-case `global`, a colon and a non-empty reason; the
  row serves no step. → `CAP-GOV-spec-rules` 3.16 (SHOULD)
- An off-screen main-scenario step or extension holds `off screen: <reason>` (`off-screen:` and any case count) in
  one of its lines; the reason is the rest of that line, a trailing `)` and whitespace dropped. → `CAP-GOV-spec-rules`
  3.16 (SHOULD)
- The shared UX model parses both markers once; `RULE-ux-links` treats a classified Step cell as an empty one and a
  cell mixing pairs and `global:` as invalid, through its existing cell check. → `CAP-GOV-spec-rules` 3.15 (MUST)
- `RULE-ux-coverage` does not report a row classified global with a reason or a step classified off screen with a
  reason. It reports, at its warning severity and with its own message, a classification without a reason and an
  off-screen classification on a step that cites a UX ID. → `CAP-GOV-spec-rules` 3.16 (SHOULD)
- The reason is checked for presence only; no heuristic on trigger or step wording decides a classification.
- An empty Step cell and an uncited step without a marker keep their current warnings; the `ux-writing` instruction
  names the `global:` form for a global control and `usecase-writing` the `off screen:` phrase, with one example each.
- This replaces, in part, two clauses of `ADR-ux-screens` (Step links and coverage): the coverage rule's "an
  interaction whose Step cell is empty" and "a step or extension that cites no UX ID" now exclude a classified item
  with a reason, and "only a step that truly happens off-screen cites none" gains the phrase that says so.

---

## 5. Consequences

- **Positive**:
  - Intended gaps stop recurring; the remaining warnings are candidates again.
  - The reason is reviewed where the gap is, by the owner, with no new document or field.
  - No change to `RULE-ux-links`, its errors or the flow graph.
- **Negative / Risks**:
  - One more Step cell form and one more step phrase for authors and the parser; a misspelled marker is silently a
    non-marker and the gap keeps warning, which is the safe failure.
  - A wrong but reasoned classification is accepted mechanically; only review catches it, as the proposal's threat
    model accepts.
- **Follow-ups**:
  - A spelling check for near-miss markers (`offscreen:`, `Global`) if consumers report gaps that stay warned after a
    classification was written.

---

## 6. Confirmation

- `RULE-ux-coverage` tests under its own `tests/` for each accepted and defective form; `RULE-ux-links` tests for the
  mixed Step cell. `CAP-GOV-spec-rules` 3.15 and 3.16 restate the clauses.
