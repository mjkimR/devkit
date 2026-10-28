---
reconcile_id: REC-readiness-cli-runtime
status: resolved
targets: []
---

# Reconcile: CLI citation diagnostic guidance

## Living Spec impact

No Living Spec contract changes. The production diff changes only the shared CLI-contract remediation and its
runtime-owned rule guide. It explains the running CLI reference and two possible causes without changing matching,
lookup failures, settings, Click-root handling, exits, providers, readiness, digest or authority.

`CAP-INT-mcp-services` and the integration operational reference describe missing-import readiness failures and
separately authorized runtime recovery. They do not describe unknown-command or unknown-option remediation, and
remain consistent with this clarification. No capability, use case, architecture, decision or entrypoint changes
are needed. The rule guide is runtime-owned, absent from the deployment receipt, and `devkit sync --check` remains
clean; there are no bundle-source edits or sync outputs.

## Verification

The author compared the scoped diff, both acceptance criteria and the existing integration explanation at low
effort. The regression preserves rule ID, citation location, severity and exact lookup messages. It fails twice
with the original remediation and passes with the clarification. All 17 rule tests and 3,406 affected tests pass;
lint, types and committed governance checks pass. No unresolved findings remain.

## Source feedback and remaining scope

`FB-readiness-cli-contract-checks-the-base-runtime` is already promoted and remains unchanged. The agreed diagnostic
guidance scope is fully delivered. The underlying runtime mismatch is not fixed by this work. Historical broad
runtime comparisons are excluded scope, not a deferred requirement of `SPEC-readiness-cli-runtime`; this turn
creates no runtime workflow, build authority or follow-up commitment.
