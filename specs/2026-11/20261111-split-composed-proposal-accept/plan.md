---
id: PLAN-split-composed-proposal-accept
spec: SPEC-split-composed-proposal-accept
---

# Technical Plan: `SPEC-split-composed-proposal-accept` Split composed Planning acceptance into its own subcommand

## 1. Constitution & Invariant Review

None. The split moves a CLI form without changing an accepted decision: a breaking CLI change is allowed within
`0.x` (`ARCH-05-3-command-plugins`) and unused options are removed without shims
(`ADR-remove-unused-cli-options-without-shims`). The adapter keeps calling use cases only
(`ARCH-05-2-components`); no feature edge is added. ADRs that name `accept --mode` stay unchanged as history.

## 2. Architecture Overview & Impact

- `features/delivery/cli/proposals.py`: new `accept_plan_cmd` (`accept-plan`) with `--by` (required,
  `user|policy`), `--mode` (required, `accept_only|accept_and_handoff`), `--effort` (`low|medium|high`, optional),
  `-w` and `--format`. Its body is today's composed branch of `accept_cmd` unchanged (`PlanAcceptUseCase(...).execute`
  then `_echo_composed("ACCEPTED", ...)`). `accept_cmd` loses `--mode`, `--effort`, the `--direct`/`--check` guards,
  the `--effort requires --mode` guard and `_composed_check_refusal`; its help describes only the basic acceptance.
  The `accept-plan` help names the read-only material (`devkit spec proposal report <slug>`, `devkit workflow
  envelope check --unit <dir>`) in static text. Module docstring updated.
- `usecases/native_plan_accept.py` `_accept_command`: `spec proposal accept-plan {slug} --by {by} --mode
  {mode}[ --effort {effort}]`.
- `usecases/native_handoff.py`: `[FIX]` names `spec proposal accept-plan {slug} --by user --mode accept_only`.
- `base/errors.py`: docstrings of `ProposalWrongWorktreeError` and `ProposalApprovalNotReadyError` name
  `proposal accept-plan`; `ProposalApprovalReplyError.target_files` stays `("--mode", "--effort")` (both options
  exist on `accept-plan`).
- Spec bundle skill sources: `spec-orchestrate/SKILL.md.jinja`, `spec-orchestrate/references/git-operator-operations.md`,
  `spec-review-proposal/SKILL.md.jinja`, `spec-next/references/workflow-signals.md.jinja`,
  `spec-next/references/post-handoff.md`; then `devkit sync` for the projected copies.
- Living Spec: `CAP-DLV-proposal-lifecycle`, `CAP-DLV-proposal-planning`, `CAP-DLV-delivery-workflows`,
  `CAP-DLV-project-policy`, `CAP-HARN-command-mount` §4.2 catalog row, `UC-plan-and-hand-off-a-proposal`,
  `docs/development/reference/integration.md`.

## 5. Error Handling & Edge Cases

- Missing `--mode`, invalid choices and removed or foreign options are click usage errors (exit `2`) raised before
  the use case runs (AC-02, AC-04).
- `accept_and_handoff` without `--effort` reaches the use case and raises `SPEC_PROPOSAL_APPROVAL_REPLY_INVALID`
  as today (AC-03); `--effort` with `accept_only` is ignored by the use case as today (no new guard).
- All other refusals and partial-effect outcomes are unchanged because the same use case and renderer run (AC-01).

## 6. Verification & Test Plan

- Rename the composed invocations in `tests/e2e/features/delivery/test_plan_accept_cli.py` and
  `tests/integration/features/delivery/test_composed_output.py` to `accept-plan` (AC-01, AC-05 via the asserted
  `[FIX]`); replace the `--check`/`--direct` usage-error test with `accept-plan` refusing `--check`, `--direct`,
  `--note` and a missing `--mode`, and `accept` refusing `--mode` and `--effort` (AC-02, AC-04).
- An e2e test runs `accept-plan --mode accept_and_handoff` without `--effort` and asserts the refusal, its
  `target_files` `--effort` and no write (AC-03); `test_approval_error_modes.py` keeps the class default
  `target_files` (`--mode`, `--effort`).
- `tests/integration/package/test_help_and_notices.py`: `accept-plan --help` names the modes, the effort and the
  read-only commands; `accept --help` names no `--mode`/`--effort` (AC-04, AC-06).
- Handoff `[FIX]` assertion in the delivery tests (AC-05).
- `tests/integration/bundles/spec/test_git_operator.py` `COMPOSED_ACCEPT` names `accept-plan`, plus a scan that no
  spec bundle skill source names `accept ... --mode` (AC-07).
- Commands: `just lint`, the type check of `docs/development/setup.md`, `just test-affected`, the devkit-spec
  `tests/e2e/features/delivery/` suite, `uv run devkit rules check --ci --base main`, `uv run devkit sync --check`.
