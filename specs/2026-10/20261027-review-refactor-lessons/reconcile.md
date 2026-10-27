---
reconcile_id: REC-review-refactor-lessons
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-review-refactor.md
    resolution: modified
  - file: docs/usecases/governance/UC-review-and-refactor-accumulated-slop.md
    resolution: modified
  - file: docs/decisions/2026-10/20261027-apply-review-refactor-changes-in-parallel-checkouts.md
    resolution: modified
  - file: docs/decisions/2026-10/20261026-apply-behavior-preserving-batches-as-direct-mode-refactors.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/architecture/ARCH-04-delivery-strategy.md
    resolution: modified
---

# Reconcile: review-refactor lessons

- `CAP-DLV-review-refactor` states the change contract (parallel application, sequential fallback, no governance
  relaxation, differential comparison, divergence list, removal sweep, reviewer brief) and the report interface
  (behavior changes, outcome after integration); `UC-review-and-refactor-accumulated-slop` carries the steps,
  extensions and scenarios.
- `ADR-apply-review-refactor-changes-in-parallel-checkouts` supersedes
  `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors` (status and pointer only on the old one);
  `CAP-DLV-delivery-workflows` and `ARCH-04-delivery-strategy` cite the new ID.
- Not changed: the release handbook (`ADR-handbook-on-request-release-snapshot`, refreshed at the next release) and
  the accepted ADR body of `ADR-apply-approved-contract-removals-as-separate-work-items` (history).
- Entrypoints: the capability's entrypoint (the playbook's `SKILL.md`) is unchanged.
- Deferred: the separate performance playbook continues as `PROP-performance-pass`.
