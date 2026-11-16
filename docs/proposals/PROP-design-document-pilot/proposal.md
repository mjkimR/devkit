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

- Select small real examples for all three roles. Candidate domains are proposal/spec/milestone relationships
  and bundle/asset/projection relationships. Inspect synchronization for a design mechanism and an operational
  symptom; choose a better existing topic if its current owners already answer the question adequately.
- Prototype readable entry documents and only the supporting files the selected content needs. Keep drafts and
  comparison evidence in this proposal's materials or dated materials until the selected approach permits their
  promotion. Use existing representations; no new kind or runtime behavior is a prerequisite for this pilot.
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

### Expected acceptance evidence

- Small domain, design and operations examples each identify their purpose, existing sources and added value.
  A before/after ownership comparison identifies ambiguity, duplication and any proposed ownership transfer.
- Reader walkthroughs exercise all three entry paths without requiring the full document corpus. Failed paths
  identify a concrete missing behavior; successful existing paths justify leaving those facilities unchanged.
- A bounded change walkthrough identifies which owned statements need updating and which layers are unaffected.
  No implementation change is required to update every documentation layer.
- Evidence distinguishes verified facts, open questions and illustrative content. The result states the minimal
  support needed by foundation and later proposals and preserves source contracts and historical evidence.

## 4. Lifecycle & Retirement Criteria

Run this proposal first. Planning selects the real examples; acceptance and handoff use the proposal gates.
Retirement requires the content comparison and walkthrough evidence, not new document-system or viewer code.
Final runtime and viewer verification belongs to their respective proposals after representation decisions.
