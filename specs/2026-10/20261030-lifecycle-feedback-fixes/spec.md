---
id: SPEC-lifecycle-feedback-fixes
title: Fix four lifecycle feedback items
summary: Fix the envelope commit fix placeholder, point the stale local render fix at a locked restore, refuse unknown worker envelope stages and state the reference writes a document rename implies, closing four open feedback items.
status: completed
created: 2026-10-30
related_capabilities: [CAP-DLV-workflow-envelopes, CAP-DIST-context-and-playbooks, CAP-DOCS-document-model]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-lifecycle-feedback-fixes] Fix four lifecycle feedback items

## 1. Problem Statement & Motivation

Four open feedback items describe small defects in the delivery lifecycle that agents work around each time:

- The `[FIX]` of `EnvelopeCommitInvalidError` for an unsupported anchor id names a `SPEC-<slug> or PROP-<slug>`
  placeholder. That breaks the agent output contract, and
  `packages/devkit/tests/integration/package/test_agent_output_contract.py::test_fixes_carry_no_placeholder` fails on
  the base, so every full-suite run reports a failure no change caused.
- The `CONFIG_LOCAL_RENDER_STALE` fix names a plain `devkit sync`. A plain sync can rewrite tracked files (the
  receipt, the managed `AGENTS.md` block, seeds) that a worker's write scope denies. Workers recovered with
  `devkit sync --locked`, which restores only ignored copies and local evidence and refuses with `RECEIPT_STALE`
  when the committed receipt itself is out of date.
- `devkit workflow envelope worker --stage` accepts any text other than `-`. An envelope whose stage the bound
  workflow does not declare is held from the first stage, so a guessed stage name holds every gate of the unit, and
  only `devkit workflow envelope commit` notices it.
- `CAP-DOCS-document-model`'s renaming step and the proposal template's `boundaries.excludes` example never say that a
  document ID rename makes `devkit rules fix` rewrite references in ADRs, PADRs and `specs/**/feedback/` files. A
  rename proposal that follows the template excludes paths its own rule fix must write.

## 2. User Stories

- **US-1**: As an agent running the full suite, I want the base to pass the output contract test, so that a failure
  in my run is one my change caused.
- **US-2**: As a delegated worker whose write scope excludes tracked distribution files, I want the stale local
  render advisory to name the restore I may run, so that `get-context` works without a write outside my scope.
- **US-3**: As a worker recording its run, I want a `--stage` the unit's workflow does not declare refused at write
  time with the declared stages, so that a guessed stage never holds every gate.
- **US-4**: As a Planning agent scoping a document rename, I want the rename procedure and the proposal template to
  name the reference writes it implies, so that the write scope covers them before review.

## 3. Non-Goals

1. **Scope Excluded**: no change to which anchors `devkit workflow envelope commit` supports, to what
   `devkit sync --locked` restores, or to how evaluation holds an envelope with an unknown stage.
2. **Scope Excluded**: the stage check covers `envelope worker` only; `envelope new` and the other kind commands keep
   writing without loading the definition (`CAP-DLV-workflow-envelopes`: a review can be recorded while the definition
   is invalid or missing).
3. **Scope Excluded**: no change to `RULE-document-reference`, `devkit rules fix` or `devkit docs refs`; item 4 is
   wording only.
4. **Scope Excluded**: the duplicate FB-local-render-fix-ignores-worker-write-scope belongs to another unit in
   Development and is left for the Host to close.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The unsupported-anchor fix carries no placeholder
- **Given** `commit_message` called with an anchor id that is not a `SPEC-` or `PROP-` id with a valid slug (for
  example `custom`)
- **When** it raises `EnvelopeCommitInvalidError` (`ENVELOPE_COMMIT_INVALID`)
- **Then** its `[FIX]` is a concrete action (commit the `[TARGET]` envelope with a manual `git commit`) without a
  `<...>` placeholder, and `test_fixes_carry_no_placeholder` and `test_class_fixes_carry_no_placeholder` pass (exit
  `0`)

### [AC-02] The stale local render fix names the locked restore first
- **Given** a workspace whose `.devkit/transient/local-render.json` is missing or stale
- **When** `devkit get-context`, `devkit status` or `devkit playbook get` raises `CONFIG_LOCAL_RENDER_STALE`
- **Then** its `[FIX]` names `uv run devkit sync --locked` first, states that it leaves committed files unchanged,
  and names a plain `uv run devkit sync` only for the case where the locked restore reports `RECEIPT_STALE`
- **And** after `devkit sync --locked` the same workspace's `get-context` succeeds and the tracked files
  (`.devkit/config.toml`, `.devkit/installation.json`, `AGENTS.md`) are byte-identical to before

### [AC-03] An undeclared worker stage is refused at write time
- **Given** a unit bound to a workflow whose definition loads
- **When** `devkit workflow envelope worker --unit <dir> --stage no-such-stage` runs, with authoring flags or as a
  bare skeleton
- **Then** it exits `2` with `ENVELOPE_FLAG_INVALID` (`INPUT_ERROR`), `[TARGET] --stage`, a `[FIX]` that names the
  stages the workflow declares and the `uv run devkit workflow next --unit <dir>` command that names the current one,
  and writes no file
- **And** `--stage -` is still refused with `ENVELOPE_FLAG_INVALID` and `[TARGET] --stage`

### [AC-04] A declared stage and an unloadable definition still write
- **Given** a unit bound to a workflow
- **When** `envelope worker --stage` names a stage the definition declares (an exception stage included), or the
  bound definition cannot be loaded (missing or unreadable)
- **Then** the worker envelope is written as before (exit `0`), so recording a run never depends on a valid definition

### [AC-05] The Living Spec and references match the new fixes
- **Given** `CAP-DIST-context-and-playbooks`, `docs/development/reference/distribution.md` and
  `CAP-DLV-workflow-envelopes`
- **When** a reader looks up `CONFIG_LOCAL_RENDER_STALE` or the `envelope worker --stage` contract
- **Then** the error tables name the locked restore with its `RECEIPT_STALE` exception, and the envelope capability
  states the write-time stage check with its code, fix and lenient fallback

### [AC-06] The rename procedure names its reference writes
- **Given** `CAP-DOCS-document-model` section 3.5 item 5 and the spec bundle's `templates/proposal.md`
- **When** a reader plans a document ID rename
- **Then** the capability states that the rule fix rewrites references in current documents, ADRs, PADRs and
  `specs/**/feedback/` files included, and names `uv run devkit docs refs <old-id> --direction in -n 0` to list them;
  the template's `excludes` example carries a comment that a rename proposal owns those referencing paths
- **And** after `devkit sync` the deployed `.devkit/managed/spec/templates/proposal.md` carries the comment and
  `devkit sync --check` exits `0`

## 5. Assumptions

- The undeclared-stage refusal reuses `ENVELOPE_FLAG_INVALID` with `[TARGET] --stage`, the code and target the
  existing refusal of `-` already uses, so `CAP-DLV-cli-and-output`'s error table needs no new row.
- When the bound definition cannot be loaded, or loads with another id than the unit's workflow, the check is skipped,
  as `--from latest` already does, so a run can still be recorded on a broken definition.
- The stage check applies to the bare `envelope worker` skeleton too, so the stage of every worker envelope written
  by the command is a declared one.

## 6. Source feedback

- `FB-envelope-commit-fix-placeholder-fails-output-contract`: the whole item; AC-01.
- `FB-render-stale-fix-ignores-worker-scope`: the advisory's fix and its documentation (the suggestion's second
  option); AC-02 and AC-05. The first option (a Host refresh in the `spec-delegate` payload) is not taken.
- `FB-worker-envelope-stage-unchecked-at-write`: the whole item; AC-03, AC-04 and AC-05.
- `FB-rename-write-scope-unstated`: the whole item, the optional template comment included; AC-06.
