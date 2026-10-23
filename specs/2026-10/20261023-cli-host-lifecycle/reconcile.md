---
reconcile_id: REC-cli-host-lifecycle
status: resolved
targets:
  - file: docs/architecture/ARCH-04-2-delivery-policy.md
    resolution: modified
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/mcp/CAP-MCP-runtime-registration.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-delivery-decision-boundaries.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-local-and-pull-request-integration.md
    resolution: modified
  - file: docs/decisions/2026-10/20261023-host-cli-lifecycle-authority.md
    resolution: modified
  - file: docs/development/reference/host.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
  - file: docs/development/reference/worktree.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md
    resolution: modified
  - file: guides/install/mcp.md
    resolution: modified
---

The lifecycle capability contracts, use cases, approval policy, integration architecture, ADRs, references and MCP
consumer guide now describe Host conversational approval followed by source-bound CLI revalidation. The CLI retains
automatic authority only from the applicable retained-base policy, keeps local and pull-request routes distinct,
and directs recovery from observed Git and PR state. Lifecycle MCP registrations are removed while shared artifact
publication and transport remain. No deferred behavior remains in this scope.

Entrypoints were updated for the proposal lifecycle CLI and use cases, the integration CLI and use case, the policy
CLI, and worktree integration guidance. Candidates that were only tests, schemas, package configuration, or helper
directories were rejected as non-doorways. The existing bundle root remains the entrypoint for agent guidance;
architecture, ADRs, references and the install guide are not entrypoint-bearing documents.
