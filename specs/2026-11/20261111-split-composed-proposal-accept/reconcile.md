---
reconcile_id: REC-split-composed-proposal-accept
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-command-mount.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
    resolution: modified
---

# Reconcile: `SPEC-split-composed-proposal-accept`

The composed Planning acceptance is now `devkit spec proposal accept-plan <slug> --by user|policy --mode
accept_only|accept_and_handoff [--effort low|medium|high]`; `devkit spec proposal accept` keeps only the basic
acceptance (`--by`, `--note`, `--direct`, `--check`). Neither operation changed behavior, sentinels, codes or exit
codes.

- `CAP-DLV-proposal-lifecycle`:
  - the CLI example names `accept-plan`;
  - the option table lists `--by` for both commands and `--mode` and `--effort` for `accept-plan`;
  - the `--check` row no longer describes a refusal under `--mode`; a paragraph after the table states the options
    each form lacks (click usage errors, exit `2`, no shim), that `accept-plan` has no dry run, and the read-only
    commands its help names;
  - the output, error-code rows (`SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED`, `SPEC_PROPOSAL_POLICY_NOT_AUTO`,
    `SPEC_PROPOSAL_WRONG_WORKTREE`) and the Host-authorized lifecycle CLI section name `accept-plan`;
  - the `SPEC_PROPOSAL_APPROVAL_REPLY_INVALID` row now states the existing `[TARGET]` of a missing effort
    (`--effort` only), which the new AC-03 test asserts.
- `CAP-DLV-proposal-planning` rule 14: `accept` never commits, merges or hands off; `accept-plan` composes them.
- `CAP-DLV-delivery-workflows`: the `proposal-handoff` row names `accept-plan --mode accept_and_handoff`; the command
  table gives `accept-plan` its own row and the `accept` row describes only the basic form.
- `CAP-DLV-project-policy` rule 4 names `accept-plan --mode accept_and_handoff` as a reader of `proposal-handoff`.
- `CAP-HARN-command-mount` §4.2 adds `accept-plan` to the `proposal` catalog row; no other section changed.
- `CAP-HARN-agent-guidance` (scope extension on Task 1.2, found by the reconcile check): the skills table names
  `proposal accept-plan` for `spec-orchestrate`, `spec-next` and the local `spec-review-proposal`, keeping `proposal
  accept` for its other environments and `accept --check`; the Host-authorized acceptance paragraph names
  `devkit spec proposal accept-plan`.
- `UC-plan-and-hand-off-a-proposal`: the scope lists `accept-plan`, and scenarios 24 and 25 run it.
- `docs/development/reference/integration.md` (quick reference, not a Living Spec target) names the `accept-plan`
  command for a local Host.

Not changed: ADRs that name `accept --mode` (`docs/decisions/` describes each decision at its time) and historical
materials under `docs/materials/`.

## Entrypoints

No capability or use case entrypoint changes: the new subcommand lives in
`packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py`, already an entrypoint of
`CAP-DLV-proposal-lifecycle`.
`devkit spec entrypoints derive` proposed only broad directories (`features/delivery`, `bundles/spec/bundle/skills`,
`tests`) and `base/errors.py` for every target; all were rejected as hub or helper paths.
