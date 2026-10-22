---
reconcile_id: REC-scope-boundary-candidates
feature: SPEC-scope-boundary-candidates
status: pending
targets:
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
    resolution: modified
---

# Reconciliation

`CAP-COLL-work-scope-registry` §4.1 now limits the `candidate` input row to bundles that declare no code and states
the rule after the input table: once a `_Boundary` entry of a spec bundle's `tasks.md` is a code path, its code side
is its declared code and it contributes no candidate; a proposal and a bundle with a missing, skeleton or code-less
`tasks.md` keep the candidates; `no-entrypoints` stays reported in both cases; a stored record changes rule at its
next recollection. The `declared-code` row drops "wins over a candidate of the same path", which no longer applies
once declared code replaces the candidates. §4.2 states that a spec bundle with declared code is compared by its
declared and observed code only. This matches `from_spec` in
`packages/devkit-spec/src/devkit_spec/features/scope/usecases/inputs.py` and its tests.

`UC-run-parallel-work-safely` is unchanged: its precondition lists the targets' `entrypoints` among the inputs a task
declares its scope with, which still holds before code is declared; Scenario 4 (`no-entrypoints` for a spec whose
`reconcile.md` targets a capability without `entrypoints`) still holds at every stage
(`SPEC-scope-boundary-candidates` Non-Goal 1, AC-05). No architecture invariant, ADR, glossary term, command, output
line or code changes, so no other Living Spec document is affected. The `spec-orchestrate` guidance (serialize units
that overlap in `devkit spec scope query`) needs no change: it now receives fewer candidate-only overlaps.

## Entrypoint review

`devkit spec entrypoints derive` proposes only the two scope test files for `CAP-COLL-work-scope-registry`; both are
rejected (tests are no doorway). The scope feature directory is already declared, so no `entrypoints` change.

## Source feedback

`FB-scope-observation-candidates` is resolved: its candidate overlaps came from the `entrypoints` of a broad reconcile
target, which no longer contribute once `tasks.md` declares code. Disposition and verification are in the feedback
file. No work is deferred.
