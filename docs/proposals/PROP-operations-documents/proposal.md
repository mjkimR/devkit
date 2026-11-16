---
id: PROP-operations-documents
title: Operations and recovery documentation
summary: "Establishes symptom-led operational guidance that routes to existing recovery owners, adding document tooling only for gaps demonstrated by the early pilot."
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
  - docs/proposals/PROP-operations-documents/
  excludes:
  - packages/devkit-viewer/
  - packages/devkit-spec/
task_kind: feature
workflow: sdd-proposal
depends_on:
- PROP-design-document-foundation
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

- Apply the foundation matrix and early pilot. Retain the operations role; choose its home in Planning with
  `docs/operations/` as a candidate rather than a fixed kind or schema.
- Own symptom classification, diagnostic evidence, applicability, recovery-owner selection and confirmation of
  normal operation. Cover upgrade guidance where a real selected scenario needs it.
- Include capability recovery contracts and advisory actions in the ownership matrix. Keep command guarantees,
  compatibility conditions and error actions with their existing owners. Reuse executable instructions and
  playbooks by reference; do not maintain parallel recovery steps.
- If a procedure changes owner, explicitly retire its old authoritative copy or reduce it to a reference.
  Keep deployment topology in architecture, incident history in materials and CLI/API syntax in references.
- Use interrupted sync or receipt mismatch only where the early pilot shows added routing value over current
  status/recover guidance. Verify supported commands and avoid executing real recovery effects just to author docs.
- Deliver the authoring convention and smallest supported representation. Decide location, indexed kind/ID and
  tooling separately. Add lookup/search/reference, namespace or validation behavior only for demonstrated gaps;
  identify required feature edges and focus tests on runtime changes.
- Preserve existing execution permissions. Leave execution engines, general incident-management systems,
  cross-layer lifecycle integration and viewer work outside this proposal.

### Expected acceptance evidence

- The selected example adds a supported symptom-to-diagnosis-to-recovery-owner-to-normal-state path. It identifies
  the evidence selecting each branch and gives a stop/escalation route where current support is insufficient.
- Recovery guarantees and steps have one authoritative owner across capabilities, advisories, instructions,
  playbooks and references. A journal-compatibility change walkthrough identifies affected routing without
  duplicating the recovery contract in operations.
- Representation and discovery choices follow pilot evidence and work in global/package cases. Reused facilities
  count as support when the agreed path is demonstrated; new runtime behavior has focused tests.

## 4. Lifecycle & Retirement Criteria

Start after foundation. Planning settles representation and procedure ownership; acceptance and handoff use the
proposal gates. Retirement requires useful maintained operational guidance and verified entry paths, not a new
kind, executor or execution of recovery effects. Later integration checks use the retained operational example.
