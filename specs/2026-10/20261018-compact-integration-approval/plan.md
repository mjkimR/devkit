---
id: PLAN-compact-integration-approval
spec: SPEC-compact-integration-approval
---

# Plan: Compact native integration approval

## 1. Invariant Review

Preserve `CAP-INT-mcp-services` authorization and local-only execution. Full immutable requests and digests remain
server-side, including filesystem identities, policies, evidence, registrations and cleanup revisions. This clarifies
`ADR-integration-approval-asserted`: native approval is the local ask decision, not a second business gate.

## 2. Components and Interfaces

Add an explicit request approval-scope projection and compact result projection. Preserve the existing full library
serialization for CLI and detailed inspection. All four MCP handlers use the compact projection; only status accepts
optional detail=false. The form renders a concise effect scope from the same immutable request that is approved.
Prepare remains available for diagnostics, but integrate already prepares and is the default entry point. Resume
retains its request-id-only authority and validation. The MCP transport keeps identical text/structured JSON encodings
for compatibility, using the reduced result. No new dependencies or runtime authority parameters are introduced.

Update source spec constitution, router, completion/worktree/integration guidance and Living Spec contracts together.
No API changes to providers. Detailed status stays read-only and does not grant authority.

## 3. Verification

Real SDK conversations cover all four tools, text/structured agreement, form contents, compact vs detailed status,
partial resume and rejected caller authority. Existing service tests cover stale scope, denied approval and permission
failure. Run devkit and spec lint/type checks, focused integration/host/spec tests, governance, builds and consumer smoke.
Independent code and reconcile reviews run at high effort. Recheck after fixes. Native installed-host validation remains
separate from SDK coverage; the connected server may need restart to load new code.
