---
id: SPEC-remove-unused-cli-options
title: Remove unused CLI options
summary: 'Removes CLI options no documented workflow or caller uses: worktree finish --local-only, host status --host, rules check/fix --summary-only, workflow next --workflow, workflow handoff --date and docs list --query.'
status: in-progress
created: 2026-11-11
related_capabilities:
  - CAP-WT-task-worktrees
  - CAP-DLV-cli-and-output
  - CAP-DLV-workflow-definitions
  - CAP-DOCS-document-lookup
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-remove-unused-cli-options] Remove unused CLI options

## 1. Problem Statement & Motivation

Six CLI options are accepted but no documented workflow, bundle guidance, script or caller uses them. Each one widens
the command surface an agent reads in `--help`, the reference documents and the tests that keep it working:

- `devkit worktree finish --local-only` has changed nothing since `finish --merge` was retired
  (`ADR-single-local-landing-route`), which kept it accepted only because guidance still named it.
- `devkit host status --host` accepts only `codex`, the one supported host adapter.
- `devkit rules check|fix --summary-only` replaces findings with per-rule counts; nothing runs it.
- `devkit workflow next --workflow` evaluates a unit against another definition than its binding; agents follow the
  binding, and `bind --workflow` changes it.
- `devkit workflow handoff --date` back-dates the handoff history; the history records the day the handoff ran.
- `devkit docs list --query` duplicates the ID and title lookup that `devkit docs search` does.

devkit has no external consumers except `devkit.advisory` and the `devkit-cli` package, neither of which passes these
options, so the options are removed outright: no shim, deprecation period or hidden alias. A removed option is an
unknown option.

## 2. User Stories

- **US-1**: As an agent reading devkit help and references, I want only options that change behavior, so that I do not
  pass flags that do nothing or duplicate another command.
- **US-2**: As a maintainer, I want each removed option's code, tests and documentation gone together, so that no
  guidance names an option the CLI rejects.

## 3. Non-Goals

1. **Scope Excluded**: the `playbook search` ranking flags; they stay for parity with `docs search`.
2. **Scope Excluded**: any other option, command, output line or exit code. `[BOUND_ELSEWHERE: ...]` keeps its
   rendering for library callers; `[RULE_COUNTS: ...]` goes with `--summary-only`, the only path that printed it.
3. **Scope Excluded**: the hidden `devkit host hook --host` option: generated hook commands pass it.
4. **Scope Excluded**: `handoff --workflow` (the candidate to continue with), `new --date`, `bind --workflow` and the
   library parameters `Workspace.resolve_unit(unit, workflow)` and `apply_handoff(plan, when=...)`.
5. **Scope Excluded**: help text rewording beyond the removals; the `worktree` group docstring is edited by another
   work item.

## 4. Acceptance Criteria & Behavioral Contracts

Every removed option is refused by click before the command runs: exit `2`, stderr containing
`No such option '<option>'`, and no file written.

### [AC-01] `worktree finish --local-only` is unknown
- **Given** a branch the base already contains, with its worktree
- **When** `devkit worktree finish <branch> --local-only` runs
- **Then** it exits `2` with `No such option '--local-only'` on stderr and the worktree and branch remain
- **And** `devkit worktree finish <branch>` removes them, makes no fetch, push or `ls-remote` call and exits `0`

### [AC-02] Guidance names plain `finish` for the remaining cleanup
- **Given** the spec bundle sources, `guides/`, `docs/capabilities/` and `docs/development/reference/`
- **When** `git grep -n -- --local-only -- packages docs guides scripts justfile ':!docs/materials'` runs
- **Then** it lists only decision text and the test asserting the refusal, and every remaining-cleanup instruction reads
  `devkit worktree finish <branch>` with its existing wording kept

### [AC-03] `ADR-single-local-landing-route` is superseded in part
- **Given** the accepted clause that `--local-only` stays accepted and the follow-up to retire it
- **When** the decision records are read
- **Then** a new ADR states `Supersedes in part` for `ADR-single-local-landing-route` naming those clauses, the
  earlier ADR stays `accepted` with the matching `Superseded in part by` line, and `devkit rules check` on both
  reports no violation

### [AC-04] `host status --host` is unknown
- **Given** a devkit project
- **When** `devkit host status --host codex` runs
- **Then** it exits `2` with `No such option '--host'` on stderr
- **And** `devkit host status --format json` reports `"host": "codex"` and exits `0` or `1` as before
- **And** `devkit host hook --host codex --asset <asset>` still dispatches

### [AC-05] `rules check|fix --summary-only` is unknown
- **Given** a workspace with findings
- **When** `devkit rules check --summary-only` or `devkit rules fix --summary-only` runs
- **Then** each exits `2` with `No such option '--summary-only'` on stderr
- **And** `devkit rules check` prints one `[VIOLATION: ...]` per finding and its `[SUMMARY: ...]` line as before

### [AC-06] `workflow next --workflow` is unknown
- **Given** a unit
- **When** `devkit workflow next --unit <dir> --workflow <id>` runs
- **Then** it exits `2` with `No such option '--workflow'` on stderr
- **And** `next --anchor <file>` still selects among ambiguous anchors, and `bind --workflow <id>` still reports
  `ANCHOR_MISMATCH`, `UNIT_NOT_FOUND` and `WORKFLOW_NOT_BINDABLE` as before

### [AC-07] `workflow handoff --date` is unknown; the history takes today
- **Given** a completed unit with an eligible candidate
- **When** `devkit workflow handoff --unit <dir> --workflow <id> --date 2026-10-13` runs
- **Then** it exits `2` with `No such option '--date'` on stderr and the anchor is unchanged
- **And** without `--date` the handoff exits `0` and its `workflow_history` entry has `completed: '<today>'`

### [AC-08] `docs list --query` is unknown
- **Given** an indexed workspace
- **When** `devkit docs list --query <text>` runs
- **Then** it exits `2` with `No such option '--query'` on stderr
- **And** `CAP-DOCS-document-lookup` points ID and title lookup at `devkit docs search`, and the other `list` filters
  behave as before

## 5. Assumptions

- The intent counted six workflow integration test files passing `--date`; only two pass `handoff --date` (the others
  pass `new --date`, which stays). Neither needs a fixed handoff date, so both assert on today.
- `[BOUND_ELSEWHERE: ...]` is unreachable from the CLI once `next --workflow` is gone; the library still produces it
  through `Workspace.resolve_unit(unit, workflow)`, so the renderer, its JSON field and the devkit entry skill text
  stay, and its test moves to the library.
- `InspectHost` is called with `SUPPORTED_HOSTS[0]`, the only supported host.
- One new ADR records the no-shim removal of all six options, because it changes accepted contracts in four packages
  and supersedes one clause of an accepted ADR.
