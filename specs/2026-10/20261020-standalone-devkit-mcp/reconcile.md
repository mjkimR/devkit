---
reconcile_id: REC-standalone-devkit-mcp
feature: SPEC-standalone-devkit-mcp
status: resolved
targets:
  - file: docs/architecture/ARCH-08-1-agent-output.md
    resolution: modified
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-05-2-components.md
    resolution: modified
  - file: docs/architecture/ARCH-05-3-command-plugins.md
    resolution: modified
  - file: docs/architecture/ARCH-05-4-distribution-components.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/host/CAP-HOST-lifecycle-observation.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/development/reference/host.md
    resolution: modified
  - file: docs/capabilities/mcp/CAP-MCP-runtime-registration.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: waived
    rationale: "The reference already delegates native integration behavior to the updated capability and names no removed runtime command."
---

# Reconciliation

The runtime contract separates package/transport ownership, local project registration, explicit configuration
identity and execution constraints. Existing architecture, host, integration, delivery and worktree contracts
reflect those boundaries. No explicitly linked open direct-fix feedback source requires disposition.
Native terminal UI remains a separate unverified area; protocol/wheel tests do not establish host UI support.


The independent code review findings are resolved in reverify-01 and reverify-02. The reviewed implementation
keeps locked asset restoration separate from optional registration initialization and carries only a refusal
constraint across child processes. Native approval and terminal-removal exceptions remain invocation-local.
Entrypoint candidates were derived and reviewed; existing focused capability paths were retained, and the new
runtime capability names its runtime, dependency-free contracts, invocation constraints and registration provider.
Broad cross-capability package/test/tooling candidates were rejected. No accepted implementation requirement was
deferred; real-host UI evidence remains explicitly unverified under the accepted validation boundary.

The independent reconciliation recheck resolves both topology and confirmation-ownership findings.
`ARCH-08-1-agent-output` now names the standalone runtime command and links its runtime contract, following
Host authorization of this additional target. The native-protocol output exception is unchanged.
