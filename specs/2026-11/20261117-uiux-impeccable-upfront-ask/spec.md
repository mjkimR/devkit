---
id: SPEC-uiux-impeccable-upfront-ask
title: Ask about Impeccable at the start of app-uiux-improve
summary: app-uiux-improve asks the user first whether to use Impeccable unless the request already says so; silence keeps the inline track.
status: completed
created: 2026-11-17
related_capabilities: [CAP-DLV-uiux-improvement]
related_usecases: [UC-improve-an-interface-and-user-flow]
workflow: sdd-spec-feature
---

# [SPEC-uiux-impeccable-upfront-ask] Ask about Impeccable at the start of app-uiux-improve

## 1. Problem Statement & Motivation

The Impeccable track runs only after the user selects it, and an installed Impeccable merely permits an offer
(`ADR-impeccable-session-authority`). In practice the coordinator rarely makes that offer, so users who would want
Impeccable never hear the choice, and a late offer arrives after framing and design work already took the inline
path. The track stays optional; the change makes the choice explicit at the start of every request that does not
already state it.

## 2. User Stories

- **US-1**: As a user invoking app-uiux-improve, I want to be asked first whether to use Impeccable, so that I can
  choose the track before any design work starts.
- **US-2**: As a user who already said whether to use Impeccable, I want no repeated question.

The affected goal is `UC-improve-an-interface-and-user-flow`.

## 3. Non-Goals

1. **Scope Excluded**: making Impeccable the default track, installing it, or detecting it with new tooling.
2. **Scope Excluded**: changing the brief, routing, question relay, acceptance, setup/cleanup authority or the task
   route approval.
3. **Scope Excluded**: asking again later in the same request after the user answered.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Ask first when the request is silent
- **Given** an app-uiux-improve request that states neither use nor non-use of Impeccable
- **When** the coordinator starts the request
- **Then** its first question round asks whether to use Impeccable for this request, says whether Impeccable appears
  installed, and is combined with any route or missing-input question of that round, before framing, design work or
  delegation; review-only and small requests are asked too.

### [AC-02] No question when the request already decides
- **Given** a request or exact prior instruction that states use or non-use of Impeccable
- **When** the coordinator starts the request
- **Then** it asks no Impeccable question and follows the stated choice.

### [AC-03] Asking is not selecting
- **Given** the question is pending, unanswered or there is no answer channel
- **When** the coordinator continues
- **Then** it loads and invokes no Impeccable, keeps the inline track for work that does not depend on the answer,
  and treats silence as non-selection.

### [AC-04] Yes without installation
- **Given** the user answers yes and Impeccable is not installed
- **When** the coordinator handles the answer
- **Then** the existing unavailable-Impeccable path applies (upstream install routes, user-requested install or
  inline continuation).

### [AC-05] Consistent contract
- **Given** the skill, orchestration reference, bundle README, capability, use case and decisions
- **When** they are reviewed and the bundle tests run
- **Then** they state the same upfront question, and the bundle text cites no authoring-repository document ID.
