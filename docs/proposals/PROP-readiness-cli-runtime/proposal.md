---
id: PROP-readiness-cli-runtime
title: Explain the running CLI reference in citation diagnostics
summary: "Clarify that missing CLI commands or options are checked against the currently running CLI and can indicate either an invalid citation or an older runtime, without changing checks or integration behavior."
status: accepted
created_at: 2026-10-28
target_area: capabilities/integration/
priority: high
size: S
planning_effort: low
dev_effort: low
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/services/builtins/cli_contract/
    - docs/capabilities/integration/
  excludes:
    - packages/devkit-spec/
    - packages/devkit-mcp/
    - packages/devkit/src/devkit_agt/features/integration/
task_kind: bugfix
workflow: sdd-proposal
---

# [PROP-readiness-cli-runtime] Explain the running CLI reference in citation diagnostics

## 1. Background & Hypothesis

`FB-readiness-cli-contract-checks-the-base-runtime` records valid branch CLI additions rejected against the older
retained runtime. `RULE-cli-contract` uses the currently running CLI's Click tree. Its missing-command and
missing-option guidance does not explain that the runtime itself can be older than the cited interface.

The user selected a small guidance change. This proposal improves the reader's next diagnostic step; it does not
make branch CLI additions pass integration or deliver the broader integration-runtime solution.

## 2. Technical Spike Questions

The direction is settled by the user. No further comparison, Scout, Challenger or user question is required for
this low-effort Planning turn. The earlier comparison in `materials/runtime-options.md` is historical evidence,
not the current scope or Development acceptance criteria.

## 3. Proposed Design & Impact

Clarify the existing missing-command and missing-option diagnostic guidance in the CLI-contract rule. The guidance
MUST say that citations are checked against the currently running CLI. It MUST explain both possible causes: the
citation is invalid, or the running runtime is older than the cited interface. It MUST NOT assert that runtime
incompatibility is proven merely because lookup failed.

Recommended wording for Development to refine within the existing advisory layout:

> CLI citations are checked against the currently running CLI. A missing command or option can mean an invalid
> citation or an older runtime. Check the running CLI's help and compare it with the intended interface.

Retain the existing rule ID, citation location, unresolved command or option, failure result and exit behavior.
Keep current matching, options, settings, Click-root handling, readiness, digest and authority behavior unchanged.
The implementation scope is diagnostic text plus focused rule-local regression coverage. Update the existing rule
guide or operational reference only where needed to keep its explanation consistent. A capability edit is needed
only if its existing diagnostic guidance otherwise conflicts; no new behavioral contract is proposed.

A brief dogfood note MAY point to the separately authorized retained-runtime recovery already described in
`CAP-INT-mcp-services`. It MUST NOT define a new workflow or imply permission to build, install or execute a runtime.

### Scope excluded

- Runtime selection, installation, launch or build machinery, including automatic source execution.
- Changes to validation, Click-root handling, readiness, exit codes, CLI options, digests or authority.
- Runtime fingerprints, metadata manifests, whole-runtime wheel tests, cleanup tests or consumer-upgrade scenarios.
- Delivering the originally proposed broader integration-runtime fix.

## 4. Lifecycle & Retirement Criteria

Development starts after the Host's normal acceptance and handoff. Its focused acceptance criteria are:

- **AC1**: Given an unknown command or option, the diagnostic identifies the currently running CLI as the reference
  and states invalid citation and older runtime as possible causes without asserting a proven mismatch.
- **AC2**: The same fixtures preserve the rule ID, citation location, unresolved command or option and failure
  result. Existing passing citations and matching/settings behavior remain unchanged.
- **AC3**: Any touched guide or operational reference agrees with the diagnostic. It adds no runtime workflow or
  behavior change and grants no authority.

Use focused rule regression tests and relevant repository checks during Development. Planning checks proposal
boundaries, document rules and envelopes only. No runtime build or integration scenario is required by this scope.

## Planning decisions

- The user's direction replaces the earlier runtime-design scope with diagnostic guidance only. Size is S and
  both Planning and Development effort are low because the direction leaves nothing further to settle.
- Withdraw and delete the `explicit-readiness-cli-surface` PADR. Its runtime/check-context design exceeds the
  user-selected guidance scope; this change needs no lasting architectural decision or replacement PADR.
- Earlier envelopes and materials remain historical evidence. Their broader runtime acceptance criteria and
  recommendations do not apply to the current proposal or its Development work.

## Source feedback

- `FB-readiness-cli-contract-checks-the-base-runtime` remains promoted to this proposal. The current goal covers
  its diagnostic guidance only; Planning does not claim the underlying integration/runtime behavior is fixed.
