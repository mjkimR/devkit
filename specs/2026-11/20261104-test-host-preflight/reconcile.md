---
reconcile_id: REC-test-host-preflight
status: resolved
targets:
  - file: docs/development/ci-cd.md
    resolution: modified
---

# Reconciliation: `SPEC-test-host-preflight`

## Reflection

The repository verification contract in `docs/development/ci-cd.md` specifies socketpair validation for every
selection, conditional loopback bind/listen for full or known-server selections, path forwarding and conservative
option handling, coded exit-2 advisories, exact retry commands, caller-owned permissions, and conditional cold-cache
wheel dependency downloads. This is repository tooling, with no installed application capability, use case,
architecture invariant or glossary term change. No additional canonical capability is required.

## Source feedback

`FB-full-suite-host-capabilities` is resolved by the selected loopback preflight and conditional build-prerequisite
guidance. Focused57, affected72 and existing selector e2e80 tests passed. The controlled baseline comparison changed
TCP-denied full preflight from exit0 without an advisory to exit2 with `TEST_LOOPBACK_BLOCKED`; real permitted bind
succeeded. Code Review's P2 about a test-owned live TCP requirement is closed by `reverify-01.yaml`, verified with
injected TCP denial and separate successful TCP mock assertions. No required work remains deferred.

## Entrypoints

The only changed Living Spec target is repository development guidance, not a capability/use case entrypoint
owner. Derivation has no document-code pairs to apply.
