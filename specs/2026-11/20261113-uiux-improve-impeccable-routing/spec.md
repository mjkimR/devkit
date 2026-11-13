---
id: SPEC-uiux-improve-impeccable-routing
title: Impeccable question and load routing for app-uiux-improve
summary: "Allows a capability-gated Impeccable question relay with every answer user-confirmed, native skill loading and user-session fallback while preserving task route and file authority."
status: in-progress
created: 2026-11-13
related_capabilities: [CAP-DLV-uiux-improvement]
related_usecases: [UC-improve-an-interface-and-user-flow]
workflow: sdd-spec-feature
---

# [SPEC-uiux-improve-impeccable-routing] Impeccable question and load routing

## 1. Problem Statement & Motivation

Interactive Impeccable commands currently require a session the user operates. A resumable child can instead
return questions to the coordinator without answering them, preserving one request while the user decides every
answer. `ADR-impeccable-question-relay` permits this bounded route; `ADR-uiux-task-approved-run` continues to govern
the selected implementation route. `MAT-impeccable-routing-planning` records the observed continuation probe and
unverified native-load behavior. The bundle remains independently installable and content-only.

## 2. User Stories

- **US-1**: As a user improving an interface, I want to confirm the complete Impeccable question round in the
  coordinator conversation and then let the same child continue within its brief.
- **US-2**: As a coordinator, I want an explicit fallback when native loading, continuation or required nested roles
  are unavailable, so I do not infer capabilities or answer for the user.

The affected goal is `UC-improve-an-interface-and-user-flow`.

## 3. Non-Goals

- **Scope Excluded**: plugin installation or enablement changes without the user's existing setup authority,
  plugin-cache loading, upstream prompt vendoring, runtime or host adapters, new feature edges and delivery records.
- **Scope Excluded**: changing the run-model route, Git authority, context-file ownership, edit-list acceptance or
  the pilot hygiene fixes owned by `PROP-uiux-improve-bundle-hygiene`.
- **Scope Excluded**: empirical proof of model obedience, native Impeccable support on either host or quality parity.
  Live checks are best effort for this personal project; unavailable evidence is reported rather than a gate.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Capability-gated relay
- **Given** the user selects Impeccable and native loading plus same-child continuation are observed for the actual host and project
- **When** the coordinator routes an interactive command
- **Then** a read-only question phase precedes explicit user confirmation and the same child's bounded writing phase.

### [AC-02] Every answer remains the user's
- **Given** a question packet with identifiers, suggested answers and source paths/passages for document-derived pre-fills
- **When** the user confirms the complete visible packet or answers each question
- **Then** every answer including every pre-fill is confirmed before dependent writes; silence, omitted answers and gaps-only confirmation do not count.

### [AC-03] Native load failure
- **Given** Impeccable cannot load through the supported host skill mechanism
- **When** the failure is reported
- **Then** the report names observed current-project plugin enablement and native availability, uses the user-operated session fallback and prescribes no plugin-cache load or unauthorized enablement change.

### [AC-04] Continuation and source changes
- **Given** continuation is lost or the relevant brief facts, source state, answers or scope change
- **When** writing would resume
- **Then** lost state uses the user-operated fallback; changed relevant facts refresh the packet and obtain confirmation for affected answers before dependent writes, without a replacement child guessing the transcript.

### [AC-05] New questions and nested capabilities
- **Given** another upstream question appears or shape/critique needs nested roles
- **When** the command continues
- **Then** new questions return for user confirmation; unavailable or unverified nested capabilities use the user-operated session without claimed equivalent inline coverage; live mode stays excluded.

### [AC-06] Retained permissions and writer interval
- **Given** the child is briefed or the user confirms an answer
- **When** it inspects or writes
- **Then** the question phase changes no retained/product files, index or HEAD; PRODUCT.md and DESIGN.md changes still need explicit file/action direction; writing remains brief-bounded and the coordinator makes no concurrent product edits.

### [AC-07] Return and partial execution
- **Given** a child returns a completed or partial result
- **When** the coordinator accepts it
- **Then** it compares the recorded base, retains edit-list and ownership checks and reports unexpected writes or limited attribution without blind replay, unsolicited revert or deletion.

### [AC-08] Consistent independent contract
- **Given** the updated entry, orchestration, guide, capability, use case and decision
- **When** they are reviewed and the bundle is installed
- **Then** they state the same relay/fallback contract, retain independent installation and selected task authority, and distinguish instruction assertions from unverified native host/plugin behavior.

## 5. Verification and Assumptions

The starting worktree already includes completed `SPEC-uiux-improve-run-model`; its route and authority rules remain.
No screen or application UI is changed. Static contract assertions and representative packet/fallback review verify
these instructions, not model obedience. Native Impeccable loading and interactive relay remain unverified on both
hosts; the Codex marker probe establishes only same-child context retention.
