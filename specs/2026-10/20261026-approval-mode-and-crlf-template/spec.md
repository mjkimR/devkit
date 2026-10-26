---
id: SPEC-approval-mode-and-crlf-template
title: Approval refusal mode, completion report wording and CRLF-preserving config template
summary: 'Resolves three feedback items: proposal approval refusals render BLOCKED, the completion guidance drops report-URI wording, and devkit config template keeps a file''s existing line endings.'
status: in-progress
created: 2026-10-26
related_capabilities:
  - CAP-DLV-proposal-incubation
  - CAP-DIST-sync-and-transactions
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-approval-mode-and-crlf-template] Approval refusal mode, completion report wording and CRLF-preserving config template

## 1. Problem Statement & Motivation

Three open feedback items need the change the user agreed (`materials/decisions.md`):

- `devkit spec proposal accept --mode` refuses an unmet Planning or worktree prerequisite with
  `PROPOSAL_APPROVAL_NOT_READY`, which derives the `MAINTENANCE` directive ("a codebase defect or tool failure
  occurred"), although the caller resolves the prerequisite. The same error also covers a mode or effort the caller
  chose wrongly. The composed handoff already renders these causes as `BLOCKED` (`SPEC_HANDOFF_NOT_READY`) and
  `INPUT_ERROR` (`SPEC_HANDOFF_REPLY_INVALID`), and `CAP-DLV-proposal-incubation` documents no mode for the
  `PROPOSAL_APPROVAL_*` rows.
- The `spec` skill's completion reference tells an agent to preserve a "report URI" across a stale recovery, although
  acceptance and handoff take no published report.
- `devkit config template` reads `.devkit/config.toml` with newline translation and writes LF, so on a CRLF file that
  lacks a template part it rewrites every existing line ending while `added` names only the template parts.
  `CAP-DIST-sync-and-transactions` (Commented Template) says no line is changed.

## 2. User Stories

- **US-1**: As a Host agent running `devkit spec proposal accept --mode`, I want a refusal I can fix to say so, so
  that I resolve the prerequisite or correct the mode or effort instead of reporting a tool defect.
- **US-2**: As a Host recovering a stale acceptance or handoff, I want the guidance to name only the state the CLI
  uses, so that I do not look for a report URI.
- **US-3**: As a developer with a CRLF `.devkit/config.toml`, I want `devkit config template` to add only its lines,
  so that the diff shows the template and nothing else.

## 3. Non-Goals

1. **Scope Excluded**: a mode change of `PROPOSAL_APPROVAL_STALE`, which stays `MAINTENANCE` like
   `SPEC_HANDOFF_STALE`: a changed source, base or acceptance delta needs inspection before any further effect.
2. **Scope Excluded**: line-ending preservation for the selection edits (the commands that rewrite `agents` or
   `[presets]` through `prepare_config_update`); only `devkit config template` is in the agreed scope.
3. **Scope Excluded**: support for a lone-CR file, which is not valid TOML and is refused with `CONFIG_INVALID`
   before anything is written.
4. **Scope Excluded**: a change to which template parts are added or where they go.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] An unmet approval prerequisite renders BLOCKED
- **Given** `ProposalApprovalNotReadyError` raised with any prerequisite message of `native_plan_accept.py`
- **When** it is rendered (`to_dict()["advisory"]`)
- **Then** its code is `PROPOSAL_APPROVAL_NOT_READY`, its mode is `BLOCKED` and `guardrail` is true

### [AC-02] An invalid approval mode or effort renders INPUT_ERROR
- **Given** a mode other than `accept_only` or `accept_and_handoff`, `accept_and_handoff` without a valid effort, or
  a confirmation reply that widens `accept_only`
- **When** `PlanAcceptUseCase.execute`, `PlanAcceptUseCase.execute_native` or the confirmation reply check refuses
  it, and the refusal is rendered
- **Then** its code is `PROPOSAL_APPROVAL_REPLY_INVALID`, its mode is `INPUT_ERROR`, `input_error` is true and its
  `fix` names `accept_only`, `accept_and_handoff` and the efforts `low`, `medium` and `high`

### [AC-03] A stale approval stays MAINTENANCE
- **Given** `ProposalApprovalStaleError`
- **When** it is rendered
- **Then** its code is `PROPOSAL_APPROVAL_STALE` and its mode is `MAINTENANCE`

### [AC-04] The approval error table names the modes
- **Given** `CAP-DLV-proposal-incubation`, section "Proposal review briefings and combined acceptance"
- **When** the `PROPOSAL_APPROVAL_*` rows are read
- **Then** `PROPOSAL_APPROVAL_NOT_READY` names `BLOCKED`, `PROPOSAL_APPROVAL_REPLY_INVALID` names `INPUT_ERROR` and
  `PROPOSAL_APPROVAL_STALE` names `MAINTENANCE`

### [AC-05] The completion reference preserves no report URI
- **Given** the `spec` skill's completion reference source and its synchronized projection
- **When** the stale-recovery line is read
- **Then** it reads "A stale source invalidates the old request: inspect the partial state and authorize only the
  remaining effects, preserving the source SHA, authority and recovery state.", `rg -n "report URI"` on the source
  prints nothing, and `devkit sync --check` reports no drift

### [AC-06] config template keeps a CRLF file's line endings
- **Given** a `.devkit/config.toml` whose every line ends in `\r\n` and that lacks template parts
- **When** `devkit config template` runs
- **Then** it exits `0` and reports `state: updated`, the original lines appear in the result in order with their
  `\r\n` endings, no line of the result ends in a bare `\n`, and a second run reports `state: unchanged` with
  `added: []`; `--print` before the write returns the text the write produces

### [AC-07] An LF or mixed file keeps its bytes and gets LF lines
- **Given** a `.devkit/config.toml` whose lines end in `\n`, or that mixes `\n` and `\r\n` endings
- **When** `devkit config template` runs
- **Then** every original line appears in the result with its own ending, and the added lines end in `\n`

## 5. Assumptions

1. The invalid mode and effort selections get their own code `PROPOSAL_APPROVAL_REPLY_INVALID`, mirroring
   `SPEC_HANDOFF_REPLY_INVALID`, because one class cannot render both `BLOCKED` and `INPUT_ERROR`; the decision asks
   for `INPUT_ERROR` on caller-fixable input.
2. A declared `dev_effort` outside `low|medium|high` and a proposal status line that cannot be changed exactly are
   Planning prerequisites of the proposal file, so they stay `PROPOSAL_APPROVAL_NOT_READY` (`BLOCKED`).
3. "The file's own line ending" is CRLF when every `\n` in the file follows a `\r`; otherwise the added lines use LF.
   A file with mixed endings keeps every existing byte, because the template is rendered on the untranslated text.

## 6. Source feedback

- `FB-approval-refusals-emit-maintenance` (AC-01 to AC-04)
- `FB-completion-guidance-report-uri` (AC-05)
- `FB-config-template-rewrites-crlf-line-endings` (AC-06, AC-07)
