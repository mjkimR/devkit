---
id: FB-readiness-rule-api-change-undiagnosed
title: Integration readiness reports a rule engine API change as a generic rules failure
scope: repo
kind: friction
category: tool-error
target: integration_integrate readiness provider (devkit-spec) and the INTEGRATION_RECEIPT_READER_CHANGED diagnosis
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-22
---

# [FB-readiness-rule-api-change-undiagnosed] Integration readiness reports a rule engine API change as a generic rules failure

## 1. Friction / Question (friction, question)

- **Context**: Integrating `SPEC-lint-clean-target-scoped-rules` through the retained MCP service under shared base
  `dev-integration=auto`. The branch adds an `inputs` argument to `BaseRule` and passes it from three bundle rules.
- **Expectation**: As for a receipt schema change (`INTEGRATION_RECEIPT_READER_CHANGED`), a source branch that changes
  the rule engine API its own bundle rules use is diagnosed with a dedicated code whose action names the CLI route run
  from the source's code.
- **Actual**: The readiness provider loads the source tree's managed rule files with the service's installed engine
  (the target's code), so the three rules fail to load and the refusal is `INTEGRATION_NOT_READY` with
  `RULES_RUN_FAILED` / `RULES_LOAD_FAILED` details and a BLOCKED guardrail action. Restarting the service does not help.
- **Workaround (or Interpretation Chosen)**: Stopped and reported; the user authorized the CLI route
  (`devkit worktree finish <branch> --merge --local-only` from the base), followed by the cumulative check on the
  merged result.
- **Suggestion**: Extend the reader-change diagnosis to rule loading: when source-tree rules fail to load under the
  running engine, target-tree rules load, and the source range changes the rule engine's public contract
  (`devkit_agt.features.rules` models/base), refuse with a dedicated code that names the CLI route, as the receipt case
  does. A sibling change that adds an engine API used by rules (the rule-shared-python-ast unit, in Development) meets the same refusal.

## Evidence

```text
integration_integrate dev-lint-clean-target-scoped-rules: INTEGRATION_NOT_READY (BLOCKED)
  RULES_RUN_FAILED: Failed to load rule package .../.devkit/managed/advisory/rules/unique_code:
  BaseRule.__init__() got an unexpected keyword argument 'inputs' (also devkit-dev architecture, usecase-boundaries)
Source branch checks: rules check --ci 0 errors; test-affected 2672 passed.
CLI merge 8240e402; cumulative check on the result: rules check --ci 0 errors, 2672 passed.
```

## Disposition

- **Disposition**: dismissed by the user's decision: this mismatch occurs exclusively when dogfooding devkit development inside this repository (modifying `BaseRule` / rule engine core APIs in a branch while running MCP from the base target), not in consumer repositories where devkit is an installed external package. For this rare dogfood scenario, the existing CLI merge route (`devkit worktree finish <branch> --merge --local-only` from the base checkout) is a sufficient and safe workaround without introducing additional engine diagnosis complexity.
