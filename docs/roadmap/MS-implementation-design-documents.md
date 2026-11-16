---
id: MS-implementation-design-documents
title: Implementation design documents and supporting artifacts
summary: "Introduces a maintained implementation-design layer with examples, datasheets and supporting artifacts, with clear ownership boundaries against existing document kinds."
status: planned
created_at: 2026-11-16
depends_on: []
---

# [MS-implementation-design-documents] Implementation design documents and supporting artifacts

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification), §1.3
(Delivery Workflow Orchestration), §1.9 (Document Search) and §2 (Bounded Context) by giving agents a maintained
home for implementation-level design and its detailed supporting artifacts. Large examples, implementation
strategies, diagrams and datasheets should be discoverable without expanding capability contracts indefinitely
or making historical research serve as the current design.

The intended home is `docs/designs/`. Its defining concern is current implementation design, rather than document
length or numerical content. Clear responsibility boundaries with capabilities, architecture, use cases, UX,
ADRs, materials, module references and development guides are central to the theme. Proposal Planning settles
the concrete contracts and alternatives; this milestone frames the theme without pre-approving those choices.

## Exit condition

- Authors can determine which existing document kind or design document owns a piece of information, including
  ambiguous cases, without maintaining the same authoritative statement in multiple places.
- Architecture's responsibility within the complete documentation system is explicit. Authors may assume arc42
  knowledge, but can distinguish architectural content from behavioral contracts, domain meaning, implementation
  design and operational procedures, and know when to reference their owners instead of restating them.
- Current implementation designs can group independently readable details, examples, datasheets and assets
  behind a discoverable entry document. Small designs need no empty supporting structure.
- Document lookup, search, references, namespace handling and viewer navigation expose designs and their
  connections to existing contracts, with explicit handling of supporting files that are not indexed documents.
- Authoring, implementation review and Living Spec reconciliation keep the current design and its supporting
  artifacts aligned with implementation under the selected development approach.
- A bounded pilot on existing repository documents demonstrates clear ownership, preserved contract detail and
  usable navigation through an entry document to its supporting artifacts.

## Non-goals

- **Scope Excluded**: replacing capability, architecture, use case, UX, ADR or materials documents with design
  bundles, or classifying every detailed passage or numerical value as design content.
- **Scope Excluded**: mandatory migration of all existing documents, mandatory subdirectories for every design,
  or a new general-purpose development-process methodology.
- **Scope Excluded**: an arc42 tutorial or automatic creation of unused architecture chapters. Clarifying adjacent
  domain-model and operations responsibilities does not introduce their document kinds or runtime support.
- **Scope Excluded**: editing proprietary design formats, spreadsheet calculation engines, automatic design
  generation from source code, or moving historical evidence into current design ownership.

## Completion review

Decomposition: pending
Direct proposal work: pending
