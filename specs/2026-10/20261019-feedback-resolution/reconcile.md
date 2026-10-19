---
reconcile_id: REC-feedback-resolution
feature: SPEC-feedback-resolution
status: pending
targets:
  - file: docs/decisions/2026-10/20261019-feedback-resolution-lifecycle.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
---

# Reconciliation: `SPEC-feedback-resolution`

## Contract reflection

- `ADR-feedback-resolution-lifecycle` defines the five states and task-authorized resolution without rewriting
  accepted storage/roadmap decisions. It extends the known preserved-materials states to include resolved.
- `CAP-HARN-agent-guidance` reflects source capture at entry, scope for delegated writes, separation from observation
  recording and hygiene, verified resolution, partial-work handling and independent integration authority.
- `CAP-DOCS-document-model` defines status semantics and preserves feedback discovery regardless of enclosing spec
  completion; explicit status filters separate resolved records from open ones.
- `CAP-DLV-delivery-workflows` places resolution in living-spec-draft/report-session, with no added session record,
  stage or gate, and retains the requirement when capture/sweep settings suppress new observations.
- `CAP-DLV-proposal-incubation` reflects resolved feedback preservation, source-reference carry for feature and
  bugfix specs, and no automatic resolution at handoff. Existing reference-rewrite/rollback behavior is unchanged.

## Source feedback disposition

The motivating `FB-padr-summary-length-unchecked` is resolved using the preexisting `SPEC-summary-length-guard`
implementation ec04a75 and its passing CLI/library 300/301-character and no-write regression cases. Its Disposition
records the evidence. This feature does not claim to implement that older fix or close other backlog feedback.

## Scope and deferred work

No required scope is deferred. No bulk migration of older promoted records is performed. No external submission,
new status-update command, migration path or workflow gate is added.

## Entrypoint review

Derived candidates were reviewed. Existing proposals/, skills/, playbooks/, templates/, workflows/ and subagents/
entrypoints already identify the owning implementations. No new pair is applied: the other joins are tests, the
installation receipt or code owned by a different capability, rather than implementation of each target contract.
