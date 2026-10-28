---
id: SPEC-input-recovery-notices
title: Actionable integration input recovery and milestone notices
summary: "Recover missing integration claims by correcting the same invocation and report inactive milestone assignment without blocking proposal creation."
status: in-progress
created: 2026-10-28
related_capabilities:
  - CAP-INT-mcp-services
  - CAP-DLV-proposal-incubation
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-input-recovery-notices] Actionable integration input recovery and milestone notices

## 1. Problem Statement & Motivation

Session integration refusals direct agents to change source when only invocation claims are missing. Proposal
creation silently assigns drafts to done or dropped milestones. Both observations need actionable output while
preserving the existing authority and lifecycle boundaries.

## 2. Defect Characterization

- **Current behavior**: Missing session claims yield `INTEGRATION_NOT_READY` with a commit-and-prepare-again fix.
  `proposal new --milestone` writes membership for done and dropped milestones without a notice. The source
  feedback records the observed commands and output; regression tests will measure the unchanged production head.
- **Expected behavior and its basis**: The Host-agreed fixes specialize invocation recovery under
  `CAP-INT-mcp-services` and add a nonblocking notice under `CAP-DLV-proposal-incubation`.
- **Behavior to preserve**: Claims remain explicit on prepare and integrate. Source-readiness recovery,
  request digests and authority checks remain enforced. Milestone status and completion assertions remain untouched.
  Invalid milestone IDs fail before writes; planned, active and absent milestones keep existing behavior.
- **Reproduction conditions**: Run the added integration CLI and proposal roadmap regressions against production
  code at `60908741cd4965898ab42851902251a8b7e84d01` before fixing it. Compare their failures with the same tests after
  the fix; no base checkout is required.

## 3. Non-Goals

1. **Scope Excluded**: Persisting claims, changing integration authority or digest validation, reopening milestones,
   resetting assertions, adding approval gates, or implementing Backlog reassignment behavior.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Recover missing session claims on the same command
- **Given** prepare or integrate lacks required session claims
- **When** readiness refuses the command
- **Then** `INTEGRATION_NOT_READY` names `--claims` and retrying the same command with corrected claims, without
  directing source edits, commits or a fresh prepare solely for the missing input.

### [AC-02] Preserve integration checks
- **Given** valid explicit claims or an ordinary source-readiness failure
- **When** integration is prepared or executed
- **Then** existing source-readiness guidance, authority refusal and digest validation retain their behavior.

### [AC-03] Notice for inactive milestone membership
- **Given** a global milestone with status done or dropped, addressed by ID or alias
- **When** a proposal is created with that milestone
- **Then** creation succeeds, canonical membership is written, and `result.notices` carries one stable-code NOTICE
  identifying the milestone and state and advising membership review; the milestone bytes remain unchanged.

### [AC-04] Preserve proposal validation and CLI semantics
- **Given** a planned, active, absent or invalid milestone, or an inactive milestone under JSON/text and `--strict`
- **When** proposal creation runs
- **Then** ordinary membership adds no inactive notice, invalid membership writes nothing, and inactive membership
  succeeds with its notice even under `--strict` through the existing output boundaries.

## Source feedback

- `FB-integrate-asks-for-a-new-request-when-claims-are-missing`: specialize missing-claims recovery; claims stay explicit.
- `FB-proposal-new-accepts-a-done-milestone`: surface done/dropped membership through a notice only.
