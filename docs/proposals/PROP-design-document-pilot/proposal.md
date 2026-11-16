---
id: PROP-design-document-pilot
title: Early content pilot for domain, design and operations
summary: "Tests domain, design and operations ownership on small real devkit examples before selecting new document identities or implementing tooling."
status: reviewing
created_at: 2026-11-16
target_area: documents/
priority: high
size: M
planning_effort: medium
dev_effort: medium
milestone: MS-documentation-system-evolution
boundaries:
  owns:
  - docs/proposals/PROP-design-document-pilot/
  - docs/materials/
  excludes:
  - packages/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-design-document-pilot] Early content pilot for domain, design and operations

## 1. Background & Hypothesis

Domain models, implementation designs and operations guidance are retained documentation roles. Their usefulness
and boundaries should be tested with real content before committing to new indexed kinds or dedicated tooling.
This early pilot supplies evidence for `PROP-design-document-foundation`; it does not wait for runtime or viewer work.

## 2. Technical Spike Questions

- **Q1**: Which existing content demonstrates a distinct contribution from each role, and which passages already
  have a suitable authoritative home in capability, architecture, reference or executable guidance?
- **Q2**: Can a reader follow concept-to-contract, contract-to-design-to-detail, and symptom-to-recovery-owner
  paths using existing entry documents, links and discovery facilities?
- **Q3**: Which concrete failures require a new identity, relation, search behavior, artifact handler or UI?

## 3. Proposed Design & Impact

- Use one bounded distribution slice for all three roles. Domain explains bundle availability, selection,
  projected asset paths and the installation receipt. Design explains journaled file-to-directory and
  directory-to-file replacement. Operations starts from `TRANSACTION_PENDING` and distinguishes the
  `RECOVERY_BLOCKED` branch. The selected sources and evidence protocol are in
  [example selection](materials/example-selection.md).
- Keep the pilot to one entry draft per role and one design detail draft. Supporting artifacts are source links
  unless the chosen mechanism requires an authored diagram. Drafts are evaluation content, not current contracts.
  Existing support may be the final recommendation for any of the three representation decisions.
- Prototype readable entry documents and only the supporting files the selected content needs. Keep drafts and
  comparison evidence in this proposal's materials or dated materials until the selected approach permits their
  promotion. Use existing representations; no new kind or runtime behavior is a prerequisite for this pilot.
- Keep reference paths specific to the reader question. Each entry explains its overview and next step without
  prerequisite reading of whole documentation layers. Domain links necessary contracts; design links needed
  capability, architecture and detail; operations links the selected diagnosis or recovery owner. Concise
  non-normative summaries may orient the reader while the exact normative statement keeps one owner.
  Use existing reverse-reference tools where sufficient; require no all-pairs graph or manual reciprocal links.
- Compare the prototypes against the existing architecture, glossary, capability, reference and procedure views.
  Account for each statement's authoritative source. Do not duplicate a rule merely by labeling it conceptual.
- For domain content, first compose existing conceptual meaning and cite validity and transformation contracts.
  If moving an invariant is useful, demonstrate how the old authoritative statement becomes a reference.
- For operations, add symptom classification, diagnostic evidence, selection of the existing recovery owner and
  a normal-state check. Include capability recovery contracts and advisory actions among the existing owners;
  reuse their instructions instead of inventing parallel recovery steps.
- For design, separate cohesive implementation mechanisms from observable guarantees. Demonstrate how an entry
  document reaches independently readable details and actual supporting artifacts where available. An illustrative
  datasheet may test a format, but is not evidence of real maintenance demand and is not mandatory pilot content.
- Capture useful reference principles: overview-to-detail navigation, caller/callee boundary links, evidence for
  uncertain claims and change-specific updates. Reuse existing metadata and reconciliation rather than add a
  parallel registry, approval system or completeness-by-line-count metric.
- Record three independent representation decisions for each role: content location, indexed kind/ID, and tooling/UI.
  Name evidence for every proposed extension and the existing support that already works. Missing evidence may
  defer an extension; it does not remove the agreed documentation role.

### Planning decisions and excluded scope

- The Host's user decisions retain domain, design and operations as three roles. Architecture explains system
  scope, building blocks, runtime interactions and cross-cutting structure within the whole documentation system;
  detailed implementation explanations link back to it. Existing arc42 quality and risk ownership stays there.
  The pilot does not teach arc42 or introduce a fourth role.
- Start with composed views and source links. No normative ownership transfer is selected for this pilot.
  A proposed transfer requires explicit source-statement identification, retirement of the old normative copy
  and separate scope authority before editing that owner.
- Content home, indexed kind/ID and runtime/UI remain independent decisions for foundation Planning. This pilot
  recommends each from observed reader outcomes; it neither registers kinds nor builds final documentation homes.
- No code, template, rule, authoring instruction, viewer, package, executable recovery or feature-edge change is
  included. No recovery command is run against this repository. Recovery walkthroughs use documented states.
- Pilot deliverables and deferred targets are listed in `PROP-design-document-pilot-target`. Development remains
  `medium`: document evidence and independent review suffice; production tests and benchmarks are irrelevant.

### Expected acceptance evidence

- **AC-PILOT-01**: Small domain, design and operations examples each identify their purpose, existing sources and added value.
  A before/after ownership comparison identifies ambiguity and duplication, with no ownership transfer selected.
- **AC-PILOT-02**: Reader walkthroughs exercise all three entry paths without requiring the full document corpus. Failed paths
  identify a concrete missing behavior; successful existing paths justify leaving those facilities unchanged.
  Contract-only design discovery and supplied-entry navigation have separate results. Operations includes the
  existing readiness owner and a no-journal state with desired-state drift that remains not ready.
  Each trial reports unnecessary round trips, prerequisite reading and whether the entry explains the next step.
  Link connectivity alone does not establish a useful path; no fixed hop cap is imposed.
- **AC-PILOT-03**: A bounded change walkthrough identifies which owned statements need updating and which layers are unaffected.
  No implementation change is required to update every documentation layer.
- **AC-PILOT-04**: Evidence distinguishes verified facts, open questions and illustrative content. The result states the minimal
  support needed by foundation and later proposals and preserves source contracts and historical evidence.

## 4. Lifecycle & Retirement Criteria

Run this proposal first. Planning selects the real examples; acceptance and handoff use the proposal gates.
Retirement requires the content comparison and walkthrough evidence, not new document-system or viewer code.
Final runtime and viewer verification belongs to their respective proposals after representation decisions.
The evidence package can conclude that current facilities suffice. A failed navigation attempt is a finding to
classify, not automatic authority to add runtime support. Foundation consumes recommendations with their source
revision, limitations and retained example links.
