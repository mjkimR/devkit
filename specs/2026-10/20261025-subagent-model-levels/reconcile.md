---
reconcile_id: REC-subagent-model-levels
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-agent-projections.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-manifest-spec.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/decisions/2026-10/20261025-subagent-level-projection.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-orchestration-workers.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
  - file: docs/materials/2026-10/20261025-subagent-model-levels/configuration-design.md
    resolution: modified
---

# Reconcile: `SPEC-subagent-model-levels`

## Delivered behavior

Projection and sync contracts cover neutral levels, exact default mappings, shared schema/precedence/reset,
strict offline validation, native variants, dormant entries, status/dry-run and receipt behavior. Delivery
contracts and source roles inherit by default. The promoted ADR supersedes only the effort-preset alias of the
consolidated orchestration ADR. Glossary registers subagent model level separately from activity-effort.

## Verification and scope

AC-01 through AC-07 are implemented and tested. No new use-case flow or transport command is introduced;
existing capability interfaces describe the added configuration behavior. Native model execution/account access
remain explicitly unverified. No required work is deferred and no open source feedback is addressed by this unit.
Entrypoints retain existing inventory/config command entryways; the new pure resolver is an additional doorway
for model policy. Broad derived distribution/project/bundle directories and all test paths were rejected.
The exact resolver doorway was written directly because directory candidates fold narrower selectors
(the known FB-entrypoint-narrow-selector-folding limitation). Existing other entrypoints remain accurate.

The retained configuration material clarifies unusable installed discovery entries.
Observed workflow evidence friction is tracked independently in `FB-reverify-after-workflow-return`; no runtime
feature requirement is deferred to that feedback.
