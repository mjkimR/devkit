---
reconcile_id: REC-scope-registry-sandbox-access
status: resolved
targets:
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
    resolution: modified
---

# Reconciliation: `SPEC-scope-registry-sandbox-access`

`CAP-COLL-work-scope-registry` now distinguishes shared read-opened locks from exclusive mutation locks, limits
interrupted-file cleanup to mutation, documents side-effect-free token lookup, missing namespace/lock semantics,
unsafe-lock rejection, deadline preservation, separate history observations and explicit mutation permissions.
`scope/localfs.py`, `scope/location.py`, `scope/flow.py` and `cli/scope.py` implement these boundaries.

`CAP-DLV-project-policy` and architecture remain unchanged: there is no configuration, storage layout, transport,
core lock API, or host authorization change. The accepted ADR is retained unchanged. No new domain terms are added.

There are no explicitly linked source feedback items to resolve. The carried Planning feedback remains open.
The independently tracked `PROP-worker-shared-state-mcp` remains a draft outside this implementation; its existence
was verified. No required acceptance work is deferred there.

Entrypoint review retains the existing scope directory and CLI entrypoints, and the pre-existing cleanup entrypoint.
Tests support those implementations and are not added as capability implementation entrypoints.
