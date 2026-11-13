---
id: SPEC-uiux-upstream-fallbacks
title: Handle observed Impeccable limitations in the UIUX skill
summary: "Add local guidance for false UI detection, unavailable delegated autonomy probes and unsupported audit persistence while preserving native skill loading and consumer authority."
status: completed
created: 2026-11-13
related_capabilities: [CAP-DLV-uiux-improvement]
related_usecases: [UC-improve-an-interface-and-user-flow]
workflow: sdd-spec-feature
---

# [SPEC-uiux-upstream-fallbacks] Handle observed Impeccable limitations in the UIUX skill

## 1. Problem Statement & Motivation

Three upstream observations can misdirect a delegated UI/UX improvement: a detector misses a monorepo UI, a child
cannot perform an autonomy probe, or a suggested audit persistence command does not exist. The local skill can guide
honest reporting and supported continuation without fixing upstream runtime behavior. This work extends
`CAP-DLV-uiux-improvement` and `UC-improve-an-interface-and-user-flow` within their existing authority boundaries.

## 2. User Stories

- **US-1**: As a coordinator, I want to inspect actual UI evidence after negative detection so that an existing
  interface is still considered within the authorized goal.
- **US-2**: As a coordinator, I want capabilities and stop conditions in the delegation brief so that unavailable
  required probes stop dependent work and use an authorized route.
- **US-3**: As a developer, I want audit findings returned even without supported persistence so that an unsupported
  command does not trigger invented commands, installations or unauthorized file changes.

## 3. Non-Goals

1. **Scope Excluded**: upstream runtime fixes, external submissions or retained upstream follow-up work.
2. **Scope Excluded**: new runtimes, installers, automatic invocation, cache-loading routes, dependencies or feature edges.
3. **Scope Excluded**: changes to selected task routes, native loading, every-answer confirmation, host permissions,
   Git authority, context-file ownership or attribution requirements.
4. **Scope Excluded**: live upstream trial gates, native enforcement claims or claims that instruction tests prove model behavior.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Treat negative visual detection as advisory

- **Given** Impeccable reports `hasVisualImplementation=false` for a consumer target.
- **When** the coordinator evaluates the target.
- **Then** the installed skill directs inspection of the actual target, UI code and executable local branch build,
  reports detection and coverage limits, and promises neither absent UI nor correction by `--target`.

### [AC-02] Report an unavailable autonomy probe and preserve required gates

- **Given** a delegated Impeccable session with observed capabilities and bounded stop conditions.
- **When** `AUTONOMY_DIRECTIVE_CHECK` requires a live probe that the child cannot run.
- **Then** the skill requires disclosure and stopping dependent work rather than claiming a pass or substituting the
  brief for upstream requirements; continuation uses the existing user-operated route or authorized inline work.
  Native loading, every-answer confirmation and host permissions remain required on their applicable routes.

### [AC-03] Return audit results without inventing persistence

- **Given** installed Impeccable has no supported audit persistence command.
- **When** persistence would be attempted.
- **Then** the skill requires inspecting installed supported help/interface first and returning findings in the
  session report when unavailable, without inventing or retrying `audit-storage write`, installing tools or writing
  unrequested files.

### [AC-04] Ship conditional guidance without widening authority

- **Given** a consumer selecting app-uiux-improve without delivery packages.
- **When** assets are synchronized from an installed wheel.
- **Then** the entry links the mitigation reference with a read condition, the complete reference is projected,
  and existing selection, routing, native loading, answer confirmation, Git and context-file boundaries still pass
  their instruction and distribution checks.

### [AC-05] Close the three observations as verified local mitigation

- **Given** the three Source feedback records selected by the user for local compensation.
- **When** this local guidance and its checks are complete.
- **Then** each record is promoted with a Disposition linking this completed mitigation and verification, explicitly
  says upstream runtime was not fixed, and leaves no open upstream submission or follow-up task.

## 5. Assumptions and Outcome Measurement

The observations describe historical upstream behavior; no installed version or live-supported host is assumed.
Use a conditional reference linked directly from the entry because orchestration.md is 12,280 of 12,288 bytes.
The reference adds exceptional handling without splitting or weakening the existing delegation procedure.

Baseline: accepted head 5cab6156a60de1a2a2845e38fc19bda92961c90e. Measure explicit guidance for the three failure cases
in that committed bundle using `git show`, then compare the changed bundle without checking out the base. The
measurement is instruction coverage, not a model-obedience or upstream-runtime measurement. Native trials are best
effort and are not acceptance gates.

## Source feedback

- `FB-impeccable-context-target-no-visual-implementation`
- `FB-impeccable-autonomy-probe-in-subagent`
- `FB-impeccable-audit-storage-write-missing`

The user selected local compensation rather than a retained upstream backlog. Promote each useful verified local
mitigation to this work; dismiss with rationale only if no useful change is needed. Do not claim an upstream fix or
create external submission work. No dependencies on another active Unit are declared.
