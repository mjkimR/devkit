---
id: ADR-linked-domain-relationship-views
title: Linked domain relationship views
summary: "For maintained conceptual relationships, we use linked ID-free domain entries with existing contract owners, to give question-specific understanding, accepting owner-led discovery and review-only link checks."
proposal: SPEC-domain-model-documents
status: accepted
created_at: 2026-11-16
---

# [ADR-linked-domain-relationship-views] Linked domain relationship views

- **Status**: Accepted
- **Date**: 2026-11-16

---

## 1. Context & Problem Statement

The supplied domain pilot explains useful relationships, but its filename was supplied to the reader. Existing
contracts define validity and transformations without providing the selected conceptual compositions together.
Foundation retains domain as a distinct role and leaves its maintained home open.

## 2. Decision Drivers

- Give an entry that answers its conceptual question and identifies the next needed authority.
- Preserve existing unique normative owners and concise glossary definitions.
- Keep discovery question-specific and avoid identity/runtime surfaces without a required indexed outcome.

## 3. Considered Options

- Linked ID-free domain entries: distinct maintained relationship home using selected indexed-owner links;
  direct domain index queries are unavailable.
- Existing steering topic: viable short domain background with context discovery; per-topic whole-body reading
  and always-surfaced summary add load for these specific relationship questions.
- New indexed Kind: independent indexed identity; at least Kind enum and definition changes, with exact remaining
  consumer costs needing inspection. No agreed required outcome demands it.

## 4. Decision Outcome

Choose linked ID-free domain entries, conditional on independent global/package domain route validation in Development.

- Conceptual relationship entries use `docs/domain/<slug>.md`, or analogous `domain/` under a registered package
  docs root. → `CAP-DOCS-documentation-ownership` planned Domain representation subsection (SHOULD).
- An entry gives its question, relationship overview, authority boundary and next useful step; only useful detail
  is split. Selected owner links provide question-specific discovery without whole-layer prerequisites.
  → `CAP-DOCS-documentation-ownership` planned Domain representation subsection (SHOULD).
- ID-free domain files do not borrow indexed identity or promise search/resolve/refs nodes.
  → `CAP-DOCS-documentation-ownership` planned Domain representation subsection (MUST).
- Validity/transformation contracts retain their current owners; no normative statement transfers.
- No Kind, runtime, namespace schema, template, viewer or lifecycle automation is selected.

`ADR-documentation-ownership-and-linked-design-entries` and `ADR-document-system` remain in force.
No accepted ADR is superseded, wholly or partially. Common responsibility clauses remain with the existing shared
capability; generic source instructions implement them without a second normative matrix.

## 5. Consequences

Two maintained entries give bounded conceptual understanding alongside contracts and architecture. Existing owner
search/lookup leads to ordinary links. Direct domain index identity remains unavailable; link integrity and
source agreement need review. If corrected selected links still cannot meet D2–D4, return the named unmet outcome
to the Host before any runtime scope expansion. New Kind work needs its own evidence and authority.

## 6. Confirmation

Review only for semantic owner uniqueness, source agreement and ordinary navigation. D1–D6 in the blueprint require
independent withheld-entry global/package walkthroughs, negative identity controls, source asset delivery and scoped
checks. Domain discovery has not yet been demonstrated; Foundation's validated routes concern DESIGN only.
