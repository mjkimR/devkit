---
reconcile_id: REC-mcp-delivery-decisions
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/development/reference/host.md
    resolution: modified
---

# Reconciliation

The local MCP path replaces external-runner user interaction for accepted proposal handoff. AutoHub is an
alternative host and receives no changes. The service returns confirmed effort as run input, preserving the
worker envelope as its authoritative record and final integration as a separate approval. Integration displays
committed presentation evidence while retaining exact scope and existing authority checks. Host transport
preserves the tool's external-operation annotation because configured worktree setup may install dependencies.

No new architecture dependency or change to the read-only viewer is required. Consumer guidance is mirrored in
the spec bundle's worktree and effort references and synchronized through the deployment receipt.
