---
id: PROP-design-document-foundation
title: Documentation ownership and minimal design foundation
summary: "Uses the early content pilot to define documentation ownership and choose the smallest design representation, adding runtime support only for demonstrated gaps."
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
  - docs/proposals/PROP-design-document-foundation/
  excludes:
  - packages/devkit-viewer/
  - packages/devkit-spec/
task_kind: feature
workflow: sdd-proposal
depends_on:
- PROP-design-document-pilot
---

# [PROP-design-document-foundation] Documentation ownership and minimal design foundation

## 1. Background & Hypothesis

Domain, design and operations are retained roles within the documentation system. The early examples in
`PROP-design-document-pilot` establish where each adds value and where existing owners already suffice.
Separate content locations, indexed kinds/IDs and dedicated tooling are independent decisions.

Architecture authors may know arc42. The missing guidance is architecture's boundary within the complete docs
system, rather than a tutorial on its chapters. Neither document length nor numerical content determines ownership.

## 2. Technical Spike Questions

- **Q1**: Which owner defines each representative statement across capability, architecture, domain, use case,
  UX, ADR, materials, reference, developer guide, operations, executable guidance and design?
- **Q2**: What minimal design entry and optional supporting files satisfy the pilot's reading and maintenance needs?
- **Q3**: Which demonstrated discovery or reference gap requires a new kind/ID, relation or runtime change, and
  which needs only content placement, links or existing configuration?
- **Q4**: Assuming arc42 knowledge, what architectural content is retained and what should cite another owner?

## 3. Proposed Design & Impact

- Use the early pilot to settle the common ownership matrix before finalizing schemas or runtime changes.
  Maintain domain, design and operations as explicit roles even where existing runtime facilities are reused.
- Define architecture's inclusion, exclusion and reference boundaries. Exercise strategy versus ADR rationale,
  building blocks versus internal mechanisms, runtime views versus use cases and algorithms, cross-cutting
  concepts versus domain meaning and common contracts, and deployment views versus operational procedures.
- Establish `docs/designs/` as the proposed current-design home, with entry documents and optional details,
  examples, diagrams and datasheets. Compare existing ARCH deep dives and linked references as implementation
  alternatives; architectural significance and content ownership decide routing, not length alone.
- Keep one authoritative statement and reference it from other views. Preserve contract limits in capabilities,
  rationale in ADRs and historical evidence in materials. Explicitly distinguish retained owners from transferred
  owners; an ownership transfer removes or replaces the old authoritative restatement in the same change.
- Adopt overview-to-detail reading paths and explicit boundary links. Keep uncertain findings in proposal/materials
  until supported. Reuse existing ownership metadata instead of creating parallel source-path registries.
- Decide content location, indexed kind/ID and dedicated tooling independently. Add only the identity, lookup,
  search, reference, namespace or artifact behavior required by an observed pilot gap. Existing facilities that
  meet the selected discovery contract pass without code changes. Add checks only for concrete failures.
- Keep document logic in `devkit-docs`; shared-model and adapter changes serve only demonstrated gaps. Declare
  any required feature edge in Planning. Domain and operations implementation belongs to
  `PROP-domain-model-documents` and `PROP-operations-documents`; this proposal establishes their shared boundaries.

### Expected acceptance evidence

- The matrix assigns one primary owner to each pilot statement and explains when to link or transfer ownership.
  An arc42-aware author can route the architectural overlap cases without relying on chapter names alone.
- A decision table separately justifies location, identity and tooling for each role. Existing-kind and linked-file
  alternatives are evaluated; new runtime support is conditional on a named unmet discovery or maintenance need.
- Selected design examples have usable entry paths and optional supporting artifacts, without mandatory empty
  hierarchy or independent IDs on every detail. Illustrative fixtures prove format behavior, not real demand.
- The chosen representation is verified in global and package namespace cases. Run focused regression tests only
  where runtime behavior changes; unchanged discovery paths have walkthrough evidence instead of invented code work.

## 4. Lifecycle & Retirement Criteria

Start after the early pilot. Planning settles roles and representation before implementation; acceptance and
handoff use the proposal gates. Retirement requires verified ownership conventions and selected discovery paths.
Runtime edits are required only for demonstrated gaps. Cross-layer lifecycle and viewer integration remain later work.
