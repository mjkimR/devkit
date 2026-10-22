---
id: SPEC-superseded-reference-cleanup
title: Align leftover references with the current ownership and integration recoveries
summary: Repoints the remaining references to devkit-dist as the foundation owner and to the superseded review loop ADR, adds the distinct integration recoveries of the retained runtime codes to the integration use case, and gives the reconcile reviewer read-only shell access to the diff it compares.
status: completed
created: 2026-10-22
related_capabilities:
  - CAP-INT-mcp-services
  - CAP-MCP-runtime-registration
related_usecases:
  - UC-drive-development-to-integration
workflow: sdd-spec-feature
---

# [SPEC-superseded-reference-cleanup] Align leftover references with the current ownership and integration recoveries

## 1. Problem Statement & Motivation

`SPEC-contract-alignment` and `SPEC-retained-runtime-receipt` left statements outside their write scopes that no
longer describe what ships, and `SPEC-scope-boundary-candidates` found a role that cannot do what its contract asks:

- The `devkit-agt` dependency comment in `packages/devkit/pyproject.toml` calls `devkit-dist` "the shared foundation";
  `ADR-foundation-and-mcp-package-ownership` gives the foundation to `devkit-core`.
- A decision driver of `ADR-configuration-language-and-rendering` says the foundation belongs to devkit-dist and cites
  the superseded `ADR-dist-foundation-ownership`. What devkit-dist owns there is project configuration.
- The module docstring of `test_effort_procedure.py` cites the superseded `ADR-bounded-high-effort-review-loop`;
  `ADR-host-owned-review-loop-recovery` names this test in its Confirmation.
- `UC-drive-development-to-integration` lists no extension for `INTEGRATION_RECEIPT_READER_CHANGED` or
  `MCP_RUNTIME_STALE`, whose recoveries differ from "resolve and integrate again": a Host following the use case may
  restart a service where that does not help, or not restart one where it does.
- The `reconcile-reviewer` role contract asks it to compare the diff in `diff_scope` and to report a moved head as
  stale, but on claude-code it has only Read, Grep and Glob, so it can run neither `git diff` nor confirm the head.

### Source feedback

- `FB-agt-pyproject-foundation-comment`: the `devkit-dist` requirement comment in `packages/devkit/pyproject.toml`
  names it the devkit executable and distribution and keeps the lockstep clause.
- `FB-configuration-adr-foundation-driver`: the `ADR-configuration-language-and-rendering` driver is reworded
  editorially to project configuration owned by devkit-dist, citing `ADR-foundation-and-mcp-package-ownership`.
- `FB-effort-test-cites-superseded-adr`: the `test_effort_procedure.py` module docstring cites
  `ADR-host-owned-review-loop-recovery`.
- `FB-integration-usecase-coded-extensions`: `UC-drive-development-to-integration` gains step extensions for
  `INTEGRATION_RECEIPT_READER_CHANGED` and `MCP_RUNTIME_STALE` and states that the executor's other coded refusals
  are listed in `CAP-INT-mcp-services`.
- `FB-reconcile-reviewer-diff-access`: the `reconcile-reviewer` role gets read-only shell access to run the range's
  diff and confirm the head, following the `challenger` precedent. The user added this item to the unit's scope after
  `plan-intent` was recorded; that record (`decisions/01-gate-plan-intent.yaml`) names the first four only.

### Assumptions

1. The driver rewording is an editorial edit under `ADR-immutable-decisions-editable-records`: the driver's weight
   (configuration code cannot import the harness) is unchanged, and the statement it now cites is the outcome of
   `ADR-foundation-and-mcp-package-ownership` that keeps project configuration, receipts and execution binding in the
   distribution's project feature.
2. Both new extensions key to step 7: the receipt case is checked before every provider run, prepare included, and
   the stale-runtime check refuses every tool call other than a read-only one, `integration_integrate` included. A
   reader-changed refusal resumes at step 9 through the CLI route, like extension 7d; a stale-runtime refusal resumes
   at step 7 after the restart or reconnect.
3. Each new extension gets one acceptance scenario, because `usecase-writing` requires a scenario for every extension
   that changes the outcome.
4. The use case cites `CAP-MCP-runtime-registration` in extension 7g but does not add it to `capabilities:`:
   `RULE-traceability-link` then requires the capability's `usecases` list to name the use case, and capability files
   are outside this unit's write scope. The missing link pair is recorded as feedback.
5. The `reconcile-reviewer` frontmatter copies the `challenger` host settings (claude-code
   `tools: [Read, Grep, Glob, Bash]` with `disallowedTools: [Write, Edit]`, codex `sandbox_mode: read-only`,
   antigravity `run_command` with `commandExecutionPolicy: sandbox`) and keeps `x-git-actions: [read]`, its effort
   presets and an "Expected diff after the run: none." comment. The body's "you have no shell" clause is dropped,
   because it would be false; the role still reads the context files instead of running `devkit get-context`.
6. The `spec-delegate` payload reference says nothing about the reconcile reviewer lacking a shell, so it stays
   unchanged; no capability states the reconcile reviewer's tool set.

## 2. User Stories

- **US-1**: As an agent reading package metadata and decision records, I want them to name `devkit-core` as the
  foundation owner and devkit-dist as the executable, distribution and project configuration owner, so that I do not
  place shared code in the wrong wheel.
- **US-2**: As an agent reading the review loop tests, I want their docstring to cite the in-effect ADR, so that I
  follow the rule the test confirms.
- **US-3**: As a Host following `UC-drive-development-to-integration`, I want the use case to give the recovery of
  each retained-runtime refusal, so that I restart the service only where that helps and take the CLI route only under
  separately granted authority.
- **US-4**: As a caller of `reconcile-reviewer`, I want the role to run the range's diff and confirm the head itself,
  so that its verification does not depend on an exported patch file and reports staleness it can check.

## 3. Non-Goals

1. **Scope Excluded**: no production code or behavior change; the integration codes, their directives and the role
   effort presets stay as they are.
2. **Scope Excluded**: no edit to completed spec bundles, materials or other bundle assets, including the stale
   "(it has no shell)" note on the `challenger` row of the `spec-delegate` payload reference, which this unit records
   as feedback.
3. **Scope Excluded**: no use case extension for the other executor refusals (`INTEGRATION_NOT_READY`,
   `INTEGRATION_RECEIPT_CONFLICT` and the rest); the use case delegates them to `CAP-INT-mcp-services`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The devkit-agt dependency comment names devkit-dist the executable and distribution
- **Given** `packages/devkit/pyproject.toml`
- **When** `rg -n 'devkit-dist==' packages/devkit/pyproject.toml` runs
- **Then** the one matching line ends with the comment
  `# the devkit executable and distribution, released in lockstep from the same tag`, and
  `rg -c 'shared foundation' packages/devkit/pyproject.toml` reports no match

### [AC-02] The configuration ADR driver names project configuration and the in-effect ADR
- **Given** `ADR-configuration-language-and-rendering`
- **When** `rg -n 'ADR-dist-foundation-ownership|foundation belongs'` runs on its file
- **Then** it reports no match, the Decision Drivers section holds the driver "Project configuration belongs to
  devkit-dist, which cannot import the harness (`ADR-foundation-and-mcp-package-ownership`).", and `git diff` of the
  file changes that one driver only

### [AC-03] The effort procedure test cites the in-effect review loop ADR
- **Given** `packages/devkit-spec/tests/integration/bundles/spec/test_effort_procedure.py`
- **When** `rg -n 'ADR-bounded-high-effort-review-loop|ADR-host-owned-review-loop-recovery'` runs on it
- **Then** the only match is `ADR-host-owned-review-loop-recovery` in the module docstring, and the module's tests
  pass unchanged

### [AC-04] The integration use case gives the retained-runtime recoveries
- **Given** `UC-drive-development-to-integration`
- **When** an agent reads its Extensions section
- **Then** an extension keyed to step 7 names `INTEGRATION_RECEIPT_READER_CHANGED`, says a restart does not help and
  that the agent takes the CLI route run from the source's code only under separately granted authority, citing
  `CAP-INT-mcp-services`; another keyed to step 7 names `MCP_RUNTIME_STALE` with the restart or reconnect of the
  retained service, citing `CAP-MCP-runtime-registration`; the section states that the executor's other coded
  refusals and their recoveries are listed in `CAP-INT-mcp-services`; each new extension is covered by one
  acceptance scenario; and
  `uv run devkit rules check docs/usecases/delivery/UC-drive-development-to-integration.md` exits 0

### [AC-05] The reconcile reviewer runs the range's diff read-only
- **Given** the `reconcile-reviewer` role contract in the `spec` bundle
- **When** its frontmatter and body are read and `uv run devkit sync` regenerates the projections
- **Then** claude-code has `tools: [Read, Grep, Glob, Bash]` and `disallowedTools: [Write, Edit]`, codex has
  `sandbox_mode: read-only`, antigravity has `run_command` in `tools` and `commandExecutionPolicy: sandbox`,
  `x-git-actions` stays `[read]`, the body directs the role to run the diff of `diff_scope` and to confirm the head
  itself, `test_role_contracts.py` asserts these host settings, the projected `.claude/agents/reconcile-reviewer.md`,
  `.codex/agents/reconcile-reviewer.toml` and `.agents/agents/reconcile-reviewer.md` carry them, and
  `uv run devkit sync --check` exits 0
