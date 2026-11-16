---
id: PADR-problem-first-formal-document-openings
title: Problem-first formal document openings
summary: "For formal design, domain and operations documents, we open with the problem the document answers and keep the reader question as an authoring scoping step, to stop restating the summary, accepting that the question is no longer a visible section."
proposal: PROP-formal-document-templates
supersedes: [ADR-linked-domain-relationship-views]
status: draft
created_at: 2026-11-16
---

# [PADR-problem-first-formal-document-openings] Problem-first formal document openings

- **Status**: Draft
- **Date**: 2026-11-16

---

## 1. Context & Problem Statement

`CAP-DOCS-documentation-ownership` §3.3 asks authors to state the reader question, and
`ADR-linked-domain-relationship-views` §4 says a domain entry gives its question. The design and domain templates
turned that into an opening section. In the delivered documents that section restates the frontmatter `summary` as
an interrogative, which a reader arriving from `devkit docs list` or search has already read. No surveyed external
template places a question section beside a summary; a question appears at most as one sentence inside the problem
statement or as an authoring prompt (`materials/template-survey.md` §2).

This decision meets the admission criteria: it changes a lasting authoring rule in a capability and an accepted ADR
clause, and it applies to three document kinds.

## 2. Decision Drivers

- Each opening sentence adds information beyond `summary`.
- A document stays focused on one reader question.
- Templates, writing instructions and the capability state one consistent shape.

## 3. Considered Options

1. **Keep the question section.** No change, but the duplication stays and the operations template remains the
   exception.
2. **Problem-first opening with a scoping step.** The body opens with the problem per kind; settling the one
   question becomes an authoring step in the writing instruction.
3. **No opening section.** Rely on `summary` and start with the mechanism, concepts or symptom table. A document
   read without its frontmatter then has no framing.

## 4. Decision Outcome

Choose option 2.

Supersedes in part `ADR-linked-domain-relationship-views`: the clause that an entry gives its question; its
relationship overview, authority boundary and next useful step remain.

- A formal design, domain or operations document opens with the problem it answers: the problem the mechanism
  solves (design), the concepts readers confuse (domain) or the observed symptom (operations). It has no question
  section or label; at most one sentence of the problem statement is phrased as a question.
  → `CAP-DOCS-documentation-ownership` §3.3 Independent usefulness (SHOULD).
- Before writing, the author settles the one reader question the document answers and splits or drops a document
  that has none. The writing instruction of each kind carries this step.
  → `CAP-DOCS-documentation-ownership` §3.3 Independent usefulness (SHOULD).
- A formal document closes with its authority boundary, naming what it does not settle and the owner that does by
  full ID, and with its maintenance trigger and next useful action.
  → `CAP-DOCS-documentation-ownership` §3.3 Independent usefulness (SHOULD).

## 5. Consequences

- Good: the opening carries new information; the three kinds share one opening and closing shape.
- Bad: the question is no longer visible to a reviewer, who checks focus against the scoping step instead.
- Neutral: no rule checks sections; Review keeps judging semantic usefulness as before.

## 6. Confirmation

The three templates and writing instructions carry no question section or label and state the opening, scoping
step and closing above; `CAP-DOCS-documentation-ownership` §3.3 item 2 states the same; the delivered documents
agree with the proposal's Q3 outcome and pass `devkit rules check`.
