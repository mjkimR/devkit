---
id: SPEC-list-terminal-statuses-historical
title: Terminal statuses are historical in document browsing
summary: Treats terminal statuses of feedback, decisions and proposals as historical, so devkit spec list and search hide them unless --history is passed, and list reports how many it hid.
status: completed
created: 2026-10-26
related_capabilities:
  - CAP-DOCS-document-lookup
  - CAP-DOCS-document-model
  - CAP-DOCS-document-search
related_usecases:
  - UC-find-the-right-documents
workflow: sdd-spec-feature
---

# [SPEC-list-terminal-statuses-historical] Terminal statuses are historical in document browsing

## 1. Problem Statement & Motivation

`devkit spec list feedback` in this repository prints 170 items of which 10 are open; `devkit spec list decision`
prints 53 ADRs of which 7 are superseded. Settled items crowd the current ones out of the default page, so an agent
either pays the context for history it does not need or must remember `--status open` on every call. Completed spec
bundles and done or dropped milestones already follow the historical rule of `CAP-DOCS-document-model`: hidden from
browsing and search unless `--history` is passed, still resolvable. Terminal statuses of feedback, decisions and
proposals are the same kind of history and follow no such rule.

Non-Goal 1 of `SPEC-feedback-list-filters` and the "Feedback defaults" scope note of `CAP-DOCS-document-lookup`
refused a status default for one kind, because `list feedback` and `list feedback spec` would select differently
and items hidden without a trace would drop out of reports and the hygiene pass. A uniform historical rule keyed to
each kind's terminal statuses selects alike whatever kinds are named, and a hidden count on every page leaves a
trace. `ADR-terminal-statuses-are-historical` records this reversal.

## 2. User Stories

- **US-1**: As an agent browsing documents, I want settled feedback, superseded decisions and rejected proposals
  hidden by default, so that the default page shows what is current (`UC-find-the-right-documents`).
- **US-2**: As an agent that needs settled items, I want `--history` or a `--status` naming their status to show
  them, so that the history stays one flag away.
- **US-3**: As an agent reading a page, I want to be told how many matching documents were hidden as historical and
  how to see them, so that nothing disappears without a trace.

## 3. Non-Goals

1. **Scope Excluded**: changing what the rules check. A document historical only through its terminal status stays
   checked by every rule on whole-workspace runs; only browsing and search hide it.
   - **Rationale**: the agreed change is browsing; terminal-status documents still carry rule-checked lifecycle
     fields (dispositions, supersession links).
2. **Scope Excluded**: a hidden count for `devkit spec search`; search returns a bounded number of ranked hits and
   has no page line.
3. **Scope Excluded**: terminal statuses for other kinds (proposal decisions, specs, milestones beyond today's rule)
   or a configurable vocabulary.
   - **When to Reconsider**: when another kind's settled items crowd its default listing.
4. **Scope Excluded**: changes to `resolve` or `refs`; historical IDs stay resolvable and their references
   queryable.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Terminal statuses are hidden by default
- **Given** a workspace with feedback whose statuses are open, resolved, promoted, dismissed and forwarded, a
  decision with status accepted and one with status superseded, and a proposal with status draft and one with
  status rejected
- **When** `devkit spec list feedback decision proposal` runs
- **Then** it exits `0` and lists only the open feedback, the accepted decision and the draft proposal

### [AC-02] `--history` shows them
- **Given** the workspace of AC-01
- **When** `devkit spec list feedback decision proposal --history` runs
- **Then** every document of AC-01 is listed and `[PAGE: ...]` carries `hidden=0`

### [AC-03] A listed status shows its documents whatever their history
- **Given** the workspace of AC-01 plus a completed spec bundle
- **When** `devkit spec list feedback --status resolved` runs without `--history`, and then
  `devkit spec list spec --status completed`
- **Then** the first lists the resolved feedback and the second the completed spec, each with `hidden=0`

### [AC-04] The page reports what it hid
- **Given** the workspace of AC-01
- **When** `devkit spec list feedback` runs
- **Then** the last lines are `[PAGE: total=1 offset=0 limit=20 count=1 next=- hidden=4]` and
  `[HISTORY_CMD: devkit spec list feedback --history]`; with `--format json` the object carries `"hidden": 4`

### [AC-05] No hint without hidden documents
- **Given** a workspace whose feedback is all open
- **When** `devkit spec list feedback` runs
- **Then** `[PAGE: ...]` carries `hidden=0` and no `[HISTORY_CMD: ...]` line is printed

### [AC-06] The rule holds for every kind selection and for search
- **Given** the workspace of AC-01
- **When** `devkit spec list` runs without KIND, and `devkit spec search` runs for a query matching the resolved
  feedback
- **Then** `list` hides the same documents as AC-01 with `hidden=` counting them, and `search` returns no hit for a
  terminal-status document unless `--history` is passed

### [AC-07] Historical IDs stay resolvable
- **Given** the workspace of AC-01
- **When** `devkit spec resolve` runs on the superseded decision's ID
- **Then** it prints its `[DOCUMENT: ...]` line and exits `0`

### [AC-08] Call sites that need settled items pass `--history`
- **Given** the bundled skills and playbooks that list or search documents
- **When** a step needs superseded decisions or rejected proposals (ADR compaction, milestone completion review)
- **Then** its command passes `--history`, and the scout's `--history` hint names terminal statuses

## 5. Assumptions

- The terminal statuses are a fixed table per kind: feedback `resolved`, `promoted`, `dismissed`, `forwarded`;
  decision `superseded`; proposal `rejected`, compared case-insensitively.
- A given `--status` replaces the default hiding for every historical document (completed bundles and done or
  dropped milestones included), so a named status is never empty only through history.
- The hint is a stdout sentinel `[HISTORY_CMD: devkit spec ...]` repeating the command with `--history`, like
  `[NEXT_CMD: ...]`, rather than a notice: a notice would repeat on almost every call and change `--strict` exits.
- `hidden` counts the documents that match every other filter and were left out only as historical; it is `0` with
  `--history` or `--status`. It is printed on `list` pages only, so the `refs` page line is unchanged.
- `--status open` call sites stay as written: they remain correct and state the selection explicitly.
