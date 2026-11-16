---
id: PROP-design-document-foundation
title: Documentation ownership and minimal design foundation
summary: "Uses the completed pilot to settle documentation ownership and linked ID-free design entries, without new indexed kinds or runtime support."
status: accepted
created_at: 2026-11-16
target_area: documents/
priority: high
size: L
planning_effort: high
dev_effort: medium
milestone: MS-documentation-system-evolution
boundaries:
  owns:
  - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/
  - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/
  - docs/capabilities/documents/
  - docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
  - docs/architecture/README.md
  - docs/decisions/
  - docs/steering/glossary.md
  - docs/proposals/PROP-design-document-foundation/
  - docs/
  excludes:
  - packages/devkit-core/
  - packages/devkit-cli/
  - packages/devkit-mcp/
  - packages/devkit-viewer/
  - packages/devkit-spec/
  - packages/devkit-docs/src/devkit_docs/features/
task_kind: feature
workflow: sdd-proposal
depends_on:
- SPEC-design-document-pilot
---

# [PROP-design-document-foundation] Documentation ownership and minimal design foundation

## 1. Background & Hypothesis

`SPEC-design-document-pilot` retained domain, design and operations examples with unique existing authorities.
The supplied design entry reached an independent detail and source. Two independent contract-only trials found
no direct route to that detail. This supports a question-specific route, not a new indexed kind or UI.
The pilot did not execute package discovery, viewer navigation or recovery. Its four operations states include
no journal with desired-state drift: journal absence does not establish readiness.

Clean ownership is the primary driver. Domain, design and operations remain distinct roles alongside contracts
and architecture. Authors may know arc42; they need responsibility boundaries, not a chapter tutorial.
`materials/direction.md` records options, evidence identity, incoming-ref scope and limitations.

## 2. Technical Spike Questions

- **Q1 resolved for recommendation**: assign one normative owner by the statement's responsibility, with concise
  non-normative orientation elsewhere. The routing cases and ownership treatment are in `materials/target-docs.md`.
- **Q2 resolved for recommendation**: maintain an ID-free `docs/designs/<slug>.md` entry, with optional linked
  detail, diagrams, examples or datasheets only when useful. The retained mechanism needs entry plus one detail.
- **Q3 bounded**: add one ordinary link from the transaction capability to its maintained entry. Keep the entry
  outside the document index. Observe the withheld-name route during Development; no indexed design search,
  reverse-reference edge, automatic reference validation or viewer result is promised.
- **Q4 resolved for recommendation**: architecture retains system structure, system interactions, deployment,
  architectural constraints, cross-cutting technical concepts, quality and risk. Domain meaning, behavioral
  contracts, local mechanisms and operational actions retain their distinct owners.

## 3. Proposed Design & Impact

### Recommended direction

Adopt `PADR-documentation-ownership-and-linked-design-entries`. Separate physical home, identity and tools:

| Role | Content home | Kind / ID | Dedicated support |
| --- | --- | --- | --- |
| Domain | Chosen later by `PROP-domain-model-documents`; pilot remains evidence | Undecided there; no new kind here | Existing owner references; unsupplied discovery still untested |
| Design | `docs/designs/<slug>.md`; optional `<slug>/` supporting files | ID-free Markdown, including entry; no borrowed ARCH/MAT identity | One selected owner-to-entry ordinary link; existing indexed owner lookup |
| Operations | Chosen later by `PROP-operations-documents`; pilot remains evidence | Undecided there; no new kind here | Symptom/evidence → existing recovery owner → normal-state owner; no executor |

The entry alone states the question, mechanism overview, authority boundary and next useful detail or source.
Each detail can be read directly. Small designs may use only the entry. Examples and numerical datasheets are
content choices, not classification rules. Links are selected for reader questions; no all-pairs links, manual
reciprocal registry, fixed hop budget or whole-layer prerequisite is introduced. Existing `docs refs` supports
reverse lookup among indexed owners; ID-free design links do not become graph edges.

Domain concepts and relationships supply a conceptual basis alongside structure and contracts. There is no rigid
authoring order or required domain → architecture → design pipeline. Summaries may orient readers but do not
create a second normative owner. A genuine normative transfer removes/replaces the old restatement in the same
change and names the receiving owner. This foundation selects no transfer of existing pilot statements.

### Minimal implementation scope

1. Add the shared ownership contract CAP-DOCS-documentation-ownership (planned) under
   `docs/capabilities/documents/`; clarify the architecture boundary in `docs/architecture/README.md`.
   Add only three glossary role definitions if needed to avoid terminology ambiguity.
2. Update source `living-spec-writing.md` with concise responsibility routing and conditional loading of the
   relevant detail; update source `architecture-writing.md` with the ARCH overlap criteria in `materials/target-docs.md`.
   Add an ID-free `design-template.md` under the existing source templates directory. It is an optional authoring
   aid, not a generator, required folder scaffold, new bundle asset or runtime schema.
3. Adapt the retained pilot mechanism into `docs/designs/distribution-transactions.md` and
   `docs/designs/distribution-transactions/file-directory-replacement.md`. Replace evaluation/revision wording
   with maintained-current wording and repair source links for the new depth. Keep original pilot evidence intact.
   Add the question-specific ordinary link in `CAP-DIST-sync-and-transactions` §3 near transaction guarantees.
4. Promote the PADR through the normal proposal handoff and reflect its clauses in the shared contract and
   architecture boundary. No new package, feature edge, Kind, metadata field, registry, CLI/MCP adapter or runtime
   implementation is selected. `docs/` in boundaries names the nearest existing parent of the new designs home;
   it authorizes only those two new design paths, not unrelated documents.

Source bundle instructions implement the single shared ownership contract in consumer-generic form; they add no
independent normative matrix. Source changes contain consumer-generic rules and placeholders only. They cite no devkit repository IDs.
No package feature dependencies change; `.devkit/architecture.toml` needs no declaration. If subsequent evidence
requires runtime behavior, stop and return the missing outcome to the Host for scope review rather than silently
extending this plan. `dev_effort: medium` reflects content-only implementation with independent walkthrough and
review; high Planning remains justified by distributed authoring conventions and cross-kind ownership.

### Acceptance and verification

- **F1 ownership**: route the cases in `materials/target-docs.md`, including pilot passages, to one normative owner. No
  transferred contract, duplicate recovery procedure or new authoring DAG is present in the actual diff.
- **F2 representation**: the maintained entry works alone for overview and next action; the independent detail
  answers the mechanism question and reaches inspected source symbols. Optional artifacts need no independent ID.
- **F3 global discovery**: an independent reader receives only the transaction capability and original replacement
  question, before receiving entry filenames. Observe capability → maintained entry → needed detail/source.
  Retain opened sections, avoidable reads/returns and next-step clarity, even if the route fails. Contrast with
  pilot R1/V1 as qualitative historical evidence; claim no elapsed-time or numerical improvement.
- **F4 package validation**: in a disposable fixture at Development's authorized ignored probe path, register one
  package namespace and reproduce the same relative capability → ID-free design entry → detail/source route
  under its `docs/packages/<name>/` root. From package source cwd, verify owner search/list, resolve and refs obey
  existing namespace contracts; from global selection verify the package owner is filtered while global owners
  remain available. Assert no design search/resolve/refs coverage and no effect on an unrelated package owner.
  Use fixture names, not additional maintained design copies. Record all commands and actual reader navigation.
- **F5 distribution**: inspect the optional source template and source instructions in a consuming-repository
  fixture; no repository-specific IDs, mandatory empty hierarchy or projected-file edits appear. Validate required
  source asset rules and sync/distribution checks without expanding lifecycle integration.
- **F6 current-state checks**: review statement/source agreement, ordinary relative-link destinations and index
  exclusion for ID-free entries. Run scoped document and source asset rules, envelope checks and whitespace checks.
  Runtime tests are required only if an explicitly reauthorized runtime change exists; none is planned here.

Package probes are format/discovery validation, not evidence of real package documentation demand. A failed F3/F4
is a required outcome to fix or return, not permission to declare a new kind necessary. There is no arbitrary hop
cap. No runtime recovery, domain/operations unsupplied discovery or viewer success is claimed by this scope.

## 4. Lifecycle & Retirement Criteria

This Planning turn recommends a concrete direction; `plan-accept` and `proposal-handoff` remain `ask` gates.
It neither accepts nor hands off the proposal. No unresolved goal/scope question was found in this turn.

Retirement requires F1–F6 and the selected maintained design paths. `PROP-domain-model-documents` owns domain
homes and unsupplied discovery; `PROP-operations-documents` owns operations homes and unsupplied discovery;
`PROP-design-document-lifecycle` owns change-specific lifecycle integration; `PROP-design-document-viewer` owns
viewer verification. Those existing proposals remain unchanged. The pre-existing journal-ordering ambiguity
stays with `FB-runtime-journal-ordering`; it does not authorize an architecture correction in this foundation.
