---
id: SPEC-uiux-improve-run-model
title: Task-approved UI/UX runs outside the consumer workflow
summary: "Offers explicitly approved per-task UI/UX work outside the consumer workflow while retaining constraints, host permissions, project checks and separate Git authority."
status: in-progress
created: 2026-11-13
related_capabilities: [CAP-DLV-uiux-improvement]
related_usecases: [UC-improve-an-interface-and-user-flow]
workflow: sdd-spec-feature
---

# [SPEC-uiux-improve-run-model] Task-approved UI/UX runs outside the consumer workflow

## 1. Problem Statement & Motivation

The consumer workflow is mandatory for every implementation in the existing skill. The owner wants the skill to
announce a lighter route and obtain explicit task approval, while preserving the workflow when the user chooses it.
`ADR-uiux-task-approved-run` settles the narrow authority change; the target draft
`PROP-uiux-improve-run-model-target` maps the retained contracts. The pilot evidence in
`MAT-uiux-improve-second-pilot` does not establish equal defect detection.

## 2. User Stories

- As a product owner, I want an explicitly approved outside-workflow run without changing repository policy.
- As an AI coding agent, I want clear remaining permission, verification, scope and documentation boundaries.
- As a consumer, I want the bundle to work without delivery packages or mandatory delivery records.

The affected user journey is `UC-improve-an-interface-and-user-flow`.

## 3. Non-Goals

- **Scope Excluded**: changing Impeccable question/load routing, pilot hygiene fixes, configured development approach,
  host controls, distribution runtime or package dependencies.
- **Scope Excluded**: editing consumer OOUX documents during a skill run, granting implicit Git authority, introducing
  mandatory role counts or retained delivery records, or proving model obedience or comparative UX quality.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Explicit route choice precedes writes
- **Given** a bounded improvement request without an exact prior route instruction.
- **When** the skill begins implementation work.
- **Then** it announces that it proceeds outside the repository development workflow and process guidelines and obtains explicit task approval or follows the workflow the user chooses, before product edits or write-capable delegation.

### [AC-02] Reuse authority and wait without an answer
- **Given** an exact route instruction already supplied, or no route approval and no answer/channel.
- **When** the entry reaches its route choice.
- **Then** it reuses existing authority without an identical question; otherwise dependent writes wait and useful read-only inspection is preserved.

### [AC-03] Both routes retain their obligations
- **Given** either authorized route.
- **When** inline work, accepted Impeccable edits or requested setup/cleanup proceeds.
- **Then** outside-workflow work uses the improvement loop without workflow records; workflow-selected work completes its required steps and reviews; both preserve product constraints and host permissions, and route choice changes no project policy.

### [AC-04] Git effects require their own authority
- **Given** approved work with no authority for remaining commit, integration or publication effects.
- **When** the verified result is ready for those effects.
- **Then** the coordinator asks once for the named remaining effects, reuses any exact prior authority, and performs none before authority arrives.

### [AC-05] Scope growth requires a decision
- **Given** an approved goal and user constraints.
- **When** proposed work adds surfaces or behavior beyond that goal or changes a user constraint.
- **Then** dependent work waits for a new user decision; an in-goal file addition or implementation choice alone is not scope growth.

### [AC-06] Checks and optional reviews remain explicit
- **Given** a requested implementation.
- **When** it finishes on either route.
- **Then** applicable project checks and before/after interface verification are reported with missing coverage; the bundle adds no mandatory independent review, while the selected workflow's required reviews remain required.

### [AC-07] Stale documentation is a separate follow-up
- **Given** an accepted change makes a consumer OOUX or UX statement stale.
- **When** the coordinator reports the result.
- **Then** it names the document, affected statement and concrete next action through the documentation process where present or a separate task otherwise; it edits none and creates no follow-up record without a separate request.

### [AC-08] Existing delegation and ownership remain bounded
- **Given** optional local roles, Impeccable or requested setup/cleanup.
- **When** work runs under the selected route.
- **Then** selection, question/load routing, context-file permission, recorded-base acceptance, coordinator pause and host-refusal boundaries stay intact.

### [AC-09] Installation remains independent and selection-neutral
- **Given** installed dist/catalog wheels without agent, docs or spec packages.
- **When** the bundle is selected and removed/reselected.
- **Then** the skill includes both route instructions, changes no configured approach, creates no delivery records and preserves consumer-owned artifacts.

## 5. Verification limits

Instruction assertions and installed-consumer E2E establish the shipped text and distribution behavior. Live host,
consumer and model trials are best effort and no comparative quality or performance outcome is claimed.
