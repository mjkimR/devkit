---
id: SPEC-uiux-improve-bundle-hygiene
title: app-uiux-improve pilot hygiene fixes
summary: "Clarifies branch-build verification, brief scope and precedence, goal-aware acceptance, measured contrast and local context paths in the UI/UX improvement bundle."
status: completed
created: 2026-11-13
depends_on: [SPEC-uiux-improve-impeccable-routing]
decomposed_from: PROP-uiux-improve-pilot-fit
related_capabilities: [CAP-DLV-uiux-improvement]
related_usecases: [UC-improve-an-interface-and-user-flow]
workflow: sdd-spec-feature
---

# [SPEC-uiux-improve-bundle-hygiene] app-uiux-improve pilot hygiene fixes

## 1. Problem Statement & Motivation

`MAT-uiux-improve-pilot` identifies instruction gaps in verification, scope handling, contrast measurement and
local-only context. The accepted target draft `PROP-uiux-improve-bundle-hygiene-target` maps the fixes. The landed
`SPEC-uiux-improve-run-model` and `SPEC-uiux-improve-impeccable-routing` already govern route approval and relay;
this change preserves them and clarifies `CAP-DLV-uiux-improvement` and `UC-improve-an-interface-and-user-flow`.

## 2. User Stories

- **US-1**: As a coordinator, I want actionable verification and brief instructions so that I check the branch and
  accept only changes serving the approved goal.
- **US-2**: As a designer, I want measured contrast and explicit context boundaries so that color advice is testable
  and consumer-owned files stay under the user's control.

## 3. Non-Goals

1. **Scope Excluded**: new run modes, question/load routing, setup or file-write authority, runtime code, package or
   feature edges, test tiers, distribution behavior or ADRs.
2. **Scope Excluded**: automatic consumer document edits, native plugin/host certification or claims of model
   obedience, visual quality or comparative effectiveness. Empirical trials remain best effort.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Verify the changed branch build
- **Given** a deployed baseline and an executable local changed branch build.
- **When** the coordinator inspects and verifies the improvement.
- **Then** it checks that branch before and after with the same task/data; a repeatable mocked backend is allowed
  when live service use is costly or shared, and the report names mocked coverage and missing live coverage.

### [AC-02] Keep a focus distinct from a constraint
- **Given** a focus such as color first.
- **When** the coordinator writes a brief or chooses changes.
- **Then** the focus orders work; only user-stated constraints or explicit deferrals become non-goals.

### [AC-03] State craft precedence
- **Given** a craft default that conflicts with the authorized brief or consumer specification.
- **When** the delegated session applies it.
- **Then** the brief states that authorized sources control; conflicting authorized sources return for a decision.

### [AC-04] Accept against goal and edit list
- **Given** a listed product-file edit outside the approved goal, such as an unrelated dependency bump.
- **When** the coordinator accepts the session return.
- **Then** it reports and excludes the edit from accepted work without unsolicited reversion or deletion.

### [AC-05] Compute color contrast
- **Given** color work by the coordinator or a designer role.
- **When** key foreground/background pairs are checked or proposed.
- **Then** the instructions require color-space conversion, effective colors accounting for opacity/compositing,
  numeric ratios per pair/state, comparison with applicable consumer criteria and explicit missing coverage.

### [AC-06] Pass local-only context read-only
- **Given** untracked or excluded PRODUCT.md or DESIGN.md and a session elsewhere.
- **When** the coordinator briefs it.
- **Then** the brief passes absolute read-only paths and preserves consumer ownership and upstream retention guidance;
  it infers no copy, commit, ignore or removal action.

### [AC-07] Keep load diagnosis and wording workflow-neutral
- **Given** a plugin-load failure or an independently installed bundle.
- **When** the guide and agent-read bodies describe the procedure.
- **Then** the guide checks current-project plugin enablement, prescribes no cache-load route, and agent bodies
  depend on no devkit-spec policy key, CLI gate or lifecycle record while retaining generic branch/worktree terms.

## 5. Verification and assumptions

Instruction assertions in the existing catalog integration file prove authored directives, not model obedience.
Review walks the seven accepted cases, including in-list/out-of-goal changes and opaque/translucent contrast.
No live consumer build exists in this content-only unit; empirical behavior stays explicitly unverified.
The entry, source ownership and predecessor authority remain unchanged. No screen draft or new runtime is needed.
