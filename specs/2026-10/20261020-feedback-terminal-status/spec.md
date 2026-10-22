---
id: SPEC-feedback-terminal-status
title: Treat feedback promotion and direct resolution as terminal outcomes
summary: "Feedback promotion closes routing to follow-up work; direct resolution closes verified fixes without promotion."
status: completed
created: 2026-10-20
related_capabilities:
  - CAP-DOCS-document-model
  - CAP-HARN-agent-guidance
  - CAP-DLV-delivery-workflows
  - CAP-DLV-proposal-incubation
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-feedback-terminal-status] Terminal feedback dispositions

## 1. Problem and user story

Completion instructions currently require promoted feedback to be revisited and resolved. This duplicates the
follow-up work's lifecycle and incorrectly treats a routing disposition as unfinished feedback. As a repository
maintainer, I want only open feedback to require action, with promotion and direct resolution closing separate routes.

## 2. Non-Goals

- **Scope Excluded**: bulk migration of historical feedback, schema changes, new statuses, proposal lifecycle changes,
  automatic closure of open feedback, and integration or deployment of projected assets.

## 3. Acceptance Criteria

### [AC-01] Promotion terminates feedback tracking
- **Given** an observation handed to identified follow-up work and marked promoted,
- **When** that work is implemented or reviewed,
- **Then** instructions keep the original feedback terminal and impose no status update or resolution check on it;
  source FB references remain traceability and progress is tracked in the follow-up unit.

### [AC-02] Direct verified fixes resolve open sources
- **Given** an explicitly linked open observation addressed without promotion,
- **When** the authorized session or spec implementation fully fixes and verifies it,
- **Then** completion records resolved with outcome and evidence; incomplete or unverified observations stay open.

### [AC-03] Source references do not authorize terminal writes
- **Given** a committed spec with source feedback references,
- **When** worker inspection derives its scope,
- **Then** only sources whose committed status is open add source-feedback write paths; terminal or unknown statuses
  add none, and explicit task boundaries remain independently effective.

### [AC-04] Decision history and preserved feedback remain intact
- **Given** the accepted prior lifecycle and existing feedback files,
- **When** the correction lands,
- **Then** a superseding ADR preserves the prior decision body, current contracts agree, and historical feedback and
  existing handoff/archive handling remain unchanged.

## 4. Assumptions

Direct resolution may occur in a spec unit as well as a session; “without promotion” does not mean “without a unit”.
The existing list command's explicit status filter remains the way to select the open backlog.
