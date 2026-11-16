---
id: MS-documentation-system-evolution
aliases:
  - MS-implementation-design-documents
title: Documentation system evolution
summary: "Establishes domain-model, implementation-design and operations documentation with clear ownership boundaries, integrated discovery and maintenance, and bounded repository pilots."
status: planned
created_at: 2026-11-16
depends_on: []
---

# [MS-documentation-system-evolution] Documentation system evolution

## Goal

Advances `ARCH-01-introduction-and-goals` §1.2 (Repository Governance & Deterministic Verification), §1.3
(Delivery Workflow Orchestration), §1.9 (Document Search) and §2 (Bounded Context) by giving agents a maintained
home for domain models, implementation-level design and operational guidance. Agents should understand the
system's concepts and relationships, locate its current implementation design and supporting artifacts, and
diagnose operational problems without assembling these views from unrelated contracts or historical evidence.

The intended design home is `docs/designs/`; domain-model and operations layouts are settled in proposal Planning.
Designs cover current implementation mechanisms and may group detailed examples, diagrams and datasheets.
Domain models explain concepts, relationships, identity and lifecycles. Operations guidance supports diagnosis,
recovery, upgrades and confirmation of normal operation. Clear responsibility boundaries with capabilities,
architecture, use cases, UX, ADRs, materials, module references, development guides and executable playbooks are
central to the theme. Proposal Planning settles concrete contracts and alternatives; the milestone does not
pre-approve a schema, a separate indexed kind for every layer, or an implementation choice.

Validate small real examples of all three roles before selecting their final representation or implementing
tooling. Decide content location, indexed kind/ID and dedicated tool or viewer support independently. Reuse
existing facilities where they satisfy the demonstrated need. Final integration checks revisit the retained
examples after conventions and any necessary runtime changes are delivered.

## Exit condition

- Authors can determine which existing or introduced document layer owns a piece of information, including
  ambiguous cases, without maintaining the same authoritative statement in multiple places.
- Architecture's responsibility within the complete documentation system is explicit. Authors may assume arc42
  knowledge, but can distinguish architectural content from behavioral contracts, domain meaning, implementation
  design and operational procedures, and know when to reference their owners instead of restating them.
- Current implementation designs can group independently readable details, examples, datasheets and assets
  behind a discoverable entry document. Small designs need no empty supporting structure.
- Domain-model documentation explains concepts, identity, relationships and lifecycles while retaining or explicitly
  transferring authoritative ownership. The initial conceptual view references existing validity and transformation
  contracts; changing the view's label does not create a second owner for the same invariant.
- Operations documentation connects symptoms, diagnostic evidence, recovery-owner selection and normal-state
  checks. It reuses capability recovery contracts, advisory actions, executable instructions, playbooks and references.
- All three roles have verified entry and reference paths in global and package contexts, with explicit handling
  of supporting files that are not indexed documents. Existing discovery and viewer facilities count as support
  where sufficient; new kind, search, relation, artifact or UI behavior requires a demonstrated gap.
- Authoring, implementation review and Living Spec reconciliation keep domain models, current designs,
  operational guidance and supporting artifacts aligned with implementation under the selected approach.
- An early content pilot demonstrates distinct value, clear ownership and preserved contracts for all three roles.
  Later authoring/lifecycle and viewer checks verify the chosen representations against the retained examples.
  Evidence distinguishes real maintenance needs from illustrative format fixtures and unverified assumptions.

## Non-goals

- **Scope Excluded**: replacing capability, architecture, use case, UX, ADR or materials documents with design
  bundles, or classifying every detailed passage or numerical value as design content.
- **Scope Excluded**: mandatory migration of all existing documents, mandatory subdirectories for every design,
  or a new general-purpose development-process methodology.
- **Scope Excluded**: mandatory new kinds/IDs or dedicated UI for every role, parallel ownership registries or
  approval systems, and requiring unaffected documentation layers to change for every implementation task.
- **Scope Excluded**: an arc42 tutorial or automatic creation of unused architecture chapters. Clarifying adjacent
  architecture responsibilities does not require adding quality or risk chapters to this repository; those
  concerns already have a home in arc42.
- **Scope Excluded**: an operational executor, automatic incident response, or new authority to perform recovery
  effects. Operations documentation preserves existing permissions and execution ownership.
- **Scope Excluded**: editing proprietary design formats, spreadsheet calculation engines, automatic design
  generation from source code, or moving historical evidence into current design ownership.

## Completion review

Decomposition: pending
Direct proposal work: pending
