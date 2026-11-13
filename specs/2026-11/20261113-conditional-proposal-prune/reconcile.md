---
reconcile_id: REC-conditional-proposal-prune
spec: SPEC-conditional-proposal-prune
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
    resolution: modified
---

# Reconcile: `SPEC-conditional-proposal-prune`

## Contract reflection

`CAP-DLV-proposal-lifecycle` section 4.4 and its summary now state the exact applicability condition shared by integration_plan and _parse_targets: full path history reachable from the pinned source or target, one source-revision target when present, and an empty proposal target tuple otherwise. The paragraph preserves exact tuple refusal, scope cleanup and provider failure behavior. No API, feature edge, authority, standalone prune or classic callback changes. `CAP-INT-mcp-services` remains satisfied by the existing digest and revision contract and requires no restatement. The nonexistent reference/proposals.md is not added.

## Verification and review

Medium independent code review found one P2 in Git path simplification. The fix uses --full-history and the permanent merged-before-both-pins regression passes, alongside 17 targeted cleanup tests. Implementer self-reverification closed the finding without scope expansion. The initial 53 delivery/plan-accept E2E and 1820 affected tests passed; the affected suite is rerun after the source fix. Lint covers 311 Python files; pyright reports zero errors/warnings. Final checks and exact source identities are in the Unit envelopes.

An ignored before/after probe disables the helper to reproduce the accepted branch-slug behavior: spec-only proposal target count 1 to 0, handoff 1 to 1, successful prune and unchanged retry identity. No base checkout was used. No deferred required work remains.

## Source feedback

`FB-integration-prune-without-proposal` is resolved by the verified implementation, exact-target regressions and the recorded before/after measurement. Its Disposition names this SPEC and verification evidence. No unrelated source or terminal feedback is changed.

## Entrypoints

Derived candidates were cleanup.py and the two regression files. Tests are not doorway files; cleanup.py changes selection inside the existing extension without introducing a public entrypoint. Retain the capability's three existing lifecycle doorway files rather than expanding its entrypoint list.
