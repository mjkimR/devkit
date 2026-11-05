---
id: SPEC-gitignore-drift-detection
title: Git Tracking Diagnostics for Projected Assets
summary: "Reports unignored and tracked native projections without modifying project ignore rules or the Git index."
status: active
created: 2026-11-05
related_capabilities: [CAP-DIST-sync-and-transactions, CAP-DIST-workspace-ownership]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-gitignore-drift-detection] Git Tracking Diagnostics for Projected Assets

## 1. Problem and User Stories

As a consumer agent, I need sync to identify native projections that may accidentally enter Git, with exact
paths to repair while preserving project-owned neighboring files. The accepted scope keeps root ignore rules
and the Git index under project control.

## 2. Non-Goals

- **Scope Excluded**: automatic ignore/index edits, blanket directory ignores, commit-blocking rules, new settings,
  runtime adapters and a general Git doctor.

## 3. Acceptance Criteria

### [AC-01] Effective ignore coverage
- **Given** native files in the desired installation and a Git workspace.
- **When** sync plans a successful operation, including dry-run or check.
- **Then** untracked files without effective ignore coverage produce one `PROJECTION_NOT_IGNORED` warning;
  ignored files and unrelated project files produce no projection finding. Nested rules and negations follow Git.

### [AC-02] Tracked projections
- **Given** desired or previously owned native files present in the index.
- **When** sync succeeds or previews their removal.
- **Then** one `PROJECTION_TRACKED` warning lists only tracked owned paths even if ignored; previous untracked
  paths being removed do not receive missing-ignore warnings. Neither index nor root ignore files are modified.

### [AC-03] Bounded actionable output
- **Given** more than ten findings in either category.
- **When** notices are rendered as text or JSON.
- **Then** each category reports its total and at most ten sorted path targets with safe exact-path repair
  instructions, including an omitted count. Normal sync succeeds; `--strict` promotes warnings as usual.

### [AC-04] Git and mode boundaries
- **Given** a non-Git workspace, a Git query failure, or a locked sync.
- **When** sync runs.
- **Then** non-Git workspaces skip diagnostics, a failed diagnostic query returns `PROJECTION_GIT_CHECK_FAILED`
  without aborting otherwise successful sync, and successful locked sync reports findings without extra writes.
  Existing stale-receipt and conflict refusals keep precedence.

## 4. Assumptions

Use the desired native file set for ignore coverage and the union of previous and desired native file sets for
index tracking. Inspect actual Git rules, including repository-local exclusions. Batch queries rather than
launching Git per file. These diagnostics extend the existing agent advisory format, with no interactive UI.
