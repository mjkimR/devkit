---
id: PROP-split-composed-proposal-accept
title: Split composed Planning acceptance into its own subcommand
summary: Moves the composed Planning acceptance (accept, integrate and clean up plan-<slug>, optionally preparing handoff) out of devkit spec proposal accept into its own subcommand, so each command has one operation and one option set.
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-11-11
target_area: capabilities/delivery/
priority: low                         # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/delivery/
    - packages/devkit-spec/src/devkit_spec/base/errors.py
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/
    - packages/devkit-spec/tests/
    - docs/capabilities/delivery/
    - docs/capabilities/harness/CAP-HARN-command-mount.md
    - docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
    - docs/development/reference/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-split-composed-proposal-accept] Split composed Planning acceptance into its own subcommand

## 1. Background & Hypothesis

`devkit spec proposal accept` carries two operations selected by `--mode`
(review-refactor run `rr-20261111-guidance-cli`, finding C3-4, deferred to this draft by the user):

- Without `--mode`, the basic acceptance only records `plan-accept` and `status: accepted`. It takes `--direct`,
  `--check` and `--note`, and it is the form the `cloud-pr` route (autohub) uses for a Planning branch.
- With `--mode accept_only|accept_and_handoff`, the composed acceptance also integrates and cleans up
  `plan-<slug>`, and for `accept_and_handoff` it prepares the Development handoff, left not started. It is the only
  Planning acceptance route of a local Host (`CAP-DLV-proposal-lifecycle`).

Their option sets are disjoint and guarded by hand in the CLI adapter: `--direct` and `--check` are refused with
`--mode`, `--effort` requires `--mode`, and `--note` is ignored under `--mode`. An agent cannot tell from `--help`
which combinations are valid. Each change to acceptance must keep the guards, the two forms and three documents
aligned. The drift reconciliation of the same run had to scope the "single route" sentence to the local Host.

Hypothesis: one subcommand per operation removes the guards and makes each `--help` complete, with no change to
what either operation does.

## 2. Technical Spike Questions

- **Q1** (open, user question `q1`): the subcommand name and shape. Working candidate: `devkit spec proposal
  accept-plan <slug> --by user|policy --mode accept_only|accept_and_handoff [--effort low|medium|high]`.
- **Q2** (answered from the evidence at the worktree HEAD): the composed form is named by
  - code: the CLI adapter `features/delivery/cli/proposals.py` (`accept_cmd`, `_composed_check_refusal`, the module
    docstring), `usecases/native_plan_accept.py` (`_accept_command`, the command string a
    `SPEC_PROPOSAL_WRONG_WORKTREE` refusal names), `usecases/native_handoff.py` (the `[FIX]` naming `accept --by user
    --mode accept_only`) and `base/errors.py` (docstrings; `target_files = ("--mode", "--effort")`);
  - spec bundle sources: `spec-orchestrate/SKILL.md.jinja` and `references/git-operator-operations.md`,
    `spec-review-proposal/SKILL.md.jinja`, `spec-next/references/workflow-signals.md.jinja` and
    `references/post-handoff.md`;
  - Living Spec: `CAP-DLV-proposal-lifecycle` (examples, the composed acceptance section, the
    `SPEC_PROPOSAL_APPROVAL_REPLY_INVALID` row), `CAP-DLV-delivery-workflows` (the `proposal-handoff` policy row and the
    command table), `CAP-DLV-project-policy` (rule 3's policy reader), `UC-plan-and-hand-off-a-proposal` (the composed
    scenarios), `docs/development/reference/integration.md`; `CAP-HARN-command-mount` §4.2 lists the `proposal`
    subcommands;
  - tests: `tests/e2e/features/delivery/test_plan_accept_cli.py`, `tests/integration/features/delivery/`
    (`test_composed_output.py`, `test_approval_error_modes.py`), `tests/integration/package/test_help_and_notices.py`,
    `tests/integration/bundles/spec/` (`test_git_operator.py`, `test_sdd_baseline_guidance.py`).

  No external consumer uses it: devkit's external consumers are `devkit.advisory` and `devkit-cli`
  (`ADR-remove-unused-cli-options-without-shims`), and the `cloud-pr` route (autohub) uses the basic form. Within
  `0.x` a breaking CLI change is allowed in a minor release (`ARCH-05-3-command-plugins`, `docs/development/ci-cd.md`),
  and the bundle guidance ships in the same `devkit-spec` wheel as the command, so the old form is removed without a
  shim.
- **Q3** (answered): yes. The basic path calls `AcceptProposalUseCase` on its own branch of `accept_cmd`, separate from
  `PlanAcceptUseCase`; removing the composed branch leaves repair (`--direct`), `--check`, `--note` and the `cloud-pr`
  Planning acceptance unchanged.

## 3. Proposed Design & Impact

- Add the composed acceptance as its own `devkit spec proposal` subcommand (name and shape per `q1`) with only its
  options (`--by`, the mode selection, `--effort`, `-w`, `--format`). It calls `PlanAcceptUseCase` exactly as
  `accept --mode` does today: same sentinel kinds (`ACCEPTED`, `ACCEPTED_STOPPED`), fields, codes and exit codes.
- Remove `--mode` and `--effort` from `accept`, with the guards (`--direct` and `--check` refused with `--mode`,
  `--effort` requires `--mode`). `accept` keeps `--by`, `--note`, `--direct` and `--check`; its help describes only
  the basic acceptance.
- The new subcommand has no `--check`, so the custom `_composed_check_refusal` usage error goes; its help names the
  read-only material instead (`devkit spec proposal report <slug>`, `devkit workflow envelope check --unit <dir>`).
- Update the command strings the use cases emit (`_accept_command`, the `native_handoff` `[FIX]`), `base/errors.py`
  docstrings and `target_files`, the spec bundle sources, the Living Spec documents and the tests listed under Q2.
  `CAP-HARN-command-mount` §4.2 adds the subcommand to the `proposal` catalog row.
- Contract change, no behavior change in either operation.

### Planning decisions

- No shim for `accept --mode` (Q2 evidence); a caller passing it gets a click usage error (exit `2`).
- `handoff --effort` (composed handoff in its own form) stays out of scope: it selects a mode by a flag without
  disjoint option sets, and the review-refactor run recorded no finding for it.
- No ADR: the split moves a command form without changing an accepted decision. ADRs that name `accept --mode`
  (`ADR-local-and-pull-request-integration`, `ADR-proposal-handoff`) describe their decision at its time and stay
  unchanged (`docs/decisions/` excluded); `ADR-delivery-approval-and-lifecycle-authority` names no command form.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr split-composed-proposal-accept "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/ (created with its first file).
- On acceptance (plan-accept): devkit spec proposal accept split-composed-proposal-accept --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff split-composed-proposal-accept.
- On rejection: change only status: rejected, with the user's decision and reason as a decision sentence in the
  commit message (no quote); a later hygiene pass writes the rejection ADR and deletes the proposal directory.
-->
