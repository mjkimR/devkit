---
reconcile_id: REC-worker-inspection-fixes
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Worker inspection reconciliation

`CAP-DLV-delivery-workflows` reflects absent optional reconciliation, required/malformed record diagnostics, independent cumulative rules_base, explicit --rules-base and labelled audit-base-fallback. Audit ancestry/changed paths and all existing stage requirements remain unchanged. The package README and delegated worker instructions agree with that contract. No use case, architecture, glossary or ADR contract changes: this fixes the inspector's existing cumulative governance promise and its partial-turn scope inference.

## Source feedback dispositions

- `FB-worker-inspect-partial-turn-scope`: resolved by `SPEC-worker-inspection-fixes`; permanent absent-reconcile pass/outside-scope failure tests and malformed-present/missing-tasks diagnostics pass.
- `FB-worker-inspect-scoped-reconcile-base`: resolved by `SPEC-worker-inspection-fixes`; an earlier-turn-created target passes actual RULE-reconcile-contract evaluation under cumulative rules base and fails under an explicit previous-turn rules base, while audit base and changed paths remain equal. CLI override, invalid ref and compact/full/text provenance tests pass.

## Verification

Baseline Red: 5 failed, 2 passed before production edits. Green: 48 worker inspector tests passed; affected suite 1445 passed; package lint and type checks passed. The actual reconcile-rule regression additionally confirms the originally failing comparison by explicit --rules-base previous while retaining the same audit range. Only `.devkit/installation.json` is a tracked sync output. Emulated role isolation uses absolute read scopes, explicit approvals, before/after alternate-index snapshots and actual diff review; no native confinement is claimed.
