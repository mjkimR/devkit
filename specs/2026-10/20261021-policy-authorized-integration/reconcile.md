---
reconcile_id: REC-policy-authorized-integration
feature: SPEC-policy-authorized-integration
status: resolved
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
---

Shared base policy authority, ask preservation, local-only effects, revocation and recovery are reflected in integration and delivery contracts and worktree guidance. The accepted successor `ADR-policy-authorized-local-integration` was promoted in the handoff and remains append-only. No new domain or architecture layer was introduced.

Source feedback `FB-auto-integration-dispatch` is terminal at promotion and needs no update. No agreed requirement is deferred. Entry-point review retains existing integration/service and delivery entrypoints; broad bundle/test candidates do not implement additional capabilities.
