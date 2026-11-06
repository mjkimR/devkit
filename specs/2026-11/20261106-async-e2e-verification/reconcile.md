---
reconcile_id: REC-async-e2e-verification
status: resolved
targets:
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-isolated-execution.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/decisions/2026-11/20261106-isolated-test-runs.md
    resolution: modified
  - file: docs/development/reference/exec.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/usecases/harness/UC-execute-an-isolated-command.md
    resolution: modified
---

# Reconciliation

The isolated-execution capability and use case retain fixed-commit preparation, native argv, captured runtime, bounded evidence, observation, confirmed cancellation, positive terminal ownership proof and durable guarded cleanup. The worktree contract owns detached creation/removal and interrupted-removal retry. The architecture and promoted ADR retain only the approved worktree/project edges and preserve synchronous compact execution.

Delivery and agent guidance require actual command/coverage discovery before choosing independent verification groups; unseparated or unclear consumers retain existing synchronous requirements. Devkit's tier-aware selector is its adoption example. Background result collection, exact tested SHA, accumulated intervals and repair priority remain Host duties; no E2E-existence guarantee, profile mapping, consumer completion selector, mandatory verifier subagent or git-operator supervision is introduced.

AC-01 is reflected in the delivery guidance and repository selector reference. AC-02/05/06/10/15 are reflected in delivery/guidance and its use case. AC-03/04/07/08/09/11/12/13/14 are reflected in isolated execution, worktrees and the execution reference; verification.md retains measurements and platform limits. Existing glossary terms suffice; no term is renamed.

## Deferred work

PROP-test-playbook-verification-policy remains a draft depending on SPEC-async-e2e-verification. It owns the test-management playbook assessment and recommended client local/cloud operating examples, including accepted nightly detection of broken combined cloud main. It also assesses command separability, overlap and synchronous fallback. Restart after this execution capability and devkit adoption land with required final checks. No playbook or client CI implementation is included here.

## Entrypoints

Entrypoint candidates were derived and reviewed; only the execution-only worktree API and isolated-verification guide were appended where owned. Preserve existing narrow doorways and add only isolated_execution CLI/use cases and the execution-only worktree API where owned. Drop test paths, helpers, broad shared roots and AGENTS/README hubs.

Independent high reconcile round 1 covered all nine targets. Its two document findings were corrected with the exact proposed wording; reconcile-check-02 closes the round under minor-fix self-verification. No required contract mismatch is waived.
