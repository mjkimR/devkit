---
reconcile_id: REC-maintenance-history
status: pending
targets:
  - file: docs/architecture/ARCH-05-3-command-plugins.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-maintenance-history.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-weekly-report.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-review-refactor.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-performance-pass.md
    resolution: modified
  - file: docs/usecases/governance/UC-record-a-maintenance-run.md
    resolution: modified
  - file: docs/usecases/governance/UC-find-the-latest-maintenance-run.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
  - file: docs/development/reference/maintenance-history.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-history-branch-publication.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-inspected-state-identity.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-opt-in-maintenance-history.md
    resolution: modified
---

# Reconciliation: `SPEC-maintenance-history`

The standalone feature contract and explicit composition boundary are reflected against implementation. The capability/use cases remain draft/proposed until focused review and reconciliation complete. AC-10 passes without waiving a criterion. The two promoted decisions retain their root/publication/identity decisions; only the authorized per-run applicability trace changes.

The labelled live exercise passes with sanitized evidence in the preserved materials. A repository endpoint defect was reproduced and fixed before success. The refined opt-in composition and live confirmations await focused independent review/reconciliation before canonical activation and completion.

The user-refined composition boundary is `ADR-opt-in-maintenance-history`: standalone history remains available only on explicit request. The four default catalog playbooks are restored to their pre-feature procedures. Installing commands does not add history probes, lifecycle actions, offers or completion prerequisites. The old publication ADR gains only the authorized partial-supersession applicability trace.
