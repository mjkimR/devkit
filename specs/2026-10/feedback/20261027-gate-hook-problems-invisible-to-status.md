---
id: FB-gate-hook-problems-invisible-to-status
title: Gate hook problems appear only in devkit gate status
scope: repo
kind: suggestion
category: missing-capability
target: devkit status (devkit_dist.features.distribution.usecases.status); devkit gate status
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-27
---

# [FB-gate-hook-problems-invisible-to-status] Gate hook problems appear only in devkit gate status

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `GATE_HOOK_ENTRY_MISSING` (gates installed but not run, e.g. after `pre-commit install -f`)
  is reported only by `devkit gate status`; `devkit status`, the command agents run as the health check, has no
  extension point for engine checks and reports nothing.
- **Proposed Procedure**: add a `devkit.status_checks` entry-point group that `devkit status` runs, and register the
  gate's `missing_entry_notices` there.
- **Expected Benefit**: a silently disabled commit gate shows up in the routine health check.
- **Cost & Risk**: one more extension group; status latency must stay low.
- **Attempted**: hypothesis; the walkthrough of an existing repository with the pre-commit framework showed gates
  silently off while `devkit status` reported no problem.

## Diagnostic Details

- **Reproduction**: unknown after the onboarding-polish hook rework; reachable with `pre-commit install -f`.
- **Expected / Actual**: expected `devkit status` to report it; actual only `devkit gate status` does.
- **Versions**: branch `dev-onboarding-polish`.
- **Conditions**: repositories using the pre-commit framework.
- **Workarounds Attempted**: guides warn against `pre-commit install -f`.
- **Related Assets**: `CAP-GATE-commit-gates`, `CAP-DIST-sync-and-transactions`.

## Evidence

```text
walkthrough (existing repository): devkit status -> host_hooks: [], errors: []; devkit gate status -> GATE_HOOK_ENTRY_MISSING
```
