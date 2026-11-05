---
id: SPEC-gitignore-drift-detection
title: Git Tracking Diagnostics for Projected Assets
summary: Detects missing ignore coverage and tracked devkit projections during sync without modifying project ignore rules or the Git index.
status: planned
created: 2026-11-05
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-gitignore-drift-detection] Git Tracking Diagnostics for Projected Assets

## 1. Problem Statement & Motivation

Handed off from proposal PROP-gitignore-drift-detection on 2026-11-05.
- Target Docs Blueprint: `PROP-gitignore-drift-detection-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

Pilot adoption exposed generated native agent files in Git status and accidental tracking. Native projection
roots also contain project-owned settings and instructions. CAP-DIST-workspace-ownership leaves root ignore
rules and the Git index under project ownership; sync already seeds ignores for managed and transient content
inside `.devkit/.gitignore`.

The retained scope is a read-only diagnostic during sync. It should identify the actual devkit-deployed native
paths that lack effective ignore coverage or are already tracked, then give precise remediation.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Git Tracking Diagnostics for Projected Assets so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- Which receipt and planned projection records identify the deployed paths without including neighboring
  project-owned files, including removed or changed projections?
- How should Git ignore checks distinguish missing coverage from already tracked files, including negations,
  nested ignore files and a workspace without Git?
- How can sync return bounded notices with stable codes and actionable paths without repeating every generated
  file in the output? Planning must settle dry-run, check and locked-mode behavior.

### 3. Proposed Design & Impact

- Check only actual devkit-owned native projection paths, using installation records and the sync plan.
- Distinguish missing effective ignore coverage from files already in the Git index.
- Return notices with the relevant paths and precise ignore or untracking instructions. Preserve the standard
  notice and `--strict` behavior defined by ARCH-08-1-agent-output.
- Keep the implementation in distribution so distribution-only installations receive the diagnostic.
- Preserve the existing `.devkit/.gitignore` behavior.

#### Non-Goals

- No automatic root `.gitignore` edits, managed ignore block or new opt-out setting.
- No Git index writes or automatic `git rm --cached` fixer.
- No blanket ignore of `.agents/`, `.claude/` or `.codex/`.
- No default commit-blocking rule or parallel governance implementation.

### 4. Validation & Priority

Implement this diagnostic before broader onboarding conveniences. Verify an ignored untracked projection,
a projection without ignore coverage, an already tracked projection and a neighboring project-owned file.
Include nested/negated ignore cases and a workspace without Git. Assert that root ignore files and the Git
index remain unchanged, and that notice output stays bounded.

