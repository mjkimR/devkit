---
id: SPEC-envelope-commit-file-path
title: Envelope commit accepts a workspace-relative --file path
summary: devkit workflow envelope commit joins a workspace-relative --file path to the unit directory and its fix repeats the failing path; accept a path that already starts with the unit directory and name a working form in the fix.
status: planned
created: 2026-11-17
related_capabilities: [CAP-DLV-workflow-envelopes, CAP-DLV-cli-and-output]
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-envelope-commit-file-path] Envelope commit accepts a workspace-relative --file path

## 1. Problem Statement & Motivation

An agent that has just written an envelope often holds its workspace-relative path
(`specs/<unit>/envelopes/review-01.yaml`) and passes it to `devkit workflow envelope commit --file`. The command
joins that value to the Unit, reports a doubled target and prints a `[FIX]` that reruns the same failing value, so
the agent cannot recover from the advisory alone.

## 2. Defect Characterization

- **Current behavior**: `devkit workflow envelope commit --unit specs/<unit> --file specs/<unit>/envelopes/review-01.yaml`
  exits `2` with `ENVELOPE_COMMIT_INVALID`, `[TARGET] specs/<unit>/specs/<unit>/envelopes/review-01.yaml`, and a
  `[FIX]` that ends with the same `--file specs/<unit>/envelopes/review-01.yaml` command
  (`FB-envelope-commit-file-path-doubled`; `CommitEnvelopeUseCase` in
  `packages/devkit/src/devkit_agt/features/workflow/usecases/commit_envelope.py` builds the target as
  `f"{unit}/{file}"` and the retry from the raw value).
- **Expected behavior and its basis**: `CAP-DLV-workflow-envelopes` §5 selects one literal immediate
  `envelopes/<kind>-<NN>.yaml` file of the Unit; a workspace-relative spelling of that same file names it
  unambiguously and is accepted as its Unit-relative form. Every refusal follows `CAP-ADV-agent-advisory-protocol`:
  its `[FIX]` is a deterministic action that can succeed, so a malformed `--file` names the Unit-relative form.
- **Behavior to preserve**: Unit-relative `--file envelopes/<kind>-<NN>.yaml` commits as before; non-literal,
  traversing, absolute and wrongly named paths stay refused before mutation (`test_nonliteral_paths_refuse`,
  `test_exact_commit_idempotence_and_evidence` and `test_cli_json_text_and_errors` in
  `packages/devkit/tests/integration/features/workflow/test_envelope_commit.py`).
- **Reproduction conditions**: a Git workspace with a tracked bound Unit `.devkit/transient/work/u` and an
  authored, uncommitted `envelopes/review-01.yaml`; run the use case or CLI with
  `--file .devkit/transient/work/u/envelopes/review-01.yaml`.

## 3. Non-Goals

1. **Scope Excluded**: no absolute `--file` paths, no glob or directory selection, no change to eligibility,
   index, Git-state or recovery rules, and no change to `--unit` resolution.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Workspace-relative path inside the Unit is accepted
- **Given** a bound Unit `U` with an authored, uncommitted `envelopes/review-01.yaml`
- **When** `envelope commit --unit U --file U/envelopes/review-01.yaml` runs
- **Then** it exits `0`, commits that one file, and reports `file=envelopes/review-01.yaml outcome=committed`

### [AC-02] Path outside the Unit is still refused with a working fix
- **Given** the same Unit `U`
- **When** `--file` names a path that is not an immediate `envelopes/<kind>-<NN>.yaml` of `U` (another Unit's
  envelope, a traversal, an absolute path or a bad name)
- **Then** it exits `2` with `ENVELOPE_COMMIT_INVALID` before mutation, its target holds no doubled Unit path, and
  its `[FIX]` names the Unit-relative form `--file envelopes/<kind>-<NN>.yaml` instead of the rejected value

### [AC-03] Unit-relative path keeps its behavior
- **Given** the same Unit `U`
- **When** `envelope commit --unit U --file envelopes/review-01.yaml` runs
- **Then** it commits as before and a repeat returns `outcome=already_committed`

## 5. Source feedback

- `FB-envelope-commit-file-path-doubled` (full scope).
