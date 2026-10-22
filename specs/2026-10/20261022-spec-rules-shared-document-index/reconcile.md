---
reconcile_id: REC-spec-rules-shared-document-index
status: resolved
targets:
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rule-authoring.md
    resolution: modified
---

# Living Specification Reconciliation: `SPEC-spec-rules-shared-document-index`

## 1. Reconciled Contracts

- `docs/capabilities/governance/CAP-GOV-rules-engine.md`: Documented the `get_or_compute` run-scoped in-memory cache slot on `WorkspaceCache` in section 1 (Principles: Session caching) and subsystem layout.
- `docs/capabilities/governance/CAP-GOV-spec-rules.md`: Documented in section 3.2 (Shared Behavior) that the document index is loaded once on first access and cached in memory across rules via `ctx.cache.get_or_compute`.
- `docs/capabilities/governance/CAP-GOV-rule-authoring.md`: Documented `ctx.cache.get_or_compute(key, factory)` in section 2 as an accessor available to custom rules for sharing run-scoped computations.

## 2. Deferred Work & Source Feedback

None.
