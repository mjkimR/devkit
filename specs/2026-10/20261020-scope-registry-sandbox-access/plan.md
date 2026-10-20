---
id: PLAN-scope-registry-sandbox-access
spec: SPEC-scope-registry-sandbox-access
---

# Technical Plan: `SPEC-scope-registry-sandbox-access`

## 1. Constitution & Invariant Review

None. Follow `ADR-keep-shared-storage-and-separate-read-access` and reconcile
`CAP-COLL-work-scope-registry`. No core lock, configuration, storage layout or mutation authorization change.

## 2. Components and Interfaces

- `scope/localfs.py`: separate read context from the mutation context. Stat the namespace, treating only ENOENT as
  absent; open the existing lock with O_RDONLY, O_NOFOLLOW and O_NONBLOCK, validate the descriptor as regular, and
  poll shared flock with the same deadline and interval as writers. Always close descriptors on failures. Keep the
  shared lock held across the complete record scan or journal read. No cleanup in this context.
- `scope/location.py`, `scope/flow.py`, `cli/scope.py`: add explicit cleanup control with mutation-preserving
  defaults; query ownership lookup disables token cleanup.
- `scope/` tests: syscall guards, namespace and unsafe-lock errors, process synchronization, CLI ownership/history,
  identity and existing mutation regression coverage.

## 3. Failure Modes and State

No migration or schema changes. Existing namespaces without a lock fail visibly until authorized registration
without a token initializes it, or an operator repairs the missing lock with writers quiescent. Release/sweep are
not missing-lock recovery. Never unlink or replace an existing active lock. Permission failures propagate through
existing advisory errors. Per-record parse/permission warnings remain separate from namespace failure.

## 4. Verification

Run scope tests, lint/type checks, `just test-affected`, and governance checks. Verify AC-01/02 through syscall
instrumentation and before/after snapshots; AC-03 with process barriers and bounded waits; AC-04 with existing
ownership, optimistic revision, interruption and sweep tests plus linked-worktree identity fixtures. AC-05 requires
macOS execution and a local Linux container (no network), then actual unelevated CLI queries against the initialized
worktree registry. Record commands and evidence in the allowed materials directory. Required unavailable execution
is a blocker, never waived. Independent medium code review and reconcile verification follow implementation.
