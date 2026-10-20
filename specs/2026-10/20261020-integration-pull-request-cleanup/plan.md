---
id: PLAN-integration-pull-request-cleanup
spec: SPEC-integration-pull-request-cleanup
---

# Technical Plan: `SPEC-integration-pull-request-cleanup`

## Constitution & Invariant Review

The two accepted ADRs authorize remote operations only on the confirmed PR route. Preserve worktree-to-core layering,
local-only cleanup extensions and process-local approval authority. No new dependencies.

## Components and interfaces

- `devkit.worktree` owns an injectable GitHub port, bounded gh/Git calls, repository identity, policy and PR observations.
- `devkit.integration` adds route selection, immutable remote scope, PR execution/resume and landing evidence alongside
  the existing local executor. Reuse merge construction, guards, receipts, provider checks and cleanup validation.
- `devkit_spec.integration` declares the landed-target check in readiness evidence.
- MCP prepare/integrate select `local|pull-request`, default local. Network-reaching tools declare open-world behavior.
- Approval remains process-local. Results retain PR identity, step state, build target/tree and landing evidence.

## Failure handling

Fail before remote writes for unsupported identity/policy. Mutation timeouts are unknown until remote observation
confirms their outcome. Pending checks release the lock; resumes cannot absorb target advances. Cleanup rechecks source
ancestry and preserves local dirt/divergence. Never force a push except the explicitly approved deletion lease.

## Verification

Use offline injected ports and bare repositories for acceptance scenarios, including every unchecked-landing reason,
source loss, pending/restart, failed checks, unknown mutations and cleanup interruption. Run lint/type checks, affected
tests and governance checks. High-effort independent code review and reconcile verification precede the final report.
Official GitHub documentation is evidence for platform contracts; no live remote mutations are authorized.

## Resolved CLI premise

`ADR-github-pull-request-repository-binding` records the Host-approved correction of unsupported universal `-R`
syntax and unstructured ruleset output. Explicit host/repository binding remains mandatory. Use required-check
queries to distinguish optional failures from required failures; aggregate status alone does not identify that set.


## Implementation assumptions

The provider's actual module is `packages/devkit-spec/src/devkit_spec/integration.py`, not an integration directory;
its test module is `packages/devkit-spec/tests/test_integration.py`. The Host explicitly expanded the worker scope
for those files and the new superseding adapter ADR. The synchronous REST correction preserves no-queue authority.
The worker contract is emulated through explicit absolute workdir, scoped permission requests and Host diff
validation; it is not native filesystem isolation. Platform documentation evidence and external verification limits
are recorded in the unit's platform-verification material. No external remote mutation or external test repository creation occurred.
