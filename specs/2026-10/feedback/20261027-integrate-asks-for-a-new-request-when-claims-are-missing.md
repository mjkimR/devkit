---
id: FB-integrate-asks-for-a-new-request-when-claims-are-missing
title: Integrate asks for a new request when only its claims are missing
scope: repo
kind: friction
category: tool-error
target: devkit integration integrate
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-27
---

# [FB-integrate-asks-for-a-new-request-when-claims-are-missing] Integrate asks for a new request when only its claims are missing

## 1. Friction / Question (friction, question)

- **Context**: Integrating a session branch on the local route: `devkit integration prepare <branch> --task-kind
  session ... --claims '<json>'`, then `devkit integration integrate <branch> --task-kind session ...
  --expected-digest <digest>` without repeating `--claims`.
- **Expectation**: Either the claims given to `prepare` carry over to `integrate`, or the refusal names the missing
  `--claims` option.
- **Actual**: `integrate` refused with `INTEGRATION_NOT_READY` (`INPUT_ERROR`), five `[DETAIL]` lines saying session
  claims require task_kind, effort, review, tests and lint, and a `[FIX]` to "resolve the reported readiness
  conditions, commit the final changes and prepare a new integration request". Preparing again returned the same
  digest; passing the same `--claims` to `integrate` completed the integration.
- **Workaround (or Interpretation Chosen)**: Repeat `--claims` on `integrate`.
- **Suggestion**: Name `--claims` in the `[FIX]` when the request's claims are absent on `integrate` (or carry them
  from `prepare`), and drop "commit the final changes and prepare a new integration request" for that case.

## Evidence

```text
[ERROR]  (INTEGRATION_NOT_READY) the configured provider refused integration
[FIX]    Resolve the reported readiness conditions, commit the final changes and prepare a new integration request
[DETAIL] session claims require task_kind in 'feature', 'bugfix' or 'overall-refactor'
...
second prepare: digest=c8bee9eb... (unchanged)
integrate ... --claims '<same json>' --expected-digest c8bee9eb... -> [INTEGRATION: status=completed ...]
```

## Disposition

`SPEC-input-recovery-notices` resolves the invocation-recovery defect. Missing or invalid session claims retain
`INTEGRATION_NOT_READY` and now target `--claims` with a same-command retry instruction. Claims remain explicit on
both commands. Regression tests verify successful retry with the original digest, ordinary source recovery and
simultaneous source/input failures. The original 2 CLI failures and 1 provider failure pass after the fix; the
affected suite passed 2157 tests and independent code review found no issues.
