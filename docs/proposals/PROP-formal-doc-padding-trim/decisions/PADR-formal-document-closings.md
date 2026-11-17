---
id: PADR-formal-document-closings
title: Formal document closings state limits and update triggers
summary: For formal design, domain and operations documents, we close with limits the body does not state and an Update triggers section, and state shared authoring steps once, to stop template-induced padding, accepting that next-read pointers live only in related_* fields and body links.
proposal: PROP-formal-doc-padding-trim
supersedes: [ADR-problem-first-formal-document-openings, ADR-linked-domain-relationship-views]
status: draft
created_at: 2026-11-17
---

# [PADR-formal-document-closings] Formal document closings state limits and update triggers

- **Status**: Draft
- **Date**: 2026-11-17

---

## 1. Context & Problem Statement

`ADR-problem-first-formal-document-openings` makes every formal design, domain and operations document close with an
authority boundary and a "maintenance trigger and next useful action", and has each kind's writing instruction carry
the scoping step. The templates turned that into two required sections with stock wording. Across the 13 documents
(1,063 lines) the boundary restates that the document "transfers no normative statement" or "owns no recovery",
which `CAP-DOCS-documentation-ownership` §3.1 and §3.3 already say of every document of the kind, and re-lists owners
the domain or routing table names. The next-action half repeats frontmatter `related_*` and the boundary, and the
broad section collects body content: a `RECOVERY_BLOCKED` routing rule in `OPS-distribution-sync`, owner-per-question
lines in two DOMAIN documents. The three writing instructions also copy the same six steps (materials
`document-audit.md`).

The decision changes clauses of two accepted ADRs and applies to three document kinds.

## 2. Decision Drivers

- Every closing sentence holds a fact the frontmatter, the table and the body do not.
- A section name predicts its content, so body facts stay in the body.
- A shared authoring step has one owner.

## 3. Considered Options

1. **Keep both sections and tighten the comments.** Least churn, but a required section with nothing new to say
   still invites a stock sentence.
2. **Narrow both sections and state shared steps once.** The boundary keeps only limits and owners the body lacks,
   and `## Update triggers` keeps only the source changes that make the document stale; shared steps move to
   `living-spec-writing`.
3. **Drop both sections.** The update trigger, which nothing else records, would be lost or scattered.

## 4. Decision Outcome

Choose option 2.

- A formal design, domain or operations document closes with `## Authority boundary` and `## Update triggers`.
  → `CAP-DOCS-documentation-ownership` §3.3 Independent usefulness (SHOULD).
- The authority boundary names what the document does not settle and its owner by full ID, only where the body or
  its table does not already name that owner, and what the document or its evidence cannot conclude. It carries no
  statement that the document transfers no normative statement or owns no recovery. A domain or operations document
  omits the section when nothing remains. → `CAP-DOCS-documentation-ownership` §3.3 Independent usefulness (SHOULD).
- `## Update triggers` names the source changes that make the document stale, by public entry point, use case,
  field, code or capability section. Next-read pointers go to `related_*` fields and body links; an operations
  fallback for evidence that matches no row belongs under `## Routing`.
  → `CAP-DOCS-documentation-ownership` §3.3 Independent usefulness (SHOULD).
- `living-spec-writing` states the authoring steps the three kinds share, the scoping step included; each kind's
  writing instruction keeps only its path, lead focus, body sections, closing and support location.

Supersedes in part `ADR-problem-first-formal-document-openings`: the clause that a formal document closes with its maintenance trigger and next useful action, and the clause that each kind's writing instruction carries the scoping step.

Supersedes in part `ADR-linked-domain-relationship-views`: the clause that an entry gives its next useful step.

## 5. Consequences

- Good: closings shrink to facts a reader acts on, and misplaced routing and owner lines return to the body.
- Bad: a reader who wants a "what next" pointer follows `related_*` or the table instead of a closing line.
- Neutral: no rule checks sections; Review keeps judging whether a closing sentence adds a fact.

## 6. Confirmation

The design, domain and operations templates and writing instructions state the two closings above and carry no stock
disclaimer; `CAP-DOCS-documentation-ownership` §3.3 rule 2 states the same; the 13 documents, less the folded
DESIGN-distribution-transactions, use `## Update triggers` and pass `devkit rules check`. Otherwise Review only.
