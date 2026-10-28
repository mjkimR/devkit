---
id: ADR-remove-speculative-mcp-status-notice
title: Remove speculative MCP registration notices from general status
summary: "For provider-free general status, we remove speculative MCP registration pending notices and retain diagnostics from actual registration plans, to avoid ungrounded retry advice, accepting explicit MCP commands for registration diagnosis."
proposal: SPEC-mcp-runtime-pending
status: accepted
created_at: 2026-10-28
---

# [ADR-remove-speculative-mcp-status-notice] Remove speculative MCP registration notices from general status

## 1. Context & Problem Statement

Provider metadata cannot establish an actionable registration: the provider can find no retained runtime or return
`None`. General status deliberately does not load that provider. Its inferred pending notice can recommend an
unhelpful retry. `CAP-MCP-runtime-registration` and `CAP-DIST-sync-and-transactions` currently promise that inference.

## 2. Decision Drivers

- Keep general status provider-free and free of speculative registration advice.
- Preserve diagnostics produced by actual registration planning.
- Introduce no runtime observation or substitute readiness mechanism.

## 3. Considered Options

- Keep the metadata inference: retains the unsupported assumption that provider presence implies desired work.
- Add runtime observation or probing: introduces a mechanism the settled scope excludes.
- Remove the general-status notice: keeps diagnosis in explicit registration operations and simplifies status.

## 4. Decision Outcome

Remove `MCP_REGISTRATION_PENDING` from general `devkit status`. Preserve locked sync's notice when an actual
registration plan has a host state of `write` whose write is withheld. Preserve explicit MCP commands, runtime
selection and provider failure behavior. This revises only the general-status notification clauses of the named
capabilities; the provider boundary from `ADR-mcp-runtime-and-shared-artifacts` remains.

## 5. Consequences

A real missing registration no longer prompts through general status. Explicit MCP/sync commands remain the
route for registration diagnosis and reconciliation. No cache, TTL, fingerprint, persistence schema or active-only
check replaces the removed inference.

## 6. Confirmation

AC-1 through AC-5 in `SPEC-mcp-runtime-pending` require a provider-result matrix, no-load/no-probe assertions,
locked-sync notice preservation, independent status diagnostics and consistent Living Spec wording.
