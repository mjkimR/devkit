---
id: PROP-design-document-foundation
title: Design document ownership and document-system foundation
summary: "Defines implementation-design ownership against existing document kinds and adds design bundles to document identity, discovery, references and validation."
status: draft
created_at: 2026-11-16
target_area: documents/
priority: high
size: L
planning_effort: high
dev_effort: high
milestone: MS-implementation-design-documents
boundaries:
  owns:
  - packages/devkit-docs/
  - packages/devkit-core/
  - packages/devkit-cli/
  - packages/devkit-mcp/
  - docs/capabilities/documents/
  - docs/architecture/
  - docs/decisions/
  - docs/steering/
  - docs/development/reference/
  - docs/proposals/PROP-design-document-foundation/
  excludes:
  - packages/devkit-viewer/
  - packages/devkit-spec/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-design-document-foundation] Design document ownership and document-system foundation

## 1. Background & Hypothesis

Capabilities currently contain implementation detail and large examples alongside behavioral contracts.
`CAP-DOCS-document-model` has no dedicated home for a maintained implementation design and its supporting
artifacts. Dated materials preserve evidence, while architecture, UX and module references already own some
information that could otherwise be placed in a generic design directory.

A design layer can close this gap only if its responsibility is distinguishable from existing document kinds.
Clean role separation is the primary design criterion. Neither document length nor the presence of numbers
justifies moving content. Datasheets are a supporting-artifact use case, not a reason to relocate contract limits.

## 2. Technical Spike Questions

- **Q1**: What routing matrix distinguishes capability, architecture, use case, UX, ADR, materials, module
  reference, development guide and implementation design? Which owner wins for ambiguous content?
- **Q2**: What belongs to a design entry document, an independently addressable detail document, or a supporting
  file such as a CSV datasheet? How are one-to-many and shared designs connected to existing contracts?
- **Q3**: What identity, bundle layout, summaries and relationship fields support discovery and references in
  global and registered package namespaces without creating duplicate authoritative statements?
- **Q4**: Which existing index, CLI/MCP, search and rule paths already consume the kind registry, and which need
  changes to support designs and links to non-indexed artifacts?

## 3. Proposed Design & Impact

- Establish the proposed `docs/designs/` layer for current implementation mechanisms, algorithms, internal
  collaboration and implementation strategies, with examples, diagrams and datasheets where needed.
- Specify role boundaries before settling templates or runtime behavior. Cover an interface limit, an internal
  algorithm, a cross-cutting dependency, a screen interaction, a choice rationale, a historical benchmark, a
  command example and a developer procedure as routing examples. Preserve each existing owner's responsibility.
- Define one authoritative home per statement and explicit links where another document needs that information.
  Keep authoritative contract limits in capabilities; keep historical evidence in materials. Do not reclassify
  all implementation detail in architecture or UX merely because designs now exist.
- Define a minimal entry document and optional supporting files. Settle the document-kind prefix, file naming,
  relations, independent detail identity and artifact handling during Planning; the discussed directory tree is
  an illustration, not an approved schema.
- Implement the chosen design identity, discovery, lookup, reference and validation behavior as one document-kind
  extension. Cover package namespaces and existing CLI/MCP and search surfaces. Add checks only for concrete
  identity, ownership-link or artifact-reference failures; semantic ownership remains a review concern.
- Keep document logic in `devkit-docs`; any shared model or adapter change is limited to exposing this extension
  through existing boundaries. Declare any required cross-feature edge explicitly during Planning.

### Expected acceptance evidence

- The routing matrix assigns a primary owner to every representative case and states when to link rather than copy.
- A small design works as one entry document; a larger fixture includes a separate detail, an example and a
  datasheet without treating every supporting file as a standalone indexed document.
- Existing lookup, search and reference behavior works for the chosen identity in global and package namespaces.
  Invalid identities, missing references and affected existing kinds have focused regression coverage.

## 4. Lifecycle & Retirement Criteria

Planning settles document roles and the schema before implementation. This proposal delivers the document-system
foundation; authoring lifecycle, viewer UX and repository migration are separate work. Acceptance and handoff use
the repository's proposal gates. Retirement requires verified runtime support and matching Living Spec contracts.
