---
reconcile_id: REC-periodic-drift-reconciliation
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-drift-reconciliation.md
    resolution: modified
  - file: docs/stories/governance/US-keep-the-living-spec-consistent.md
    resolution: modified
---

# Reconciliation

The distribution contract records opt-in maintenance and exact delivered preset membership. The new delivery
capability owns bounded review, evidence gaps, explicit dispositions, repeatability and report completion.
The workflow document links per-feature reconciliation to this independent sweep without adding a stage.
Traceability records navigation-only use; the governance story adds semantic review and user arbitration,
linked both ways. The parent ADR is unchanged. No new domain term or architecture invariant is introduced.

Catalog README and installation recommendations mirror selection and invocation. The Host-authorized expansion
in scripts/smoke.sh updates only the catalog bundle-name expectation required by the new registration.

## Entrypoint review

Keep the maintenance module on the content-packages contract and the exact playbook on the new capability.
Reject broad catalog, guides and smoke candidates for workflow/traceability/story wording-only changes;
these documents do not own catalog implementation. No unrelated entrypoint changes.

## Source feedback and retained follow-up

`FB-nested-role-skill-read-scope` is an imported observation, outside direct-fix scope. It stays open; Host owns
any separate disposition. No direct-fix source was completed by this unit.
Review-refactor companion delivery is retained in `FB-maintenance-companion-playbooks`; it is not acceptance work for this unit.
Weekly-report is retained in `PROP-weekly-report`, under `MS-reporting-and-actionable-insights`.
After the Host base refresh, local ID resolution and proposal sections 1 and 3 verify that it identifies this
maintenance delivery as its source, independently adds weekly-report/reporting and preserves upkeep.
This existing destination owns its separately approved Planning; no duplicate feedback or implementation is created.
Host authorized the one-line source-link repair in that proposal from the retired proposal ID to this SPEC ID.
No scheduler or rejected detector is reopened.
