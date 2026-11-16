---
id: SPEC-open-feedback-fixes
title: Fixes for four open feedback items
summary: Fixes the runtime-view journal ordering, scout web search, handoff boundary carry-over of the removed proposal directory, and the docs resolve path anchor wording.
status: in-progress
created: 2026-11-16
related_capabilities: []
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-open-feedback-fixes] Fixes for four open feedback items

## 1. Problem Statement & Motivation

Four open feedback items report small defects where a document, a role contract, a handoff skeleton or a command
help text disagrees with the contract it restates or serves. Each misleads the next agent that reads it: a runtime
diagram that orders the journal after the writes, a scout that cannot discover external sources its procedure
admits, a handoff skeleton whose boundaries name a path the handoff removed, and a resolver help that does not say
which root its paths are relative to.

## 2. Defect Characterization

- **Current behavior**:
  1. `ARCH-06-runtime-view` §1 draws "Write/update managed files & projections" before "Record written paths &
     previous state" inside the per-asset loop.
  2. The scout role contract's Claude Code host lists `tools: [Read, Grep, Glob, WebFetch, Bash]`, without
     `WebSearch`, although its procedure step 4 admits external material.
  3. `devkit spec proposal handoff` carries every `boundaries.owns` entry into the `plan.md` Planned Boundaries,
     the `tasks.md` `_Boundary` and a bugfix spec's carried `Target Area & Boundaries` notes, including the
     handed-off proposal's own path (`docs/proposals/PROP-<slug>/`), which the same handoff removes.
  4. `devkit docs resolve --help` reads "Print the path of each document ID." without the root anchor.
- **Expected behavior and its basis**:
  1. The journal is written and flushed before any disk change (`CAP-DIST-sync-and-transactions` §3 item 3;
     `apply_changes` in the distribution installation transaction).
  2. The scout can search for external sources when `task_goal` asks for them and stays read-only (the scout
     procedure step 4).
  3. The boundaries a handoff writes name only paths the Development can write; the removed proposal path is not
     one (`CAP-DLV-proposal-lifecycle` §3 step 1, refined by this spec).
  4. Output paths are workspace-relative (`CAP-DOCS-document-lookup` §3.1 item 1); the help says so.
- **Behavior to preserve**: every other `boundaries.owns` entry, including a sibling proposal path that shares the
  slug as a prefix, is still carried in order (`test_carries_the_proposal_body`, `test_binds_the_proposal_workflow`);
  an `owns` left empty falls back to `target_area`; the resolver output is unchanged (`test_resolve`); the scout
  keeps no Write or Edit tool (`test_support_roles_shell_access`); the runtime view stays a system-level summary.
- **Reproduction conditions**: read the named diagram and the scout frontmatter; hand off a proposal whose
  `boundaries.owns` lists its own directory (`test_carries_the_proposal_body`, extended); run
  `devkit docs resolve --help` through `CliRunner`.

## 3. Non-Goals

1. **Scope Excluded**: The full sync transaction algorithm in the runtime view, any change to the resolver output
   format, and any other role's tool set.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Runtime view orders the journal first
- **Given** `ARCH-06-runtime-view` §1
- **When** a reader follows the synchronization sequence
- **Then** the journal of pending changes and previous state is written before the loop that writes managed files
  and projections, and no journal step follows a file write inside that loop

### [AC-02] Scout can search the web read-only
- **Given** the scout role contract
- **When** its Claude Code host tools are read
- **Then** they include `WebSearch` and `WebFetch` and include neither `Write` nor `Edit`

### [AC-03] Handoff drops the handed-off proposal's own path
- **Given** an accepted proposal bundle whose `boundaries.owns` lists `docs/proposals/PROP-<slug>/`
- **When** `handoff_proposal` runs
- **Then** neither the `plan.md` Planned Boundaries nor the `tasks.md` `_Boundary` names that path

### [AC-04] Handoff keeps every other boundary
- **Given** the same proposal also owns a sibling `docs/proposals/PROP-<slug>-other/` and two other paths
- **When** `handoff_proposal` runs
- **Then** the sibling and the other paths are carried in their declared order

### [AC-05] Resolve help names the workspace-relative anchor
- **Given** the `devkit docs resolve` command
- **When** `devkit docs resolve --help` runs
- **Then** it exits 0 and prints "Print the workspace-relative path of each document ID."

## 5. Source feedback

- `FB-runtime-journal-ordering` (AC-01)
- `FB-scout-lacks-web-search` (AC-02)
- `FB-handoff-skeleton-keeps-proposal-boundary` (AC-03, AC-04)
- `FB-resolve-package-path-anchor` (AC-05)

## 6. Assumptions

- The handed-off proposal's own path is matched exactly: its bundle directory with or without a trailing `/`, or
  its single file; a prefix match would drop sibling proposals.
- `CAP-DLV-proposal-lifecycle` §3 step 1 states the exclusion, since the carried boundaries are its contract.
