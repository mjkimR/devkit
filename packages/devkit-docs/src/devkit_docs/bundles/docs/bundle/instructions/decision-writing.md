---
name: decision-writing
description: Read before writing or editing an ADR (docs/decisions/) or a proposal's PADR. Defines the Y-statement summary, context, options, normative outcome clauses, consequences, the Confirmation section and whole or partial supersession.
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
- **Decision Outcome**: the chosen option first, then the reason tied to named drivers, in the clause format of
  Decision Outcome Clauses.
- **Consequences**: positive, negative or risks, and follow-ups; a follow-up names what triggers it.
- **Confirmation**: how compliance is checked: a rule ID, a test path, a review step or the restating IDs of
  Decision Outcome. Write "Review only" when no check exists, so the gap stays visible.

## Decision Outcome Clauses

Capabilities and architecture documents state the lasting rules; the ADR records why.

- Write one list item per clause.
- Give a normative clause one RFC 2119 keyword and the backticked ID of the capability or architecture document that
  restates it: "Exports MUST write UTF-8 → `CAP-<AREA>-<slug>`."
- Write a clause that no document restates without a keyword; it records rationale or context only.
- If the restating document and the ADR differ, follow the restating document; the ADR keyword records the strength
  intended at decision time.

## Supersession

- A decision that replaces an earlier ADR names it in `supersedes` and says in Decision Outcome which clauses it
  replaces.
- Set the earlier ADR to `status: superseded` with `superseded_by` only when the new decision replaces all of its
  in-force decisions; a superseded ADR leaves browsing and search.
- Otherwise the earlier ADR stays `accepted`, without `superseded_by`, and gains one line per partial superseder,
  below its heading or at the affected statement: "Superseded in part by `ADR-<new>`: <the replaced clauses>."
