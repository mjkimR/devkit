---
id: SPEC-uiux-upstream-fallbacks
title: Handle observed Impeccable limitations in the UIUX skill
summary: Add bounded local guidance for false UI detection, unavailable delegated autonomy probes and unsupported audit persistence, preserving existing authority and native skill routes.
status: planned
created: 2026-11-13
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-uiux-upstream-fallbacks] Handle observed Impeccable limitations in the UIUX skill

## 1. Problem Statement & Motivation

<Describe the problem, who has it and why it matters now.>

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Handle observed Impeccable limitations in the UIUX skill so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## Agreed scope

Compensate for the observed upstream limitations in the local app-uiux-improve skill where useful. A negative visual detector is not proof that no UI exists: inspect the actual target/code/branch build and report detection limits without promising --target fixes it. Brief delegated children with actual capabilities and bounded stop conditions; an unavailable autonomy probe is reported, never claimed passed or overridden, and existing user-session/authorized-inline fallbacks apply. If audit persistence is unavailable, return audit results in the session report, inspect installed supported interfaces before persistence, and do not invent/retry unsupported commands or install/change tools without the existing explicit request.

Preserve selected-route/Git/host authority, explicit Impeccable selection, native loading, every-answer confirmation, existing file ownership and attribution. Add no runtime, upstream patch, automatic installation, cache load route or external send. Empirical native Impeccable trials are best effort, not acceptance gates.

## Source feedback

- `FB-impeccable-context-target-no-visual-implementation`
- `FB-impeccable-autonomy-probe-in-subagent`
- `FB-impeccable-audit-storage-write-missing`

The user selected local compensation rather than a retained upstream backlog. When useful local work is implemented and verified, link the source records as promoted to this completed mitigation work without claiming an upstream runtime fix; dismiss a record with rationale if no useful local change is needed. Leave no external submission work. No dependencies on another active Unit are declared.
