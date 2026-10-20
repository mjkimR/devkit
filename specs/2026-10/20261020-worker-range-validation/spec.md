---
id: SPEC-worker-range-validation
title: One-command worker result inspection for orchestrated units
summary: "Collects existing worker-result checks and reviewer diff information using committed records, with explicit input overrides and no new approval gate."
status: completed
created: 2026-10-20
related_capabilities:
  - CAP-DLV-delivery-workflows
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-worker-range-validation] One-command worker result inspection for orchestrated units

## 1. Problem Statement & Motivation

Hosts repeat range, scope, cleanliness, envelope, rules and workflow checks after each worker turn. Reviewers need
compared heads and changed paths. One read-only command collects this evidence under
`ADR-informational-range-inspection-reuses-existing-checks`.

## 2. User Stories

- **US-1**: As an orchestrating agent, I want one inspection result so I can assess a worker's committed range and
  give independent reviewers its actual changed paths.

## 3. Non-Goals

- **Scope Excluded**: approval gates, enforcement, scope registration, new envelope fields, automatic scope
  expansion, repairs, merges, environment refresh, synchronization or retries.
- **Scope Excluded**: detecting base drift against the Host's saved state and inferring ownership of link repairs.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Derive committed inputs and allow replacements
- **Given** an activity worktree with committed unit records
- **When** `devkit spec worker inspect` runs
- **Then** it derives unit, returned head, previous accepted base, declared scope and registered base checkout
  exactly as `ADR-informational-range-inspection-reuses-existing-checks` specifies; every value has provenance.
  Each explicit flag replaces only its input; repeated `--scope` or a newline-delimited `--scope-file` replaces
  the entire derived scope. Uncommitted records cannot affect derivation.

### [AC-02] Preserve blocked-range start
- **Given** a previous worker envelope whose added commit is blocked by unresolved problem records
- **When** the base is derived
- **Then** it uses their common `diff_scope.base`; missing or conflicting bases yield
  `WORKER_BASE_UNRESOLVED` and exit 2. A resolved previous result uses its envelope's added commit.

### [AC-03] Collect existing checks and reviewer information
- **Given** valid unit and compared commit inputs
- **When** inspection runs
- **Then** it reports ancestry, HEAD equality, changed paths, outside-scope paths, worktree status, envelope
  validation including blocked and pending questions, cumulative rules and workflow stage as pass/fail/not-run.
  Rules run only when HEAD equals the returned head. Base checkout HEAD and dirty paths are informational.
  Existing check codes and actions remain available in the result.

### [AC-04] Distinguish negative results and unavailable checks
- **Given** a check failure, unavailable scope/check, or unresolved required input
- **When** inspection runs
- **Then** exit is 1 for at least one failed check, 0 otherwise, and 2 for invalid invocation, invalid Git refs,
  a non-worktree, or unresolved unit/head/base. The required-input codes are `WORKER_UNIT_UNRESOLVED`,
  `WORKER_HEAD_UNRESOLVED`, `WORKER_BASE_UNRESOLVED`, with actions to pass the corresponding flag.
  Unavailable checks are not-run with their cause and a notice, not negative results.

### [AC-05] Read-only agent output and guidance
- **Given** text or `--format json` output
- **When** inspection completes
- **Then** stdout contains sentinel lines or exactly one JSON object with inputs, scope provenance, base, head,
  changed_paths and per-check results; outside_scope is absent when unavailable. No files, records or Git state
  are changed. Delegation guidance supplies this evidence to reviewers and retains the Host's scope authority
  and existing acceptance decisions.

## 5. Assumptions and Premise Check

The current base retains the CLI mounting point, task-boundary parser, committed envelope collector and worktree
Git markers described by the accepted ADR. Implementations can call existing read-only CLI checks and preserve
both structured results and advisory stderr. No new dependency or contract exception is required.

## 6. Source feedback

- `FB-reconcile-reviewer-no-diff-list`: include compared commits and changed-file information in reviewer payloads.
- `FB-worker-scope-misses-link-repairs` and `FB-handoff-premise-drift-unreported` retain their separate scope;
  this implementation does not resolve them.
