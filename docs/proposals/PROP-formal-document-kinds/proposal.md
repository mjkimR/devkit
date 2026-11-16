---
id: PROP-formal-document-kinds
title: First-class design, domain and operations document kinds
summary: "Registers design, domain and operations as formal document kinds with complete identity, governance, authoring, discovery and migration support, replacing the ID-free direction."
status: reviewing
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
    - docs/designs/
    - docs/domain/
    - docs/  # nearest existing parent for the planned docs/operations/ directory
    - docs/capabilities/documents/
    - docs/capabilities/distribution/
    - docs/capabilities/delivery/
    - docs/capabilities/governance/CAP-GOV-spec-rules.md
    - docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
    - docs/usecases/
    - docs/architecture/
    - docs/decisions/
    - docs/development/reference/
    - docs/steering/glossary.md
    - docs/README.md
    - docs/proposals/PROP-formal-document-kinds/
  excludes:
    - packages/devkit-spec/
    - packages/devkit-adaptive/
    - packages/devkit-viewer/
    - scripts/handbook.py
task_kind: feature
supersedes: PROP-operations-documents
workflow: sdd-proposal
---

# [PROP-formal-document-kinds] First-class design, domain and operations document kinds

## 1. Background & Hypothesis

The intended change is the documentation hierarchy as a supported system. Design, domain and operations require
formal Kind, prefix and ID standing with the existing document toolchain. Linked ID-free entries do not satisfy
this requirement. Their useful content and responsibility boundaries remain inputs to migration.

`SPEC-design-document-foundation` and `SPEC-domain-model-documents` delivered ID-free current entries.
`ADR-documentation-ownership-and-linked-design-entries` and `ADR-linked-domain-relationship-views` encode that
identity restriction. Planning must produce a new ADR superseding those clauses; it must preserve unique owners
and existing capability guarantees. The superseded operations proposal's Development work is unmerged and halted
at commit 55bc46fb5ce350e0a84666d6df338f8947e54e1b. Its copied source and evidence in
[materials](materials/README.md) are historical inputs, not current main implementation or formal-kind proof.

One coherent core Kind integration spec can deliver the model, governance, authoring, discovery and migration
contract. Required lifecycle and viewer integration remain separately owned by `PROP-design-document-lifecycle`
and `PROP-design-document-viewer`. The milestone is complete only when all three phases are verified.

## 2. Technical Spike Questions

- **Q1**: What exact directory, prefix, stem/H1 grammar, frontmatter, status and relation schema fits each kind?
  Proposed prefixes are DESIGN, DOMAIN and OPS. Each kind must receive a formal prefix; Planning confirms spelling
  and namespace behavior rather than making identity optional.
- **Q2**: Which independently maintained Markdown details deserve their own formal node, and which supporting
  Markdown or non-Markdown artifacts belong to an identified parent? Define canonical identity, nesting,
  navigation and migration without assigning IDs to CSV files or images.
- **Q3**: Which structured reference fields express the useful relationships, and how do identity aliases,
  current references, provenance and supersession remain distinct? Define source-entrypoint applicability per
  kind; do not copy CAP/UC reciprocal relation or code-entrypoint requirements without a role-specific reason.
- **Q4**: Which existing generic mechanisms already support the three kinds, and which explicit prefix, grammar,
  schema, help, rule or distribution inventories need extension? Produce and verify a complete support matrix.
- **Q5**: How can migration preserve incoming links, details and historical evidence while retaining public Python,
  CLI and JSON compatibility and docs-only built-wheel operation without a spec package dependency?

## 3. Proposed Design & Impact

### Formal model and governance

- Extend `packages/devkit-docs` Kind enum and definitions, coverage assertions and Living Spec path grammars for
  all three kinds. Declare appropriate directory, area policy, H1 token, summary, status and relation semantics.
- Extend parsing, aliases, namespace indexing, structured references and provenance wherever required by the
  selected schema. Define supported relations and applicable source entrypoints explicitly in current contracts.
- Provide identity, prefix/path/H1, metadata, alias, reference, format, summary and applicable code-entrypoint
  rule coverage. Preserve existing codes, deterministic actions and published output contracts.
- Audit index/list/filter/order, search modes and exact-ID pinning, resolve and incoming/outgoing refs. Update
  public Python APIs, serialized kind values, CLI choices/help and reference documentation consistently.
  Generic paths count when tested with actual new-kind nodes, not merely because an old owner links to content.
- Verify parity across existing published surfaces. `devkit-docs` registers bundles, commands, config templates
  and context documents; it has no document MCP service. Do not invent a new service to satisfy an assumed API.
  Planning may include runtime/core/CLI boundary changes actually needed for existing contracts; it must name any
  cross-package boundary extension and feature dependency rather than excluding runtime work by habit.

### Authoring assets and migration

- Replace ID-free design authoring with formal design guidance and template; add domain and operations writing
  instructions and templates. Update docs bundle registration/core selection, source AGENTS pointers,
  seed/docs/README.md, repository docs/README.md and relevant architecture-writing boundaries.
- Verify template directory distribution and exact instruction/template inventories, source sync, `get-context`
  discovery and installed-consumer built-wheel tests. Docs assets remain delivery-approach neutral.
- Migrate every canonical current document in the three role directories. Initial retained inputs are
  `docs/designs/distribution-transactions.md`, its `distribution-transactions/file-directory-replacement.md`
  detail, `docs/domain/delivery-relationships.md` and `docs/domain/bundle-selection-and-installation.md`.
  Reuse the archived operations sync composition as content input and create a canonical formal operations node.
- Repair selected capability/reference/glossary ingress, relative detail/artifact links and ID references in the
  same migration. Inventory the full current directories during Planning so these examples do not cap coverage.
- Preserve archived pilot materials and completed records as evidence. Publish a new superseding ADR and update
  the current documentation-ownership and document-model contracts to formal standing. Do not silently rewrite
  the accepted historical decisions or retain ID-free canonical entries as an optional parallel route.

### Ownership and integration

`packages/devkit-docs` owns core behavior and shipped neutral assets. The `docs/` boundary permits creation of
`docs/operations/`; other documentation changes remain limited to the role directories and current owners named
above, plus exact relevant contracts identified during Planning. Its existing CLI, governance, document
features and tests are in scope for Planning. Current owner documents may change only for the formal support and
migration contract; their distribution/recovery/delivery guarantees remain unchanged. The target blueprint lists
source interfaces and prospective canonical documents. Planning declares required feature dependencies.

`PROP-design-document-lifecycle` owns spec/adaptive workflow integration, lifecycle skill guidance and proposal
scaffolding. `PROP-design-document-viewer` owns viewer frontend/backend, public frontend libraries, generated
assets and handbook prefix/source lookup policy. These integrations are required phases, not optional fixes
triggered only by a pilot failure. Their separate ownership keeps this proposal one L feature integration.

### Expected acceptance evidence

- **F1 — Identity and schema**: Real design, domain and operations nodes load in global and registered namespace
  roots. Positive and negative tests cover metadata, status, prefix, path, H1, aliases and each supported relation.
  Detail identity and support-artifact policy are demonstrated with the retained transaction design.
- **F2 — Discovery and references**: Each kind passes list/filter, search and exact-ID/pinned lookup, resolve,
  incoming/outgoing prose and structured refs, rename/alias handling and namespace selection. Assert public
  Python/CLI/JSON kind values and compatibility, including legacy kinds and malformed/unresolved controls.
- **F3 — Governance**: Kind coverage/grammar assertions, ID, format, summary, reference and applicable entrypoint
  rules exercise all three kinds; invalid documents produce the expected stable codes and repair/action behavior.
- **F4 — Authoring and delivery**: Template-to-document authoring, source registration, sync and `get-context`
  visibility pass for all kinds. Distribution inventories and installed docs-only built-wheel consumption pass
  without importing `devkit-spec`. A neutral consumer acquires no implicit SDD lifecycle.
- **F5 — Migration and maintenance**: Every canonical current role document has its formal identity and all ingress,
  reference and artifact destinations remain usable. A create/update/rename/retire maintenance walkthrough and
  source-to-detail change retain one authoritative owner. Historical pilot evidence remains intact.
- **F6 — Coverage and regression**: A support matrix names every relevant existing surface, applicability,
  implementation owner and verification. Generic mechanisms have new-kind test proof. Existing kinds and package
  compatibility pass appropriate regression checks. Required lifecycle/viewer evidence is tracked in their
  dependent proposals and prevents milestone completion until delivered.

## 4. Lifecycle & Retirement Criteria

The corrected direction is in Planning review. Planning settles the schemas and complete
implementation contract before acceptance and handoff. One L core integration spec is the intended handoff.
Acceptance requires the planned formal-kind support matrix, migration inventory and superseding decision scope.
Development retirement requires F1–F6 evidence and reconciliation of current contracts and shipped assets.
The milestone additionally requires the lifecycle and viewer phases. Neither small code size nor owner-linked
ID-free navigation can substitute for formal support.

## 5. Planning decisions

The selected implementation contract is [core-contract](materials/core-contract.md). DESIGN/design,
DOMAIN/domain and OPS/operations use flat prefixed filenames, required metadata and optional typed relations.
Independent detail is a formal peer node. Status is draft, active or retired; only design accepts optional source
entrypoints. Parent-owned artifacts have a narrow explicit path exception. The three formal templates/instructions,
current migrations, public compatibility and required lifecycle/viewer interfaces are part of the core contract.
PADR-formal-role-document-identities records the lasting schema and partial supersession choice. No unresolved
user direction is inferred from the superseded ID-free sources. HIGH Development remains appropriate for public
Kind/identity/output contracts. Implementation size is not a criterion for dropping required runtime or governance.
