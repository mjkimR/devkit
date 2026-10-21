---
id: ADR-separate-shared-artifacts-from-scope
title: Separate immutable shared artifacts from scope coordination
summary: Keep authoritative scope coordination in its existing registry and introduce bounded immutable expiring artifacts with equivalent CLI and optional local MCP operations.
proposal: SPEC-worker-shared-state-mcp
status: accepted
created_at: 2026-10-21
---

# [ADR-separate-shared-artifacts-from-scope] Separate immutable shared artifacts from scope coordination

- **Status**: Accepted
- **Date**: 2026-10-21

---

## 1. Context & Problem Statement

`CAP-COLL-work-scope-registry` records authoritative owner tokens and optimistic revisions, while proposal review
reports are regenerable presentation artifacts. Applying TTL and generic CRUD to both would violate the registry's
non-expiring storage and read-only query contract in `ADR-keep-shared-storage-and-separate-read-access`.

## 2. Decision Drivers

Bounded report sharing across linked worktrees; immutable commit binding; no new approval authority; SDD-agnostic
package ownership; independent CLI access; optional retained local MCP transport; read-only viewers and queries.

## 3. Considered Options

- A common mutable record/artifact backend couples unrelated authority and expiry semantics and is rejected.
- Immutable local artifacts with an adapter seam meet the immediate report consumer and are selected.
- A production remote artifact adapter is viable but requires a provider/authentication/deployment decision before
  implementation. It is deferred to the follow-up tracked by `FB-remote-shared-adapter-follow-up`.

## 4. Decision Outcome

Select `devkit.shared` in devkit-dist for immutable content-addressed artifacts, separate from existing scope
records. Equivalent CLI and optional MCP methods share validation, bounded payloads, expiry, locking and errors.
Read/list never sweep; MCP sweep-plan and sweep-apply are separate tools. Identical live content is idempotent,
while expiration permits a fresh generation with a new URI and never revives the old URI. Local bounded-write MCP calls do not elicit forms and remain prohibited in cloud mode.
The proposal defines concrete keys, metadata, seven-day logical expiry, exclusion checks and acceptance fixtures.

## 5. Consequences

Consumers must retain exact artifact references and verify source commits; artifact existence never approves work.
Two reports for one commit may coexist. Filesystem sharing trusts the same OS user and the retained MCP process,
not forged caller identity. First delivery publishes the remote-adapter protocol and registration contract but
cannot claim production cross-host support. A concrete backend restarts in a separate proposal once its consumer,
provider/authentication, namespace owner and integration environment are known. `SPEC-cloud-agent-rendering` owns
cloud-specific asset rendering; local orchestration still checks MCP connection before dependent operations. Scope-registry ownership and revision behavior require no migration.
