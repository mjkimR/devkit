---
id: PLAN-worker-shared-state-mcp
spec: SPEC-worker-shared-state-mcp
---

# Technical Plan: `SPEC-worker-shared-state-mcp`

## Constitution and Invariant Review

No new conflict. `ADR-separate-shared-artifacts-from-scope` authorizes the new domain; scope coordination remains unchanged. The current base retains the classifier, workspace configuration and lock interfaces described in the accepted evidence.

## Architecture and Interfaces

Implement `devkit.shared` in devkit-dist with core/advisory-only imports. Frozen public input/result types and a runtime-checkable adapter protocol define immutable put, exact get, filtered list and bounded sweep. Entry-point factories receive repository context; the built-in local adapter is reserved. CLI and MCP call the same service validation. No new dependency is needed.

Local discovery uses Git's registered main worktree and canonical common directory, validating identity and path types. Common exclusion locking uses the existing registration lock name to serialize narrow exclusion installation. The namespace derives from the common directory, keeping independent clones isolated. Use POSIX no-follow opens, a stable read-only shared lock for reads, exclusive writes, canonical JSON metadata as YAML-compatible frontmatter and an atomic same-directory envelope rename. Seven-day expiry is computed by an injectable UTC clock. Operations use a ten-second monotonic deadline.

Add shared.adapter to effective local configuration, then apply DEVKIT_SHARED_ADAPTER. MCP resolves its configuration workspace rather than executor preferences. Add bounded_write to fixed service classification, preserve cloud refusal and fail-closed class validation. Source guidance checks connected local project tools before shared operations.

## Failure Handling

Explicit SHARED codes cover invalid input/envelopes, unavailable workspace/adapter, exclusion conflict, missing/expired artifacts, denied access and timeout. Invalid sweep candidates remain in place. Publication commits a single envelope; retry resolves the live content key, while expired keys receive a new generation. No cleanup or root switching occurs on reads or permission refusal.

## Verification

AC-01/02: real temporary Git main/linked/clone discovery, CLI/MCP parity and exclusions, including foreign and symlink fixtures. AC-03/04: concurrent publication, injected publication failures, expiry clocks, read permissions, stable metadata and registry byte snapshots. AC-05: common validation/error cases, cloud discovery/forged calls and no-form local writes. AC-06: configuration precedence and public factory registration plus reusable conformance fixtures with a test adapter.

Run focused tests, affected-package lint/type checks, just test-affected with its full fallback, just test-dist and governance checks. Independent code and reconcile reviewers verify cross-component scope at medium effort.

## Implementation decisions

First-write safety requires the shared directory itself to stay excluded, not one probe filename. Applicable
ancestor ignore negations are checked before infrastructure effects, because Git's check-ignore can omit an
ancestor negation for an absent descendant. Matching is conservative for case-folded paths, recursive globs and bracket expressions (including Git POSIX classes); an exclusion conflict
requires policy inspection, never automatic ignore rewriting. All writer initialization decisions serialize
under the existing common exclusion lock, preserving fail-closed missing-lock handling after interrupted setup.

Host-authorized narrow boundary extensions add the glossary term and distribution's shared schema/default
template. Registered adapter method binding and operation-result validation fail explicitly before consumers
can mistake malformed responses for artifacts.

Registered backend AdvisoryErrors retain their codes; only invocation/result contract violations map to adapter
unavailability. Continuation tokens stay opaque at the shared boundary; only the local backend decodes its own
filename tokens. The built-in shared template precedes installed harness tables to preserve their tool adjacency.
