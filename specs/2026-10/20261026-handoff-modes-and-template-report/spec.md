---
id: SPEC-handoff-modes-and-template-report
title: Handoff refusal modes, reviewer probes, plain handoff role and template change report
summary: 'Resolves four feedback items: caller-fixable handoff refusals stop emitting MAINTENANCE, reviewers leave ignored probes to worktree removal, the plain handoff is the Host-run step after the decision, and config template reports its writes.'
status: planned
created: 2026-10-26
related_capabilities:
  - CAP-DLV-proposal-incubation
  - CAP-DLV-project-policy
  - CAP-DLV-delivery-workflows
  - CAP-DIST-sync-and-transactions
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-handoff-modes-and-template-report] Handoff refusal modes, reviewer probes, plain handoff role and template change report

## 1. Problem Statement & Motivation

Four open feedback items need the change the user decided (`materials/decisions.md`):

- The composed `devkit spec proposal handoff --effort` refuses an unmet prerequisite (`SPEC_HANDOFF_NOT_READY`) and
  a missing or invalid effort (`SPEC_HANDOFF_REPLY_INVALID`) with the `MAINTENANCE` directive, which tells the agent a
  tool defect occurred and to stop. `CAP-DLV-proposal-incubation` documents them as `BLOCKED` and `INPUT_ERROR`. The
  fix texts still ask for a "current report URI" or a "current report", although acceptance and handoff take no
  published report.
- The code-reviewer contract tells the reviewer to delete its ignored probes before it returns, while the workers
  leave ignored scratch files for worktree removal to clean. A probe left behind could be read by a later review
  round in the same worktree.
- Only `handoff --effort` and `accept --mode accept_and_handoff` read the `proposal-handoff` policy; the Living Spec
  does not say what the plain `devkit spec proposal handoff <slug>` in a `dev-<slug>` checkout is.
- An agent saw `devkit config template` report `state: unchanged` with `added: []` while `git diff` showed the
  commented template it had added. The result contract does not state that a byte change is always reported.

## 2. User Stories

- **US-1**: As a Host agent running the composed handoff, I want a refusal I can fix to say so, so that I resolve the
  prerequisite, correct the effort or ask the user instead of reporting a tool defect.
- **US-2**: As a Host running several review rounds, I want every reviewer round to write its probes in its own
  directory and leave them for worktree removal, so that one rule covers ignored scratch files and no round reads
  another round's probes.
- **US-3**: As an agent reading the policy contract, I want to know which handoff route reads `proposal-handoff`, so
  that I run the plain handoff only after the Host's decision.
- **US-4**: As an agent running `devkit config template`, I want its result to name every change it writes, so that I
  know a tracked file changed.

## 3. Non-Goals

1. **Scope Excluded**: a policy check or a new approval flag on the plain `devkit spec proposal handoff <slug>`
   (rejected in decision 3: the CLI does not authenticate the conversational decision, and the composed handoff would
   check twice).
2. **Scope Excluded**: reviewer deletion of probes in any form (rejected in decision 2).
3. **Scope Excluded**: a mode change of `SPEC_HANDOFF_STALE`, which stays `MAINTENANCE` as its row documents, and of
   the `PROPOSAL_APPROVAL_*` errors of `devkit spec proposal accept`.
4. **Scope Excluded**: a read-only form other than the existing `devkit config template --print`, and a change to
   which template parts are added.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] An unmet handoff prerequisite renders BLOCKED
- **Given** `HandoffNotReadyError` raised with any message of `native_handoff.py`
- **When** it is rendered (`to_dict()["advisory"]`)
- **Then** its code is `SPEC_HANDOFF_NOT_READY`, its mode is `BLOCKED` and `guardrail` is true, and its `fix` does
  not contain the word "report"

### [AC-02] An invalid handoff effort renders INPUT_ERROR
- **Given** `HandoffReplyError` raised with any message of `native_handoff.py`
- **When** it is rendered
- **Then** its code is `SPEC_HANDOFF_REPLY_INVALID`, its mode is `INPUT_ERROR` and `input_error` is true

### [AC-03] A stale handoff stays MAINTENANCE and drops the report wording
- **Given** `HandoffStaleError`, `ProposalApprovalStaleError` and `ProposalApprovalNotReadyError`
- **When** they are rendered
- **Then** `HandoffStaleError` keeps mode `MAINTENANCE` as the `SPEC_HANDOFF_STALE` row documents, and none of the
  three `fix` texts asks to publish a report

### [AC-04] The composed CLI renders the refusal mode
- **Given** a retained base checkout with an untracked file and an accepted proposal
- **When** `devkit spec proposal handoff <slug> --effort medium` runs
- **Then** it exits `2`, creates no `dev-<slug>` branch, and stderr carries `SPEC_HANDOFF_NOT_READY` with the
  `BLOCKED` directive and no `MAINTENANCE` line

### [AC-05] The error table matches the emitted modes and fixes
- **Given** `CAP-DLV-proposal-incubation` §4.12
- **When** the `SPEC_HANDOFF_NOT_READY`, `SPEC_HANDOFF_REPLY_INVALID` and `SPEC_HANDOFF_STALE` rows are read
- **Then** they name `BLOCKED`, `INPUT_ERROR` and `MAINTENANCE`, and no row asks for a report URI

### [AC-06] The code reviewer leaves its probes in a per-round subdirectory
- **Given** the code-reviewer role contract, the `spec-delegate` payload reference and `CAP-DLV-delivery-workflows`
- **When** they describe the reviewer's probes
- **Then** the reviewer writes each round's probes in its own subdirectory of the ignored probe path (for example
  `<probe path>/review-NN/`), reads no other round's probes, never deletes them and leaves them for worktree removal;
  `git status --short` stays unchanged because the path is ignored; no text says "Delete every probe" or "deleted
  before it returns"

### [AC-07] The plain handoff is the Host-run step after the decision
- **Given** `CAP-DLV-proposal-incubation` and `CAP-DLV-project-policy` rule 4
- **When** they describe the readers of `proposal-handoff`
- **Then** they state that the plain `devkit spec proposal handoff <slug>` in a `dev-<slug>` checkout is the Host-run
  step after the `proposal-handoff` decision and reads no policy itself, and that `handoff --effort` and
  `accept --mode accept_and_handoff` read the policy

### [AC-08] config template reports every byte change
- **Given** a project whose `.devkit/config.toml` has selected bundles, `[tool.spec]` settings and none of the
  commented template blocks
- **When** `devkit config template` runs, and then runs again
- **Then** the first run exits `0`, changes the file's bytes and reports `state: updated` with `added` naming every
  key and table it wrote, each commented table header included; the second run leaves the bytes unchanged and reports
  `state: unchanged` with `added: []`; `--print` before the write reports the same `state` and `added` as the write

### [AC-09] The template contract states the change report
- **Given** `CAP-DIST-sync-and-transactions` (Commented Template) and the distribution reference page
- **When** they describe the result of `devkit config template`
- **Then** they state that `state` is `unchanged` exactly when the file's bytes stay the same, and that `added` names
  every key and table written, commented ones included

## 5. Source feedback

- `FB-handoff-refusals-emit-maintenance` (AC-01 to AC-05)
- `FB-code-reviewer-probe-deletion` (AC-06)
- `FB-plain-handoff-skips-proposal-handoff-policy` (AC-07)
- `FB-config-template-reports-unchanged-after-writing` (AC-08, AC-09)

## 6. Assumptions

1. `HandoffNotReadyError` takes the documented `BLOCKED` (`guardrail = True`) for every raise, the
   worktree-provenance and wrong-checkout refusals included: each is a prerequisite the user or Host resolves, never a
   tool defect.
2. The stale report wording also stands in `HandoffStaleError.fix` and the two `PROPOSAL_APPROVAL_*` fixes of
   `native_plan_accept.py`; decision 1 states that acceptance and handoff take no published report, so they are fixed
   with it (text only, modes unchanged).
3. The reported `devkit config template` mismatch does not reproduce at base `2bbd8251` in one invocation: the write
   and its report come from the same comparison, and the repository's own `.devkit/config.toml` run through the CLI
   reports `updated` with seven added names; a second run reports `unchanged` with `added: []`, which matches the
   observation. AC-08 pins the contract with a regression test of that scenario and AC-09 states it; the report code
   needs no change.
