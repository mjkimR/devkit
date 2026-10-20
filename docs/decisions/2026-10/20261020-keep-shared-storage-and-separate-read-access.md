---
id: ADR-keep-shared-storage-and-separate-read-access
title: Keep shared storage and separate read access
summary: Retain Git common-directory storage and per-worktree ownership tokens. Make queries side-effect-free using an existing read-opened lock while keeping explicit authorization for mutations.
proposal: SPEC-scope-registry-sandbox-access
status: accepted
created_at: 2026-10-20
---

# [ADR-keep-shared-storage-and-separate-read-access] Keep shared storage and separate read access

- **Status**: Accepted
- **Date**: 2026-10-20

---

## 1. Context & Problem Statement

`CAP-COLL-work-scope-registry` shares state across linked worktrees using Git directories. Logical reads currently
create locks and clean record and token temporary files, forcing write access even when all records are readable.

## 2. Decision Drivers

Preserve discovery, ownership, revision checks and coherent concurrent reads; minimize permission requirements
without claiming that a location or transport bypasses host authorization.

## 3. Considered Options

Keep Git storage with scoped mutation approval; configure shared `.devkit/state/`; introduce a service-owned MCP
registry. The latter two require additional lifecycle and authorization design and do not inherently solve token
or cross-worktree access. See `docs/materials/2026-10/20261020-scope-registry-sandbox-access/access-comparison.md` for the comparison.

## 4. Decision Outcome

Recommend the existing backend with a read-only query path. Shared locks on an existing read-opened safe lock file
serialize record and history reads against exclusive writers. Query token lookup does no cleanup. Absent namespaces
return empty without creation; existing namespaces missing a lock fail visibly. Mutations retain their present
storage, ownership, cleanup and explicit permission requirements. No automatic fallback performs writes.

## 5. Consequences

An initialized readable registry can be queried without write access; hosts that deny read-open flock still return
an error. This is not a guarantee that all sandboxed hosts permit queries. A newly initializing namespace may yield
a retryable error until an authorized writer creates the lock. Development must verify lock compatibility on Linux
and macOS and query-wide absence of write calls. Relocation and MCP are rejected for this scope, not promised later.
