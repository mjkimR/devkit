---
reconcile_id: REC-local-config-execution-environment
feature: SPEC-local-config-execution-environment
status: resolved
targets:
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-workspace-ownership.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
  - file: docs/architecture/ARCH-05-4-distribution-components.md
    resolution: modified
  - file: guides/INSTALL_GUIDE.md
    resolution: modified
---

# Reconciliation

`CAP-DIST-sync-and-transactions` defines the restricted overlay, provenance, explicit-root execution resolver,
environment transaction semantics, canonical/personal inventory separation and evidence lifecycle (AC-01–03,
AC-05–06). `CAP-DIST-workspace-ownership` defines ignored local-file ownership and transient evidence.
`CAP-DIST-context-and-playbooks` describes validated runtime reads and effective search preferences.
`CAP-WT-task-worktrees` records creation-time byte/mode copying before setup/sync, explicit copy failure,
checkout retention and independence of existing checkouts (AC-04). The architecture assigns each responsibility
to the shared core, distribution or worktree layer; the reference and installation guide expose the commands
and error remediation. The distribution consumption instruction mirrors these contracts in its source bundle.

The accepted ADR remains unchanged. Snapshot policy and rules retain shared readers and canonical receipts;
the focused snapshot regression proves local settings do not change governance authority. No story contract or
new domain term is introduced. No implementation requirement is deferred or waived.

The source observation `FB-planning-context-command-can-trigger-unavailable-sync` remains an open follow-up,
not a linked direct fix. The observed root-policy discrepancy is separately recorded as
`FB-local-worktree-copy-premise-root-policy`; creation copying supports a corresponding relative project path,
while the existing CLI prohibition on nested Git project roots remains intact. No source feedback requires an
out-of-boundary resolution.

Entrypoint derivation uses the actual source files within the assigned task boundaries. Distribution sync
entrypoints select local configuration, render evidence and sync; context selects the synchronized reader and
status; workspace ownership selects transaction path safety. The worktree lifecycle entrypoint already exists.
Test directories, unrelated source files and the guide hub are rejected as entrypoints for these capabilities.
