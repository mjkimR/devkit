---
id: ADR-local-immutable-proposal-review-view
title: Local immutable proposal review view
summary: "Permit exact local shared proposal-report reads while retaining Git-only ordinary viewer endpoints and all read-only protections."
status: accepted
created_at: 2026-10-21
supersedes: ADR-read-only-local-server-over-git-refs
---

# [ADR-local-immutable-proposal-review-view] Local immutable proposal review view

## Context

`ADR-source-bound-review-reports-and-explicit-lifecycle-approval` requires an optional readable view of immutable,
expiring reports without committing translations. The original viewer Git-only restriction excludes these records.

## Decision

Supersede only the all-reads-through-Git restriction of `ADR-read-only-local-server-over-git-refs`. Permit an exact
generation route for proposal-review artifacts through each registered repository's configured local shared adapter.
Ordinary Git routes retain their original ref/path rules. No remote adapter, arbitrary path, write, regeneration,
sweep, approval or automatic server start is added. Preserve loopback binding, Host checks, no CORS and GET-only.
Render escaped Markdown source with source SHA, language and expiry; no report HTML or script executes.

## Consequences

The viewer imports the shared local read contract in addition to core/advisory. Reading never extends TTL and
expired reports require Host publication. Rendering is deliberately a readable source view; host-specific links
and native form presentation require separate observation.
