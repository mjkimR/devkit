---
name: document-writing
description: Read before writing or editing any document (Living Spec, specs, guides, READMEs, agent assets). Defines the sentence-level baseline every document follows; the per-kind writing instructions add to it.
---

# Document Writing

An agent reads every document here before a person does. Write for a reader who knows the language, the tools and
the domain basics, and lacks only this repository's facts.

## Sentences

- State one directive or one claim per sentence. Split a sentence that stacks a condition, an action, an exception
  and a cross-reference into one list item each.
- Put the condition before the action: "If the bundle has no skeleton, create `plan.md`."
- Pair a prohibition with what to do instead when an alternative exists: "Edit the bundle source, not
  `.devkit/managed/`." A prohibition whose alternative is to do nothing stands alone.
- Give a reason in one clause when it changes how the reader applies the rule: "..., because the file is shared in
  the PR." Link background, history and rejected options by ID (ADR, MAT, SPEC) instead of retelling them.
- Write directives without hedges ("likely", "might", "probably"); state the condition under which they apply.
- Keep capitals for defined keywords (RFC 2119, and the keywords a per-kind instruction defines, such as EARS). A
  rule gets its force from its condition and reason, not from "CRITICAL", "ALWAYS" or bold text.

## Content

- Leave out what the reader already has: general language or tool knowledge, the title restated, text the same
  reader has just loaded from another document.
- Offer one default and the condition for its exception instead of a list of equal options.
- Show one concrete example per pattern (an exact command, output line or snippet) rather than an abstract
  description.
- Name exact identifiers in backticks: commands with their flags, codes, paths and IDs.
- Write no time-relative words ("recently", "the new X", "as of now"); name the version, date or ID instead.

## Layout

- Order content by when the reader needs it: purpose, constraints, procedure, completion check, references.
- Use a table for items compared on the same attributes, a numbered list for ordered steps and bullets otherwise.
- Give a heading to content a reader searches for; a single short paragraph needs none.

## Related Instructions

- Read `contract-authoring` when a document states a contract: normative keywords, measurable criteria, Non-Goals.
- Read `living-spec-writing` when writing under `docs/` or `specs/`: placement, history, summaries, references,
  terminology.
- Read `decision-writing`, `capability-writing`, `story-writing` or `architecture-writing` when writing that document
  kind.
