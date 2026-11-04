---
reconcile_id: REC-post-merge-verification
status: pending
targets:
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/architecture/ARCH-06-runtime-view.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-cli-and-output.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md
    resolution: modified
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
    resolution: modified
---

# Reconciliation: post-merge verification

Integration capabilities now describe Git effects and pending final verification, while delivery, governance and harness documents assign branch checks and fresh landed-runtime checks to the Host. Proposal acceptance retains its eligibility and explicit authority and yields before handoff. Worktree finish remains a separate operation. Architecture reflects removal of the project readiness provider.

The adaptive-development capability is included because project-level readiness was removed for both adaptive-dev and SDD. Consumer installation and development quick references follow the same procedure. The accepted ADR and its four predecessor partial-supersession references were already committed in the accepted input and remain valid.

No required work or concrete deferred work is moved to a follow-up. CLI success does not enforce or prove external final checks. The Host must perform final target verification after integration.

Entrypoint candidates were derived and reviewed. Existing integration, delivery and proposal doorway entries remain accurate after removing the deleted readiness-provider entry. Broad cross-product directory, test, configuration and guide candidates were rejected because they do not provide document-specific code entrypoints.
