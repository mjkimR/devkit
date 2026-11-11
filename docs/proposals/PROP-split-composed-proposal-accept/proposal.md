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
    - capabilities/delivery/
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

- **Q1**: The subcommand name and shape. `devkit spec proposal accept-plan <slug> --by user|policy --mode
  accept_only|accept_and_handoff [--effort ...]` is the working candidate. Should the mode stay a flag, or become
  two subcommands?
- **Q2**: Which callers name the composed form today? Candidates: the spec bundle (spec-orchestrate,
  spec-review-proposal, spec-next workflow signals, git-operator operations), `CAP-DLV-proposal-lifecycle`,
  `CAP-DLV-delivery-workflows`, references and tests. Do any external consumers rely on it? The compatibility policy
  allows a removal without a shim, but confirm it.
- **Q3**: Does `accept` without `--mode` keep repair and the `cloud-pr` Planning acceptance unchanged? (Option (b)
  of the review, retiring the basic Planning form, is out of scope.)

## 3. Proposed Design & Impact

- Add the composed acceptance as its own `devkit spec proposal` subcommand with only its options. Move the use case
  wiring unchanged.
- Remove `--mode` and `--effort` from `accept`, together with the mutual-exclusion guards. `accept` keeps `--by`,
  `--note`, `--direct` and `--check`.
- Update the guidance that runs the composed form, `CAP-DLV-proposal-lifecycle` (acceptance section and examples),
  `CAP-DLV-delivery-workflows`, `CAP-HARN-command-mount` §4.2, `docs/development/reference` and the tests.
- Contract change. No behavior change in either operation. `ADR-delivery-approval-and-lifecycle-authority` may need
  a pointer if it names the command form.

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
