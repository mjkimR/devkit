---
reconcile_id: REC-mcp-runtime-pending
status: pending
targets:
  - file: docs/capabilities/mcp/CAP-MCP-runtime-registration.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
---

# Reconciliation: `SPEC-mcp-runtime-pending`

`CAP-MCP-runtime-registration` removes the metadata-only missing-registration check, names the general-status
no-load/no-probe/no-write boundary and distinguishes explicit MCP status. Its actual-plan rule retains locked sync's
withheld-write notice, no-provider/None no-op and runtime-unavailable warning.
`CAP-DIST-sync-and-transactions` and the quick reference state the same notice boundary.
`ADR-remove-speculative-mcp-status-notice` already records the accepted direction and needs no consistency edit.
No architecture, state schema, runtime-provider or use-case step changes are introduced.

## Evidence and traceability

The baseline missing-registration test passed at accepted handoff head `5c8150d16a1a42b73036d99f93f9ff8ced9573b3`:
general status pending notices = 1, locked sync = 1. The delivered counterpart yields general status = 0 and locked
sync = 1. Eight status matrix cases assert no provider load/probe, registration plan/apply or ledger/destination
inspection. Twelve actual-plan/locked/registrations-only cases retain real outcomes. Existing host/gate/core status,
provider failure, explicit runtime command and ownership refusal tests pass in affected/dist-only verification.

`FB-mcp-registration-pending-ignores-runtime` is promoted and terminal; it remains unchanged.
No deferred item remains from the withdrawn observation design.

## Entrypoints

`devkit spec entrypoints derive` proposed the broad distribution/host source and test directories for both
capabilities. Reject those candidates: neither capability owns both complete feature trees and tests are not
entrypoints. Existing `sync.py` and `registrations.py` doorways already cover the changed behavior, so retain the
current entrypoint lists without additions.
