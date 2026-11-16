---
id: PROP-domain-model-documents
title: Domain-model documentation
summary: "Adds maintained domain-model documentation for concepts, identity, relationships and lifecycles, with explicit ownership and integrated document discovery."
status: draft
created_at: 2026-11-16
target_area: documents/
priority: high
size: L
planning_effort: high
dev_effort: high
milestone: MS-documentation-system-evolution
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
  - docs/proposals/PROP-domain-model-documents/
  excludes:
  - packages/devkit-viewer/
  - packages/devkit-spec/
task_kind: feature
workflow: sdd-proposal
depends_on:
- PROP-design-document-foundation
---


# [PROP-domain-model-documents] Domain-model documentation

## 1. Background & Hypothesis

Glossary entries define terms, while capability and architecture documents explain individual contracts and
structures. Agents still need to assemble conceptual identity, relationships and lifecycles across those files.
A maintained domain model can make these meanings explicit without becoming a database schema or class catalog.

## 2. Technical Spike Questions

- **Q1**: How should domain concepts, identity, relationships, cardinality and lifecycles be represented and split
  into readable documents? Which concepts need independent identity and which belong to one domain entry?
- **Q2**: What definitions and conceptual invariants become authoritative here, and how should glossary,
  capabilities, architecture and designs cite them without duplicating rules?
- **Q3**: Does this require a separate indexed kind or an existing-kind convention? How will lookup, search,
  references, global/package namespaces and validation expose the chosen representation?

## 3. Proposed Design & Impact

- Apply `PROP-design-document-foundation`'s common ownership matrix. Define the domain-model home and document
  structure in Planning; `docs/domain/` is a candidate, not a pre-approved layout.
- Own conceptual meaning and relationships. Link command preconditions, error guarantees and payload schemas to
  capabilities; link implementation structures and algorithms to designs or architecture as appropriate.
- Include identity, relationship meaning, lifecycle and invariants only where they help readers understand the
  domain. Keep glossary entries short and linked to their defining owner; avoid a second authoritative definition.
- Use delivery and distribution examples: proposal/spec/milestone relationships, and bundle/asset/projection
  relationships. Distinguish membership, prerequisite and provenance; distinguish asset identity from file paths.
- Deliver the selected template, authoring convention, document discovery and references as one domain-document
  extension. Preserve existing package boundaries; identify any new feature edge in Planning.
- Leave cross-layer delivery workflow integration, viewer UI and migration to the common lifecycle, viewer and
  pilot proposals. Those depend on this proposal's finished conventions.

### Expected acceptance evidence

- Representative fixtures explain relationships and lifecycles without assuming Python classes, database tables
  or a particular storage format. A glossary reference and a capability reference reach one conceptual owner.
- Domain versus capability, architecture, design and ADR examples have explicit ownership, including ambiguous
  invariant cases. Existing document behavior and namespace discovery remain supported.
- Templates, identity/reference validation and CLI/MCP/search discovery cover the chosen representation with
  focused tests where behavior changes; no unrelated generic kind-extension platform is introduced.

## 4. Lifecycle & Retirement Criteria

Start after the common ownership foundation is delivered. Planning settles layout and representation; acceptance
and handoff use the proposal gates. Retirement requires documented conventions and verified document-system
support. Pilot content, cross-layer reconciliation and viewer changes remain in their own proposals.
