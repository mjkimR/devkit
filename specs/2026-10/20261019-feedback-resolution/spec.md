---
id: SPEC-feedback-resolution
title: Resolve feedback through delivery completion
summary: "Distinguishes feedback resolution from promotion and connects source feedback to spec and session completion with verification evidence."
status: completed
created: 2026-10-19
related_capabilities:
  - CAP-HARN-agent-guidance
  - CAP-DOCS-document-model
  - CAP-DLV-delivery-workflows
  - CAP-DLV-proposal-incubation
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-feedback-resolution] Resolve feedback through delivery completion

## 1. Problem Statement & Motivation

Feedback promoted into follow-up work and feedback fixed directly currently share the promoted status. Direct
spec/session work can leave its originating feedback open after a verified fix, because capture forbids status
changes and completion does not require source feedback disposition.

## 2. User Stories

- **US-1**: As a coding agent, I want to distinguish routed feedback from verified fixes and update only the source
  feedback my authorized task addresses, so future work selection does not recommend completed fixes.

## 3. Non-Goals

1. **Scope Excluded**: automatic backlog-wide closure, a new status-update CLI, a new workflow stage or gate,
   migration of historical promoted items, and changing external submission or integration authority.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Distinguish promotion and resolution
- **Given** feedback captured as open
- **When** follow-up work receives it or an authorized fix fully addresses and verifies it
- **Then** promotion records promoted with a destination; verified completion records resolved with the destination,
  implemented outcome and verification evidence; capture alone changes neither status.

### [AC-02] Preserve feedback during handoff
- **Given** an accepted proposal citing source feedback and containing open, promoted and resolved feedback files
- **When** handoff creates a spec and retires the proposal on the task branch
- **Then** source feedback references survive in the spec, open files move to spec feedback, all other known states
  follow preserved materials with their status unchanged, and handoff never marks a source item resolved.

### [AC-03] Connect source feedback at task entry
- **Given** an authorized task selected from named feedback
- **When** spec/proposal work or session work begins
- **Then** its source FB IDs are recorded in the spec/proposal body or session agreed scope, respectively, and the
  expected task boundaries include any source feedback files that completion must update.

### [AC-04] Resolve only verified complete source feedback
- **Given** a task with recorded source feedback
- **When** spec reconciliation or session completion reviews its final diff and verification
- **Then** fully addressed open/promoted source items become resolved in the task branch with evidence; partial,
  deferred or unverified items keep their existing status with remaining scope explained; newly captured unrelated
  observations stay open. Reopening the implementation also rechecks any resolution whose evidence became stale.

### [AC-05] Support discovery and repair the motivating stale item
- **Given** resolved feedback in current document locations
- **When** explicit resolved and open list filters are used
- **Then** resolved feedback is discoverable under resolved and absent under open; the verified summary-length fix's
  source feedback is marked resolved with its existing implementation and test evidence.

## 5. Assumptions

- Source feedback is a section containing full FB IDs in the existing Markdown body, not a new frontmatter schema.
  Handoff already carries proposal body sections; specification drafting keeps this section.
- Resolution means implemented and verified on the task branch, not integrated. The normal integration gate remains.
- A new ADR records the lifecycle policy separating recording, promotion and direct resolution; historical statuses
  are left alone except for the motivating summary-length feedback explicitly checked in this work.
