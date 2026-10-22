---
reconcile_id: REC-shared-checkout-session-isolation
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
---

# Shared checkout guidance reconciliation

`CAP-DLV-project-policy` section 3 item 6 and `CAP-WT-task-worktrees` section 2a now explain shared branch
state and the coordination responsibility of the direct user and local orchestration Host. They preserve
optional worktrees for direct session tasks and required worktrees for local-orchestrated workers. The two
skill references state the same boundary beside session branch creation. Commands, output and integration
checks are unchanged; no new policy, runtime behavior, approval or ADR is introduced.

Entrypoint candidates from the two skill reference paths are wording-only associations, not new implementation
entrypoints for either capability; retain existing entrypoints. No new domain term or deferred work is introduced.
