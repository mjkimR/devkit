---
id: SPEC-reverify-summary-required
title: envelope reverify requires a summary that envelope commit accepts
summary: Makes devkit workflow envelope reverify refuse a missing summary so every envelope it writes passes envelope commit, and makes the commit refusal name the failing field and its flag, closing FB-reverify-writes-envelope-commit-refuses.
status: completed
created: 2026-11-16
related_capabilities: [CAP-DLV-workflow-envelopes, CAP-DLV-cli-and-output]
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-reverify-summary-required] envelope reverify requires a summary that envelope commit accepts

## 1. Problem Statement & Motivation

An agent closing a review round runs `devkit workflow envelope reverify --from latest --resolve all` and then
`devkit workflow envelope commit --file envelopes/reverify-NN.yaml`. Without `--summary` the writer reports success
and writes `summary: ''`, and the commit command then refuses the file with `ENVELOPE_COMMIT_INVALID` and a generic
`[FIX]` that names neither the empty summary nor the flag that fills it. The agent can only recover by hand-editing
the YAML, which the record contract forbids. Every review loop passes this path, so the friction recurs per round.

## 2. Defect Characterization

- **Current behavior**: `uv run devkit workflow envelope reverify --unit <dir> --stage review-refine --from latest
  --resolve all` exits `0` and prints `[ENVELOPE: envelopes/reverify-01.yaml kind=reverify seq=01 status=completed
  open_findings=0]`; the file holds `summary: ''`. `uv run devkit workflow envelope commit --unit <dir> --file
  envelopes/reverify-01.yaml` then exits `2` with `(ENVELOPE_COMMIT_INVALID) envelope needs a nonempty summary, a
  declared stage and the current workflow/segment` and the `[FIX]` "Finish this existing envelope with its current
  Unit identity, or commit it manually" (evidence in `FB-reverify-writes-envelope-commit-refuses`).
- **Expected behavior and its basis**: `CAP-DLV-workflow-envelopes` section 2 writes an authored envelope complete
  "so that no agent edits YAML by hand", and its section 5 item 3 makes a nonempty summary a condition of an explicit
  commit; an authored reverify without a summary is therefore incomplete and must be refused before writing.
  `ARCH-08-1-agent-output` and `CAP-CLI-agent-cli-toolkit` require every refusal to carry a stable code and a
  deterministic fix naming what to correct, so the commit refusal must name the field that fails and the flag that
  fills it.
- **Behavior to preserve**: a reverify with `--summary` keeps writing and committing as before
  (`test_envelope_commit.py::test_review_reverify_final_report_readiness_and_read_only_commands`); the existing
  `--from`, `--resolve` and `--waive` refusals keep their codes (`test_output_contract.py`,
  `test_layouts_and_authoring.py`); a bare skeleton (no authoring flag) is still written as `needs_input`; the loader
  still accepts stored reverify envelopes without a summary (`test_envelope_record_gaps.py`); the commit command still
  refuses a skeleton or a stale identity with `ENVELOPE_COMMIT_INVALID` and stages nothing
  (`test_envelope_commit.py`).
- **Reproduction conditions**: any Git workspace with a bound unit whose current segment holds a review envelope; run
  the two commands above. The integration tests reproduce it with `testsupport.workflow.simple_workspace`.

## 3. Non-Goals

1. **Scope Excluded**: requiring `--summary` on the other authoring commands (`envelope new`, `worker`, `review`,
   `answer`); only `reverify` is reported, and its summary is the judgment that closes a round.
   - **When to Reconsider**: when another kind command is reported writing an envelope the commit command refuses.
2. **Scope Excluded**: requiring `--stage` on `envelope reverify` or validating it against the definition; the commit
   refusal names `--stage` when the stage is the failing field.
3. **Scope Excluded**: deriving a summary from the carried findings, or changing the loader contract so stored
   envelopes without a summary become malformed.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] reverify refuses a missing or blank summary
- **Given** a bound unit whose current segment holds a review envelope
- **When** `devkit workflow envelope reverify --unit <dir> --from latest --resolve all` runs without `--summary`, or
  with `--summary "  "`
- **Then** it exits `2` with `ENVELOPE_FLAG_INVALID`, `[TARGET] --summary` and a `[FIX]` that names `--summary`, and
  no `reverify-NN.yaml` file is written

### [AC-02] commit refusal names an empty summary and its flag
- **Given** an uncommitted envelope file with `summary: ''` (a filled skeleton or a file written before this fix)
- **When** `devkit workflow envelope commit --unit <dir> --file <file>` runs
- **Then** it exits `2` with `ENVELOPE_COMMIT_INVALID`, a message naming `summary` as empty, a `[FIX]` naming
  `--summary` and the same-file `envelope commit` retry command, and HEAD and the index are unchanged

### [AC-03] commit refusal names an undeclared stage and its flag
- **Given** an uncommitted authored envelope whose `stage` the bound workflow does not declare
- **When** `devkit workflow envelope commit` runs on it
- **Then** it exits `2` with `ENVELOPE_COMMIT_INVALID`, a message naming the stage and the workflow, and a `[FIX]`
  naming `--stage`

### [AC-04] a reverify with a summary still writes and commits
- **Given** a bound unit with a committed review envelope
- **When** `envelope reverify --stage <declared stage> --from latest --summary "<judgment>"` runs and
  `envelope commit` commits the written file
- **Then** both exit `0` and the commit outcome is `committed`

### [AC-05] other reverify refusals and the skeleton keep their behavior
- **Given** a bound unit with a review envelope
- **When** `envelope reverify` runs with `--summary` but without `--from`, with `--from latest --resolve 9` and no
  `--summary`, or with no authoring flag
- **Then** the first exits `2` with `ENVELOPE_FROM_INVALID`, the second exits `2` with `ENVELOPE_FLAG_INVALID` and
  `[TARGET] --resolve`, and the third exits `0` with a `needs_input` skeleton (`skeleton=yes`)

## 5. Source feedback

- `FB-reverify-writes-envelope-commit-refuses` (scope: repo)
