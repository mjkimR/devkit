---
name: decision-writing
description: Read before writing or editing an ADR (docs/decisions/) or a proposal's PADR. Defines the Y-statement summary, context, options, outcome, consequences and the Confirmation section.
---

# Decision Writing

An ADR records one decision and its reasons. Start from the `decision` template; a PADR has the same sections.

## Summary

- Write `summary` as a compact Y-statement within the 300 characters of `RULE-document-summary`:
  "For <context or concern>, we <decision>, to <achieved quality>, accepting <downside>."
- Name the decision, not the topic: "we keep terminology in `living-spec-writing`", not "terminology placement".

## Sections

- **Context & Problem Statement**: the forces that require a decision: constraints and the current failure or cost.
  Leave out how the problem was discovered.
- **Decision Drivers**: one line per criterion the options are judged by.
- **Considered Options**: one or two lines per option with its main trade-off against the drivers. Include keeping
  the current state when it was viable.
- **Decision Outcome**: the chosen option first, then the reason tied to named drivers. Split a multi-part decision
  into one list item per part.
- **Consequences**: positive, negative or risks, and follow-ups; a follow-up names what triggers it.
- **Confirmation**: how compliance is checked: a rule ID, a test path or a review step. Write "Review only" when no
  check exists, so the gap stays visible.
