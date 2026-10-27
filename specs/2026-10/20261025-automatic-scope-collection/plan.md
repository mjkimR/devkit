---
id: PLAN-automatic-scope-collection
spec: SPEC-automatic-scope-collection
---

# Technical Plan

## 1. Constitution & Invariant Review

ADR-host-owned-scope-observation replaces skill-maintained refresh. Preserve registry storage, ownership, capped
registered observation and post-finish cleanup. Application adapters expose a typed BaseUseCase; services import no
use cases. No new dependency or harness hook is needed.

## 2. Architecture Overview & Impact

A feature-owned source-reader contract has filesystem and pinned-tree adapters. Shared declaration parsing moves
below use cases. A bounded Git adapter constrains subprocess time/output. Inventory and observation services build
per-source scopes; the collector use case coordinates read-only registry access, explicit fetch, inventory,
collection, bounded comparison and result finalization. CLI renders results through the existing boundary.

## 3. Component & Interface Design

`scope collect --mode snapshot|refs|worktrees --base <ref> --fetch <remote> --timeout 30 --source-timeout 5`.
The use case receives root and typed collection options and returns a typed report with notices. Observation IDs
identify pairs; task keys distinguish actual identity from ref aliases. Output and limits follow
SPEC-automatic-scope-collection, including 8 MiB encoded output, 256 observations and partial coverage.

## 4. Storage & State Management

Collection reads namespace records with a shared lock and never reads owner tokens or updates journal/records.
No persistent collection cache. Only explicit fetch updates tracking refs. Existing creation registration remains
best effort with verbose-only automatic failure diagnostics. Filesystem declarations track fingerprints for reads.

## 5. Error Handling & Edge Cases

Collection warnings use SPEC_SCOPE_COLLECTION_PARTIAL; inability to read any inventory uses
SPEC_SCOPE_COLLECTION_FAILED. Bad arguments remain ARGUMENT_INVALID. Keep partial scopes, unknown activity and
missing layers explicit; do not certify independence. Preserve confirmed registered history caps and conservative
unregistered merge-base ranges. Limits apply during reads, comparison and result construction.

## 6. Verification & Test Plan

Run focused source/collector/CLI and automatic-registration tests, then `just lint-check spec`, `just check spec`,
`just test-affected --base main` and governance checks. Verify modes, dirty paths, refs, bases, limits, deadlines,
network opt-in and byte-for-byte registry immutability. Run independent code and reconcile reviews at medium.
Rebuild projections through `devkit sync` after source guidance changes. Reuse tests for unchanged verified content.
