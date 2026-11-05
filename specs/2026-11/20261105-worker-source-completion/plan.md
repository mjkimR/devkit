---
id: PLAN-worker-source-completion
spec: SPEC-worker-source-completion
---

# Technical Plan: `SPEC-worker-source-completion`

## 1. Constitution & Invariant Review

Keep `ARCH-05-2-components` worker use-case ownership and committed Git inputs. No new feature dependency,
architecture change or authorization mechanism. `ADR-feedback-lifecycle-ledger` source completion stays intact.

## 2. Architecture Overview & Impact

Pass the resolved audit base from inspection to scope derivation. Preserve the returned-head source resolver.
For a resolved source only, check that the same exact path exists at base with matching ID and open status.
Reuse the base file inventory once per derivation; missing paths do not grant scope. Existing open sources,
explicit replacement scope, ambiguous IDs and other terminal statuses retain their behavior.

The alternative is requiring every task to repeat source paths in boundaries. It works with existing overrides
but leaves a normal completion transition producing false failures in the default tool path.

## 6. Verification & Test Plan

Keep a Git-backed regression proving failure before the fix and success after it. Cover dated/undated paths,
explicit and derived audit bases, terminal/missing/unknown/changed-ID bases, open-to-other-terminal exclusion,
repeat turns and narrow explicit scope. Run the worker integration tests, Ruff, Pyright, CI rules and
`just test-affected` with full fallback. Update `CAP-DLV-delivery-workflows`, reconcile the exact diff and resolve
the named feedback only after verification. After local integration, sync dependencies and assets in fresh
processes and rerun required final checks against the saved target SHA.
