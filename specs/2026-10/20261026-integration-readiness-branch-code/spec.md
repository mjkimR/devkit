---
id: SPEC-integration-readiness-branch-code
title: Integration names a branch rule that needs the branch's code
summary: A branch whose new synchronized rule needs package code the base runtime lacks was refused as not ready; integration now names it with INTEGRATION_RULE_RUNTIME_MISMATCH before readiness and directs a run from a runtime built from the source.
status: in-progress
created: 2026-10-26
related_capabilities:
  - CAP-INT-mcp-services
  - CAP-GOV-evaluation-lifecycle
related_usecases:
  - UC-drive-development-to-integration
workflow: sdd-spec-bugfix
---

# [SPEC-integration-readiness-branch-code] Integration names a branch rule that needs the branch's code

## 1. Problem Statement & Motivation

`devkit integration prepare|integrate` runs in the retained base checkout with that checkout's installed runtime. The
readiness provider evaluates the source's synchronized rules there: the workflow `lint-clean` check in the readiness
workspace and the CI rules snapshot both import each receipt-listed rule package. A synchronized rule is often a thin
shim that imports its implementation from a package module. When the branch adds such a rule together with the module,
or upgrades devkit to a version whose new rule needs new code, the base runtime cannot import the module and readiness
refuses with a generic `INTEGRATION_NOT_READY` (`BLOCKED`, "report it and stop") carrying `RULES_LOAD_FAILED`. The
directive is wrong for the case: nothing in the branch needs resolving, the branch's own checks pass, and the only way
forward is to evaluate with a runtime built from the source's code. Integrating `dev-foundation-documents` met this
(`FB-integration-readiness-loads-new-rule-with-base-code`), and every consumer branch that upgrades devkit to a release
with a new code-backed rule meets it too.

## 2. Defect Characterization

- **Current behavior**: From the base checkout, `devkit integration prepare dev-foundation-documents --task-kind unit
  ... --route local` refused with `INTEGRATION_NOT_READY` whose reasons were `RULES_RUN_FAILED` / `RULES_LOAD_FAILED`:
  "Failed to load rule package <tmp>/devkit-spec-readiness-*/.devkit/managed/spec/rules/steering_documents: No module
  named 'devkit_spec.features.governance.usecases.steering_documents'", and the same message from
  `<tmp>/devkit-rules-snapshot-*`. The branch added `RULE-steering-documents`, whose synchronized package imports that
  new module; base `893d3892`, branch head `6e5bb3ec`. Running the command with the task worktree's `.venv/bin/devkit`
  was refused by `INTEGRATION_RUNTIME_IN_WORKTREE`. With the user's approval, a runtime built from `git archive` of the
  branch in a scratch directory, run from the base checkout, integrated the branch.
- **Expected behavior and its basis**: Readiness evaluates the source with the code the integration lands, or names the
  runtime mismatch with its own stable code and a deterministic directive (`CAP-ADV-agent-advisory-protocol`: everything
  an agent must act on has a stable code and directive). The established case of the same kind is
  `INTEGRATION_RECEIPT_READER_CHANGED` (`CAP-INT-mcp-services`, `UC-drive-development-to-integration` 7f): a source the
  running runtime cannot evaluate is refused before the provider with its own code, and the user, with separately
  granted authority, runs integration from a runtime built from the source's code. `INTEGRATION_NOT_READY` is for
  completion conditions the source must resolve.
- **Behavior to preserve**:
  - `INTEGRATION_RUNTIME_IN_WORKTREE`: a runtime inside the worktree that integration would remove stays refused
    (`packages/devkit/tests/integration/features/integration/test_service.py`).
  - `INTEGRATION_RECEIPT_READER_CHANGED` keeps its precedence and refusal
    (`packages/devkit/tests/integration/features/integration/test_receipt_reader.py`).
  - Ordinary readiness: a completed unit is ready, and a rule package that is broken for another reason (a module no
    installed distribution provides, a syntax error) keeps the provider's `INTEGRATION_NOT_READY` with
    `RULES_LOAD_FAILED` (`packages/devkit-spec/tests/e2e/features/delivery/test_integration.py`).
  - Plain `devkit rules check`, the `rules-check` commit gate and `check --ci` keep reporting `RULES_LOAD_FAILED`
    unchanged; this change adds no behavior to the rule engine.
- **Reproduction conditions**: A synchronized repository with `[integration] provider = "spec"`; a `dev-<slug>`
  worktree with a completed spec unit commits a receipt that lists a rule asset whose Git-ignored managed module, present
  in the worktree with its recorded hash, imports `devkit_spec.features.governance.usecases.<module this runtime lacks>`;
  then `IntegrationService(base).prepare("dev-<slug>", Task("unit", ...))` in the test runtime.

## 3. Non-Goals

1. **Scope Excluded**: Readiness does not build, select or execute a runtime from the source's code by itself, and does
   not run rules in a subprocess of the source worktree's environment.
   - **Rationale**: The source worktree's environment is the branch's whole runtime, including the rule engine and the
     readiness provider that judge it, so the branch would certify itself; at a build the tree to check is the merged
     result, which neither the base nor the source environment holds. Running a source-built runtime stays an explicit,
     separately authorized Host step, as for `INTEGRATION_RECEIPT_READER_CHANGED`.
   - **When to Reconsider**: The user decides that integration may build and trust a runtime from the result commit.
2. **Scope Excluded**: The `INTEGRATION_RUNTIME_IN_WORKTREE` guard, the rule engine's loading and the
   `RULES_LOAD_FAILED` code are unchanged.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A rule that needs code the runtime lacks is named before readiness

- **Given** a source whose committed receipt lists a synchronized rule module, tracked or Git-ignored with its recorded
  hash in the worktree or base, that imports a module or name of an installed top-level package the running runtime does
  not provide
- **When** the Host runs `devkit integration prepare` or `integrate` for the source on the local or pull-request route
- **Then** it refuses with `INTEGRATION_RULE_RUNTIME_MISMATCH` (exit `2`, `actor=user`, not `BLOCKED`) naming each
  rule file and missing import in the message and the rule files in `target_files`, its directive names running
  `devkit integration integrate` from the base checkout with a runtime built from the source's code outside the worktree
  after separately granted authority, the readiness provider is not called, and no request is retained

### [AC-02] The same check covers the result tree at a build

- **Given** an approved integration whose result commit lists such a rule
- **When** the build re-checks readiness with `result_sha`
- **Then** it refuses with `INTEGRATION_RULE_RUNTIME_MISMATCH` and the target is unchanged

### [AC-03] Rules the runtime can import keep ordinary readiness

- **Given** a source whose synchronized rules import only modules and names the running runtime provides
- **When** the Host prepares the integration
- **Then** the readiness provider runs and its result is returned unchanged (ready, or `INTEGRATION_NOT_READY` for its
  reasons)

### [AC-04] A rule broken for another reason keeps RULES_LOAD_FAILED

- **Given** a synchronized rule module that imports a top-level package no installed distribution provides, or that does
  not parse
- **When** the Host prepares the integration
- **Then** no `INTEGRATION_RULE_RUNTIME_MISMATCH` is raised and the provider's refusal (`INTEGRATION_NOT_READY` with
  `RULES_LOAD_FAILED`) is unchanged

### [AC-05] Existing runtime and receipt refusals are preserved

- **Given** an interpreter inside the worktree integration would remove, or a source that changes the receipt reader
- **When** the Host prepares the integration
- **Then** it still refuses with `INTEGRATION_RUNTIME_IN_WORKTREE` or `INTEGRATION_RECEIPT_READER_CHANGED` respectively

## Source feedback

- `FB-integration-readiness-loads-new-rule-with-base-code` (scope `repo`): resolved by this unit.
