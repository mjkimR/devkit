---
id: MS-documentation-system-evolution
aliases:
  - MS-implementation-design-documents
title: Documentation system evolution
summary: "Establishes design, domain and operations as formal document kinds with complete identity, governance, authoring, discovery, lifecycle and viewer support while preserving distinct authoritative owners."
status: planned
created_at: 2026-11-16
depends_on: []
---

# [MS-documentation-system-evolution] Documentation system evolution

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification), §1.3
(Delivery Workflow Orchestration), §1.9 (Document Search) and §2 (Bounded Context) by evolving the complete
documentation hierarchy. Design, domain and operations become first-class formal document kinds, each with a
registered Kind, prefix, canonical ID, frontmatter contract, path grammar, templates and writing instructions.
Formal identity and complete support across existing relevant system surfaces are required outcomes.

Design explains current implementation mechanisms. Domain explains concepts, identity, relationships and
lifecycles. Operations composes symptoms, diagnostic evidence, applicable action owners and normal-state checks.
Capabilities retain behavioral guarantees, use cases actor goals, UX interactions, architecture system structure
and constraints, ADRs rationale, materials historical evidence and references syntax. Preserve one authoritative
owner per statement and existing safety, recovery and permission contracts.

`SPEC-formal-document-kinds` owns one coherent core Kind integration and migration. Its Planning confirms proposed
prefixes DESIGN, DOMAIN and OPS and appropriate per-kind schema, status, relations and source-entrypoint policy.
`PROP-design-document-lifecycle` and `PROP-design-document-viewer` are mandatory integration phases after that core.
Planning settles the implementation, without reopening whether these three roles receive formal identity.
Audit every existing relevant supported surface; reuse a generic mechanism when verification proves full support.
Implementation minimization is not a success criterion.

## Exit condition

- All three kinds have canonical identity in global and registered namespace roots. Their Kind definitions,
  prefixes, ID/frontmatter/H1/path grammar, aliases, summaries, statuses and appropriate structured relations agree.
  Planning defines whether each kind permits source entrypoints without copying CAP/UC semantics indiscriminately.
- Each kind has shipped templates, writing instructions, source registrations, seed guidance and hierarchy maps.
  Installed consumers receive consistent authoring assets through sync and `get-context docs`, including a
  docs-only built-wheel consumer without a `devkit-spec` dependency.
- Index, list/filter, search and exact-ID lookup, pinning, resolve, incoming/outgoing references, namespace
  selection and public Python/CLI/JSON interfaces support all three kinds. Identity, format, summary, reference
  and applicable code-entrypoint governance validate them with positive and negative evidence.
- All canonical current design, domain and operations Markdown documents migrate to the formal contracts.
  Migration repairs ingress links, references and supporting paths. Independently maintained design details have
  a coherent canonical identity policy; CSV, images and other supporting artifacts need no invented document ID.
  Archived pilots and measurements remain historical evidence rather than current canonical documents.
- A new ADR supersedes the accepted design/domain ID-free decision clauses. Responsibility separation, simple
  question-directed traversal and unchanged capability guarantees remain explicit in current contracts.
- Authoring, Planning, implementation review, reconciliation and maintenance support create, update, split,
  rename and retire for all three kinds under both SDD and adaptive-dev. Affected formal documents are required
  impact targets; unaffected layers need no arbitrary updates. Adaptive-dev acquires no implicit SDD records.
- The viewer provides complete kind navigation/groups, IDs and deep links, prose references, applicable metadata,
  relation graph, supersession recognition and supporting-artifact links in global and namespace views.
  Rendering, empty, missing and unsupported states follow existing supported behavior. Public frontend libraries,
  generated static assets, builds and packaging are verified. Handbook source lookup recognizes the kinds and
  distinguishes deliberate inclusion policy from silent omission.
- A per-kind support matrix records every audited surface, implementation owner, applicability decision and
  verification result. Real retained documents exercise authoring through migration, consumer distribution,
  maintenance and viewer use. Existing kinds and published compatibility contracts retain regression coverage.

## Non-goals

- **Scope Excluded**: replacing capability, architecture, use case, UX, ADR or materials responsibilities with
  design/domain/operations, or duplicating authoritative statements across them.
- **Scope Excluded**: a fixed authoring order, empty subdirectories for every design, whole-layer reading,
  all-pairs links, or updates to unaffected layers for every implementation change.
- **Scope Excluded**: a separate development-process methodology, parallel approval registry or unrelated workflow
  engine. Existing delivery approaches retain their authority and lifecycle.
- **Scope Excluded**: an arc42 tutorial or automatic creation of unused architecture chapters.
- **Scope Excluded**: an operational executor, automatic incident recovery or expanded permission to perform
  recovery effects. Existing action owners retain execution authority.
- **Scope Excluded**: proprietary editors, spreadsheet calculation engines, automatic design generation from code
  or moving archived historical evidence into current canonical ownership.

## Completion review

Decomposition: pending
Direct proposal work: pending
