---
id: SPEC-split-composed-proposal-accept
title: Split composed Planning acceptance into its own subcommand
summary: Moves the composed Planning acceptance (accept, integrate and clean up plan-<slug>, optionally preparing handoff) out of devkit spec proposal accept into its own subcommand, so each command has one operation and one option set.
status: in-progress
created: 2026-11-11
related_capabilities:
  - CAP-DLV-proposal-lifecycle
  - CAP-DLV-proposal-planning
  - CAP-DLV-delivery-workflows
  - CAP-DLV-project-policy
  - CAP-HARN-command-mount
related_usecases:
  - UC-plan-and-hand-off-a-proposal
workflow: sdd-spec-feature
---

# [SPEC-split-composed-proposal-accept] Split composed Planning acceptance into its own subcommand

## 1. Problem Statement & Motivation

Handed off from proposal PROP-split-composed-proposal-accept on 2026-11-11.

`devkit spec proposal accept` carries two operations selected by `--mode` (review-refactor run
`rr-20261111-guidance-cli`, finding C3-4):

- Without `--mode`, the basic acceptance only records `plan-accept` and `status: accepted`. It takes `--direct`,
  `--check` and `--note`, and it is the form the `cloud-pr` route uses for a Planning branch.
- With `--mode accept_only|accept_and_handoff`, the composed acceptance also integrates and cleans up `plan-<slug>`,
  and for `accept_and_handoff` it prepares the Development handoff, left not started. It is the only Planning
  acceptance route of a local Host (`CAP-DLV-proposal-lifecycle`).

Their option sets are disjoint and guarded by hand in the CLI adapter: `--direct` and `--check` are refused with
`--mode`, `--effort` requires `--mode`, and `--note` is ignored under `--mode`. An agent cannot tell from `--help`
which combinations are valid, and each change to acceptance must keep the guards, the two forms and their documents
aligned.

This spec moves the composed acceptance to its own subcommand, `devkit spec proposal accept-plan`, with only its
options, and removes `--mode` and `--effort` from `accept`. Neither operation changes what it does: the same use
cases run with the same sentinels, fields, error codes and exit codes.

## 2. User Stories

- **US-1**: As a local Host agent accepting a reviewed Planning branch, I want the composed acceptance to be its own
  subcommand whose `--help` lists exactly its options, so that I can build the command without knowing which
  `accept` flags exclude each other.
- **US-2**: As an agent using the basic acceptance (`cloud-pr` route, `--direct` repair, `--check`), I want `accept`
  to describe only that operation, unchanged.

The feature changes how the local Host's acceptance step of `UC-plan-and-hand-off-a-proposal` is invoked.

## 3. Non-Goals

1. **Scope Excluded**: no change to what either acceptance does: `PlanAcceptUseCase` and `AcceptProposalUseCase`,
   the mode names, the approval reply, the readiness and policy checks, sentinel kinds (`ACCEPTED`,
   `ACCEPTED_STOPPED`, `ACCEPT_CHECK`), output fields, error codes and exit codes stay as they are.
2. **Scope Excluded**: no compatibility shim. `accept --mode` and `accept --effort` become click usage errors
   (exit `2`); the bundle guidance ships in the same `devkit-spec` wheel as the command and no external consumer
   uses the composed form.
3. **Scope Excluded**: `devkit spec proposal handoff --effort` (the composed handoff) keeps its form.
4. **Scope Excluded**: no ADR change. ADRs that name `accept --mode` describe their decision at its time and stay
   unchanged; `docs/decisions/` and the historical `docs/materials/` are not edited.
5. **Scope Excluded**: `accept-plan` has no `--check`, `--direct` or `--note`; read-only material for the Host stays
   `devkit spec proposal report` and `devkit workflow envelope check`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] `accept-plan` runs the composed acceptance unchanged

- **Given** a reviewed proposal on `plan-<slug>` that `accept --mode` accepted before this change
- **When** the Host runs `devkit spec proposal accept-plan <slug> --by user|policy --mode accept_only`, or
  `--mode accept_and_handoff --effort <low|medium|high>`, from the retained base checkout
- **Then** it calls `PlanAcceptUseCase` with the same slug, mode, effort and authority and prints the same
  `[ACCEPTED: ...]` or `[ACCEPTED_STOPPED: ...]` line, `--format json` document, notices and exit code (`0`, `1`
  after partial effects, `2` when nothing was done) as `accept --mode` did, with the fields `mode=`, `authority=`,
  `completed=`, `target_sha=`, `landed_sha=`, `verification=` and `handoff=` as before.

### [AC-02] `accept-plan` takes only its own options

- **Given** `devkit spec proposal accept-plan`
- **When** it runs without `--mode`, with a `--mode` other than `accept_only` or `accept_and_handoff`, or with
  `--check`, `--direct` or `--note`
- **Then** click refuses it with a usage error and exit `2` before any check or write (missing option, invalid
  choice or no such option); `--by` is required and limited to `user|policy`, `--effort` to `low|medium|high`.

### [AC-03] The effort check stays in the use case

- **Given** `accept-plan <slug> --by user --mode accept_and_handoff` without `--effort`
- **When** it runs
- **Then** it refuses with `SPEC_PROPOSAL_APPROVAL_REPLY_INVALID` (exit `2`), whose `target_files` names `--effort`,
  before any check or write, exactly as `accept --mode accept_and_handoff` did.

### [AC-04] `accept` keeps only the basic acceptance

- **Given** `devkit spec proposal accept`
- **When** it runs with `--mode` or `--effort`
- **Then** click refuses it with a "No such option" usage error and exit `2`; its `--help` names `--by`, `--note`,
  `--direct` and `--check` and no `--mode`, `--effort`, `accept_only` or `accept_and_handoff`; the basic acceptance,
  `--direct` repair, `--check` and `--note` behave as before.

### [AC-05] Emitted commands name the new subcommand

- **Given** a composed acceptance off the retained base checkout, or a composed handoff of a proposal that is not
  accepted on the base
- **When** the refusal renders (`SPEC_PROPOSAL_WRONG_WORKTREE`, `SPEC_HANDOFF_NOT_READY`)
- **Then** its `[FIX]` names `uv run devkit spec proposal accept-plan <slug> --by <by> --mode <mode>` (with
  ` --effort <effort>` for `accept_and_handoff`), respectively `uv run devkit spec proposal accept-plan <slug> --by
  user --mode accept_only`, and no emitted command names `accept ... --mode`.

### [AC-06] `accept-plan --help` is complete

- **Given** `devkit spec proposal accept-plan --help`
- **When** an agent reads it
- **Then** it names `accept_only`, `accept_and_handoff`, the Development activity-effort and the read-only material
  commands `devkit spec proposal report` and `devkit workflow envelope check`, and `devkit spec proposal --help`
  lists `accept-plan`.

### [AC-07] Guidance and Living Spec name one form per operation

- **Given** the spec bundle skill sources, `CAP-DLV-proposal-lifecycle`, `CAP-DLV-proposal-planning`,
  `CAP-DLV-delivery-workflows`, `CAP-DLV-project-policy`, `CAP-HARN-command-mount` §4.2,
  `UC-plan-and-hand-off-a-proposal` and `docs/development/reference/integration.md`
- **When** they name the composed acceptance
- **Then** they name `devkit spec proposal accept-plan` (in the full form `accept-plan <slug> --by user|policy --mode
  accept_only|accept_and_handoff` where they spell it out), none names `accept --mode` or `accept <slug> ... --mode`,
  and the basic form's description no longer mentions `--mode`.
