---
id: PROP-operations-documents
title: Operations and recovery documentation
summary: "Establishes symptom-led operational guidance that routes to existing recovery owners, adding document tooling only for gaps demonstrated by the early pilot."
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
  - docs/proposals/PROP-operations-documents/
  - docs/ # nearest existing parent for the single new docs/operations/distribution-sync.md
  - docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
  - docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
  - docs/development/reference/distribution.md
  - docs/decisions/
  - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md
  excludes:
  - packages/devkit-core/
  - packages/devkit-cli/
  - packages/devkit-mcp/
  - packages/devkit-dist/
  - packages/devkit-spec/
  - packages/devkit-viewer/
task_kind: feature
workflow: sdd-proposal
depends_on:
- SPEC-design-document-foundation
---

# [PROP-operations-documents] Operations and recovery documentation

## 1. Background & Hypothesis

Operations documentation connects symptoms, diagnostic evidence, recovery selection and normal-state checks.
Existing status commands, advisory actions, recovery contracts, references and playbooks already cover parts of
that path. The early pilot determines what an operational entry adds without duplicating those sources.

## 2. Technical Spike Questions

- **Q1**: What operational content remains distinct from deployment architecture, capability recovery guarantees,
  advisory actions, command references, developer guides and executable instructions or playbooks?
- **Q2**: Which diagnostic evidence selects an existing recovery owner, and what applicability, prerequisites,
  stop conditions and success checks must the operational view provide?
- **Q3**: Which location, identity and tooling choices satisfy the demonstrated discovery need without new execution authority?

## 3. Proposed Design & Impact

### Planning decisions

Recommend linked ID-free `docs/operations/<slug>.md` entries; retain analogous `operations/` under a registered
package docs root. `PADR-linked-symptom-led-operations` records the viable alternatives and tradeoff. Location,
indexed identity and runtime support are separate decisions: choose this home, retain no indexed Kind/ID, and use
existing owner lookup plus ordinary links. ID-free entries remain absent from search/resolve/refs.

The single maintained example is `docs/operations/distribution-sync.md`. Its question is how a sync symptom and
evidence select the existing diagnosis/recovery authority and normal-state observation. It contains a useful
standalone overview, authority boundary, four evidence branches and next owner, adapted from pilot evidence.
A small entry needs no detail directory, empty hierarchy, new template, required reciprocal registry or hop cap.

Operations owns classification and applicability of evidence, not action guarantees: capability retains recovery
eligibility, version compatibility, stop conditions and readiness; actual advisory retains ACTION/FIX; executable
instructions/playbooks retain steps and permissions; reference retains syntax/error mapping. Use concise cited
summaries and links. Transfer no normative statement and copy no recovery procedure. Topology stays architecture;
incident history stays materials. Unknown evidence routes to the actual advisory's reporting/stop owner rather
than an invented recovery branch. No new execution authority, engine, incident system or runtime feature edge.

Add selected question-specific ordinary links at the transaction capability's Recovery passage and distribution
reference's Error codes/status discussion. They point to classification, while their present contracts and
procedures remain intact. The shared ownership capability is the single normative home for the operations
representation convention; extend its Scope and an Operations entries section. Extend the source
`living-spec-writing.md` with consumer-generic guidance consistent with that owner, without repository IDs or a
second ownership matrix. Exact future paths and section scopes are in `PROP-operations-documents-target`.

No edit to advisory code, executable consumption guidance, deployment/runtime architecture, glossary, identity,
search, namespace configuration, CLI/MCP or viewer is selected. A failed required route triggers a recorded cause
and corrected selected link/content within scope, or a Host scope decision; it never silently authorizes runtime.

### Required Development acceptance evidence

- **O1 — Maintained composition:** adapt one entry with question, overview, authority boundary and next action.
  An independent reader follows each of the four documented states: pending journal/`TRANSACTION_PENDING`,
  later-edit `RECOVERY_BLOCKED`, legacy journal lacking `directories`, no-journal desired-state drift.
  Cite each discriminator's existing owner. No-journal drift remains not ready: the readiness owner interprets
  `sync --check` exit 0 as ready and 1/2 as not ready. This is a documentation trial, not recovery execution.
- **O2 — Withheld-entry global discovery:** give a fresh independent reader the symptom question and the actual
  existing distribution reference Error codes/status entry, without the operations filename/path. Record actual
  sections opened, link traversals, wrong turns, conclusion and missing path. Also start from the transaction
  capability reached by existing lexical `TRANSACTION_PENDING` search; record observed search results instead of
  promising rank. The entry must be reached through the selected links and usable without domain/design reading.
- **O3 — Package-context discovery:** repeat a withheld-entry trial in a disposable registered package fixture under
  the Development payload's ignored probe root. Include a real fixture owner/reference with a symptom-specific
  ordinary link to its package-local operations entry. Use the existing namespace/search contracts; the reader
  begins at that owner/reference, not the entry path. Record fixture contents, context selection, exact path,
  links and evidence limitations in spec materials. No package content is added to this repository merely for a test.
- **O4 — Unique owners and maintenance:** review all substantive entry passages against capability, actual advisory,
  reference and executable guidance. A paper journal-compatibility change identifies operations discriminators
  and links to revisit; it leaves compatibility decisions, recovery steps and permissions with their owners.
  Inspect unknown/unmatched evidence and the not-ready drift branch. No real recovery is run to write docs.
- **O5 — Source/distribution and document checks:** verify generic guidance in an isolated consumer fixture through
  the docs bundle's existing instruction distribution; retain exact commands/output and opened link destinations.
  Run scoped rules and ordinary-link checks. Semantics/navigation are review-only, not claimed automated checks.

[direction.md](materials/direction.md) records baseline, options, incoming-reference coverage and support limits.
The baseline for O2/O3 is the Development head with the added ingress link withheld in a disposable fixture;
workers never check out another commit. Record before and after qualitative paths; claim no timing improvement.

### Effort and sequencing

Planning remains high as assigned. Development is medium: changes are reversible documents and one source guidance
asset, with mandatory independent code review and reconciliation under that effort. Independent O1–O5 reader
coverage remains required. No runtime is invented to match the earlier high effort hint.

The Host serializes future shared edits to the ownership capability, source `living-spec-writing.md` and transaction
capability with `SPEC-domain-model-documents`, refreshing the later worker against the landed content. Operations
adds its named section and selected ingress only; it does not overwrite the other proposal's role or link.

## 4. Lifecycle & Retirement Criteria

Foundation is completed at this worktree's base. This Planning turn leaves status reviewing; plan-accept and
proposal-handoff remain Host/user gates. Retirement requires useful maintained O1 composition, successful recorded
O2/O3 withheld-entry paths, O4 owner/maintenance review and O5 source/distribution verification. A new Kind or real
recovery execution is not a completion criterion. Lifecycle integration and viewer remain their existing proposals.

## 5. Open decisions and evidence limits

No goal/scope question requires a user answer in this turn. The concrete recommended direction awaits the existing
plan-accept gate; this is no acceptance. Operations discovery is unverified until O2/O3; pilot supplied-entry success
and Foundation design discovery do not prove it. No current production package operations scenario, exhaustive
historical-body audit, viewer support or recovery effect has been validated.
