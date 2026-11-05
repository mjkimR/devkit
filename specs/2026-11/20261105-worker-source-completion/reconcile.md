---
reconcile_id: REC-worker-source-completion
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconciliation: `SPEC-worker-source-completion`

## Contract comparison

`CAP-DLV-delivery-workflows` worker scope inference retains a resolved source only when its exact path and ID
were open at the audit base. The implementation passes the resolved audit base to derivation and checks only
that transition. Open returned-head sources, explicit replacement scopes, terminal-base exclusions and source
resolution errors retain their behavior. The regression suite covers AC-01 through AC-03.

No CLI flag, output field, error code, architecture edge, dependency, guide command or reusable agent procedure
changes. Existing worker CLI entrypoint remains the doorway for this behavior. Tests and helpers are not doorways.
No deferred work is required by the accepted scope.

## Source feedback

`FB-worker-inspect-resolved-source-scope` is directly addressed by the implementation, 64 worker inspection tests,
1665 affected tests, actual historical-range replay and independent code review with zero findings. Its exact
source path was included in the initial task boundary and is resolved with its verification evidence.

## Verification scope

Medium reconciliation is self-verified: the only affected contract and document is the single modified capability,
whose scope bullet and summary match the exact implementation diff. Behavior stays within devkit-spec worker;
there is no second package/capability area or repository tooling behavior change. No required mismatch is waived.
Final target-environment verification follows integration and remains a separate completion obligation.
