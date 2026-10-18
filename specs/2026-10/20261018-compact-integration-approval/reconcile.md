---
reconcile_id: REC-compact-integration-approval
feature: SPEC-compact-integration-approval
status: pending
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
---

# Reconciliation: Compact native integration approval

`CAP-INT-mcp-services` defines concise views for prepare/integrate/status/resume, detailed status, the native effect
summary, retained internal validation and text/structured client compatibility. The integration quick reference mirrors it.
`CAP-HARN-agent-guidance` defines direct single native approval after verified reporting, optional prepare, status
inspection and approved resume. Source constitution, router, navigator, completion, worktree and integration skills agree.
The workflow's gate remains ask and is asserted only after actual native acceptance. No provider or execution policy changes.
No work is deferred. A running MCP server must reconnect to load the updated code/schema; SDK and installed-wheel smoke
verify the new implementation without claiming that the old running server has reloaded it.
