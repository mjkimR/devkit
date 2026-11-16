---
id: PROP-operations-documents
title: Operations and recovery documentation
summary: "Adds maintained operational guidance for diagnosis, recovery and upgrades with explicit boundaries against architecture, command references and executable playbooks."
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

Deployment structure, setup instructions and individual command references do not provide one maintained path
from an operational symptom to diagnosis, recovery and confirmation of normal operation. Historical incident
notes and command-level error actions cannot by themselves serve as current operational guidance.

## 2. Technical Spike Questions

- **Q1**: Which scope distinguishes operations from deployment architecture, use cases, developer guides,
  command references and executable playbooks? Which source owns a procedure when a playbook already exists?
- **Q2**: How should symptom, applicability, prerequisites, read-only diagnosis, recovery effects, stop conditions
  and success checks be represented without inventing new execution authority?
- **Q3**: What layout, identity and discovery convention make current procedures reachable in global/package
  namespaces? Is a new indexed kind needed, or can existing document facilities support the required navigation?

## 3. Proposed Design & Impact

- Apply `PROP-design-document-foundation`'s common ownership matrix. Define the operations home and representation
  in Planning; `docs/operations/` is a candidate, not an approved schema.
- Cover normal-state checks, diagnosis, recovery and upgrade guidance. Distinguish deployment topology from
  operator actions, and distinguish operational procedure from API/CLI reference and developer contribution flow.
- Make applicability, required state, diagnostic evidence, procedure ownership, effects and completion checks
  visible. Preserve existing authorization and secret-handling boundaries; a document is not permission to run it.
- When an executable playbook owns a procedure, link to it and explain applicability rather than duplicate its
  steps. Keep incident history and measurements in materials; keep current guidance up to date.
- Deliver templates, authoring conventions and the selected lookup/search/reference/validation support. Limit
  adapter and shared-model changes to this extension and declare required feature edges during Planning.
- Use interrupted synchronization or receipt mismatch as representative fixtures. Leave execution engines,
  cross-layer delivery workflow integration, viewer UI and repository migration to their existing owners or
  separate proposals.

### Expected acceptance evidence

- A representative fixture leads from symptom through read-only diagnosis to the appropriate recovery owner and
  an observable normal-state check. Unsupported or ambiguous states have a stop/escalation path.
- Architecture, reference, playbook and materials boundaries are explicit, with one authoritative procedure and
  no implicit authorization for recovery effects.
- Current operational documents are discoverable and their references resolve under the chosen representation
  in global and package namespaces, with focused tests for runtime behavior changes.

## 4. Lifecycle & Retirement Criteria

Start after the common ownership foundation is delivered. Planning settles the representation and procedure
boundaries; acceptance and handoff use the proposal gates. Retirement requires verified documentation support,
not execution of real recovery effects. Cross-layer reconciliation, viewer work and the pilot remain separate.
