---
reconcile_id: REC-git-operator-planning-completion-route
spec: SPEC-git-operator-planning-completion-route
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconcile: `SPEC-git-operator-planning-completion-route`

## Contract comparison

- `CAP-DLV-proposal-planning`, Host-authorized proposal lifecycle CLI: states that the composed
  `devkit spec proposal accept <slug> --by user|policy --mode accept_only|accept_and_handoff` is the single Planning
  acceptance route, run by the Host itself, with no git-operator job before or after it and no git-operator acceptance
  operation (AC-01, AC-02); that a refusal in preparation writes nothing, and that a refusal after the acceptance
  commit returns `needs_recovery` with `completed_steps` and the accepted, unmerged `plan-<slug>` to the Host, which
  prepares the source and only then reruns, never repeating a deterministic refusal (AC-02). Code and tests:
  `native_plan_accept.py` (`PlanAcceptUseCase.execute` returns `needs_recovery` once `acceptance_commit` is completed;
  `_Acceptance.preview` continues from an accepted branch) is unchanged, its tests in `test_plan_accept_cli.py` pass
  unchanged (AC-03).
- `CAP-DLV-proposal-planning`, option table `--check` row: the composed form has no dry run; with `--mode`, `--check`
  is a usage error (exit `2`) with the reason and the two read-only commands, and `--direct` with `--mode` is
  `composed acceptance cannot use --direct` (AC-06). Code: `features/delivery/cli/proposals.py` `accept_cmd` and
  `_composed_check_refusal`; test `test_the_composed_form_refuses_check_and_names_the_read_only_material`.
- `CAP-DLV-delivery-workflows` §4.3, `plan-accept` rule: under `plan-accept = "auto"` a `reviewing` proposal reads as
  `[STAGE: - complete=yes]` before any acceptance; a Planning run then records its `worker` envelope at
  `direction-handoff`, where open questions hold `plan-accept` and the composed acceptance refuses with
  `SPEC_PROPOSAL_APPROVAL_NOT_READY` (AC-04, AC-05). Code: unchanged engine (`packages/devkit/`) and
  `_Acceptance.preview` hold conditions; guidance in `worker-records.md` §1 and `planning.md` step 6; test
  `test_a_question_recorded_at_direction_handoff_holds_the_composed_acceptance`.
- §4.6.1 of `CAP-DLV-delivery-workflows` (reusable lifecycle execution) is unchanged: the operator's job fields,
  effects and the GOP-06 wording stay as they are (AC-07), and `subagents/git-operator.md` is untouched.

## No-impact reasoning

- `UC-plan-and-hand-off-a-proposal`: steps 6 and 7 (the agent records the acceptance and integrates the Planning
  branch under `plan-accept`'s authority) and extension 5c already describe what the Host-run composed command does;
  they name no operator acceptance job and no dry run, so nothing contradicts the change. It lies outside the write
  scope the accepted proposal grants.
- `ADR-reusable-lifecycle-resource-manager`, `ADR-proposal-acceptance`, `ADR-host-cli-lifecycle-authority` and
  `ADR-moved-target-merge`: no decision changes; the operator's effects and the composed acceptance's behavior are
  unchanged.
- `CAP-DLV-workflow-envelopes`: the `worker` envelope's `stage` rule ("the stage `devkit workflow next` names") is
  unchanged as a contract; the Planning-specific stage choice is stated with the `plan-accept` rule it depends on.
- `docs/development/reference/integration.md` still names `accept --mode ... --by user` correctly; it is a quick
  reference outside the write scope.
- No glossary term is introduced or renamed; no screen changes.

## Deferred work and source feedback

None. The spec carries no source feedback, and no work is deferred.
