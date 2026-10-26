---
id: PLAN-handoff-modes-and-template-report
spec: SPEC-handoff-modes-and-template-report
---

# Technical Plan: `SPEC-handoff-modes-and-template-report` Handoff refusal modes, reviewer probes, plain handoff role and template change report

## 1. Constitution & Invariant Review

None. `CAP-ADV-agent-advisory-protocol` derives the mode from the error fields (input error, then guardrail, then
actor), so the two handoff errors reach their documented modes through class attributes alone. `ADR-host-cli-lifecycle-authority`
already places the decision with the Host; AC-07 states it for the plain handoff without changing behavior. No
`MUST` of `docs/architecture/` changes.

## 2. Architecture Overview & Impact

- **Handoff errors** (`packages/devkit-spec/src/devkit_spec/base/errors.py`): `HandoffNotReadyError` gets
  `guardrail = True` (`BLOCKED`, before the `DEVELOPER` actor rule) and the fix "Resolve the prerequisite the message
  names, then rerun devkit spec proposal handoff from the retained base checkout"; `HandoffReplyError` gets
  `input_error = True` (`INPUT_ERROR`); `HandoffStaleError` keeps `MAINTENANCE` and drops "publish a current report".
  Docstrings name the modes. `native_handoff.py` raises are unchanged: every raise already uses the class whose mode
  fits (AC-01 to AC-03). In `features/delivery/usecases/native_plan_accept.py` the `PROPOSAL_APPROVAL_STALE` and
  `PROPOSAL_APPROVAL_NOT_READY` fixes drop the report wording (text only, assumption 2).
- **Code-reviewer guidance** (`bundles/spec/bundle/subagents/code-reviewer.md` rule 4 and
  `skills/spec-delegate/references/payload.md`): probes go in a per-round subdirectory of the ignored probe path,
  are left for worktree removal and are never read across rounds (AC-06). `devkit sync` refreshes the projections;
  `devkit sync --check` names any tracked output for the commit. `CAP-DLV-delivery-workflows` mirrors the role row.
- **Living Spec**: `CAP-DLV-proposal-incubation` §4.12 rows (AC-05) and the lifecycle CLI section plus
  `CAP-DLV-project-policy` rule 4 (AC-07); `CAP-DIST-sync-and-transactions` Commented Template and
  `docs/development/reference/distribution.md` state the result contract (AC-09).
- **config template** (`packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config.py`):
  no code change (spec assumption 3); a CLI regression test pins AC-08.

## 3. Error Handling & Edge Cases

- `HandoffNotReadyError` covers the revoked-auto-policy refusal (`proposal-handoff policy must be ask or auto`) too;
  it becomes `BLOCKED`, which matches a policy the user changes.
- `HandoffReplyError("automatic handoff must use the proposal's declared dev_effort")` is an input the caller
  corrects, so `INPUT_ERROR` fits it as well.
- The composed CLI maps an `AdvisoryError` through the `devkit_cli` boundary to exit `2`; only the rendered
  directive changes.

## 4. Verification & Test Plan

- Red first for AC-01 to AC-03: `packages/devkit-spec/tests/integration/features/delivery/test_handoff_error_modes.py`
  pins code, mode, guardrail/input_error and the fix wording; it fails on the base for the two modes and the fixes.
- AC-04: a test in `packages/devkit-spec/tests/e2e/features/delivery/test_integration.py` runs the composed CLI on a
  base with an untracked file.
- AC-06: `packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py` pins the new
  phrases and the absence of the deletion phrase.
- AC-08: a CLI test in `packages/devkit-dist/tests/integration/features/distribution/test_config_template.py` with a
  repository-shaped config: bytes changed with `updated` and the commented table names, then unchanged bytes with
  `unchanged`, and `--print` agreeing with the write.
- AC-05, AC-07, AC-09: `rg` checks named in the tasks and `uv run devkit rules check --ci --base 2bbd8251`.
- Module checks: `just lint`/`just lint-check` and `just check` for devkit-spec and devkit-dist, `just test-affected`,
  `just test-dist`, then `uv run devkit sync` and `uv run devkit sync --check`.
