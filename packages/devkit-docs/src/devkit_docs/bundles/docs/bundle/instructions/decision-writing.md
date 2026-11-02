---
name: decision-writing
description: Read before writing or editing an ADR (docs/decisions/) or a proposal's PADR. Defines when a decision warrants one, the Y-statement summary, context, options, outcome clauses with their restatement trace, consequences, the Confirmation section and supersession.
---

# Decision Writing

An ADR records one decision and its reasons. Start from the `decision` template; a PADR has the same sections.

## When to Write

These admission criteria apply to an ADR and to a PADR alike. Write one only when at least one holds:

- The decision is costly to reverse.
- It affects more than one package, feature area or document kind.
- More than one viable option was weighed.
- It changes an existing contract or lasting rule.

Record a choice that meets none of them in the proposal's Planning decisions or the spec's `plan.md` instead.

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

Capabilities and architecture documents state the lasting rules; the ADR records what was decided and why.

- Write one list item per clause, as a declarative sentence without an RFC 2119 keyword.
- End a clause that a capability or architecture document restates with its trace: the backticked ID, the section or
  rule that holds it and the keyword that document uses: "Exports write UTF-8. → `CAP-<AREA>-<slug>` rule 3 (MUST)."
- Leave the trace off a clause that no document restates; it records rationale or context only.
- If the restating document and the ADR differ, follow the restating document; the trace records where and how
  strongly the decision was restated.

## Supersession

- A decision that replaces an earlier ADR names it in `supersedes` and says in Decision Outcome which clauses it
  replaces.
- Set the earlier ADR to `status: superseded` with `superseded_by` only when the new decision replaces all of its
  in-force decisions; a superseded ADR leaves browsing and search.
- Otherwise the earlier ADR stays `accepted`, without `superseded_by`, and gains one line per partial superseder,
  below its heading or at the affected statement: "Superseded in part by `ADR-<new>`: <the replaced clauses>."
