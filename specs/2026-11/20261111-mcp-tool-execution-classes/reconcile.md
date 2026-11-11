---
reconcile_id: REC-mcp-tool-execution-classes
status: resolved
targets:
  - file: docs/capabilities/mcp/CAP-MCP-runtime-registration.md
    resolution: modified
---

# Reconcile: `SPEC-mcp-tool-execution-classes`

`CAP-MCP-runtime-registration` is the only Living Spec document that names the execution classes. Its runtime
contract now names `read_only` and `bounded_write`, the `bounded_write` default and the read-only hint derived from
the class; the cloud paragraph no longer lists the removed preflight, approved-resume and interactive classes. The
shared artifact section already named only `bounded_write` and `read_only` and still holds, including "Unknown
execution classifications fail closed", which now covers the removed classes.

No other impact: `ARCH-05-2-components` says only that `devkit_core.base.mcp` owns explicit execution
classification, which still holds; no `docs/development/reference/` page names `McpTool` or a class; no use case
or glossary entry names the classes.

## Entrypoints

`devkit spec entrypoints derive` proposed `packages/devkit-dist/src/devkit_dist/features/shared/mcp.py` and the
`devkit-mcp` runtime test directory for `CAP-MCP-runtime-registration`. Both are rejected: the shared tool module is a
producer whose artifact behavior `CAP-COLL-shared-artifacts` owns, and tests are never doorways. The capability's
entrypoints are unchanged.

## Deferred work

`guides/install/mcp.md` still says cloud "refuses interactive/preflight/resume execution" (review-01 P3, waived in
reverify-01). `guides/` is outside this unit's write scope, so the one-line rewording (cloud exposes and runs only
`read_only` tools and refuses `bounded_write` execution, even through stale registrations) returns to the Host as a
follow-up.

## Source feedback

Finding SM-2 of the review-refactor code pass report is a material finding with no FB document; it is resolved by
this spec and needs no feedback record.
