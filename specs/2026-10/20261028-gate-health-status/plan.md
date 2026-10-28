---
id: PLAN-gate-health-status
spec: SPEC-gate-health-status
---

# Technical Plan: `SPEC-gate-health-status`

## 1. Constitution & Invariant Review

None. `ARCH-05-2-components` requires distribution independence from the harness. Entry-point inversion keeps
that invariant; `CAP-GATE-commit-gates` remains the owner of hook diagnosis. The CLI is already JSON-only.

## 2. Architecture Overview & Impact

Distribution loads optional checks in its installation services and appends their notices to project status.
Harness metadata registers a gate-owned function composing `GateStatusUseCase`; it returns only existing hook
notices. Host-hook reporting and core status errors remain separate. No new runtime dependency or stored state.

## 3. Component & Interface Design

```mermaid
graph LR
    Status[Distribution status] --> Loader[Optional status check loader]
    Loader -. devkit.status_checks .-> Gate[Gate status check]
    Gate --> Existing[GateStatusUseCase]
```

The normative provider signature is `check(root: Path) -> list[AdvisoryError] | tuple[AdvisoryError, ...]`.
Providers are read-only and return `WARNING` or `NOTICE`, preserving advisory identity and severity. Ordering is
`(entry.name, entry.value)`; provider result order is retained. Validate the whole result before appending.
Use `STATUS_CHECK_EXTENSION_FAILED` with the provider identity, failure details and an actionable developer report
for discovery, loading, invocation and malformed results. Catch `Exception` and `SystemExit`, preserving interrupts.

The gate provider skips non-Git directories using the existing project-root repository query. In Git it composes
`GateStatusUseCase` and returns its hook notices, without calling any gate's `run`. Validation errors are outside
this narrow hook-diagnostic extension and remain available in dedicated gate status.

## 4. Error Handling & Edge Cases

Providers run whether or not a receipt exists because gate installation is independent of asset synchronization.
An absent provider adds nothing. Optional failures warn without concealing receipt problems or later providers.
Disabled gates add no warning. Existing hooksPath and pre-commit chaining rules are reused unchanged.

## 6. Verification & Test Plan

- Distribution integration tests: deterministic discovery, valid advisories, atomic invalid-result rejection,
  discovery/load/execution failures, interrupts, warning/strict JSON behavior, and core-error retention (AC-03/04).
- Gate integration tests: installed metadata target, overwritten dispatcher, deleted/non-executable entry,
  hooksPath, healthy/disabled/non-Git cases, no gate execution or mutation, and disabled-check baseline (AC-01/02/04).
- `just lint-check devkit-dist`, `just lint-check devkit`, `just check devkit-dist`, `just check devkit`.
- `just test-affected` retains its full fallback; `just test-dist` verifies absence of the optional harness.
- `uv run devkit rules check --ci --base main` and stage-specific Unit checks.
