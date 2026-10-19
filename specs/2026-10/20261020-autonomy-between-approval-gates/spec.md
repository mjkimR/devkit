---
id: SPEC-autonomy-between-approval-gates
title: Agent autonomy between explicit human decision points
summary: "Concentrates human intervention at defined approval and review points while agents handle implementation, verification and recovery within approved scope."
status: completed
created: 2026-10-20
related_capabilities:
  - CAP-DLV-delivery-workflows
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-autonomy-between-approval-gates] Agent autonomy between explicit human decision points

## 1. Problem Statement & Motivation

Existing contracts let agents choose implementation details inside agreed intent, but do not clearly apply that
principle to helper tools and routine failures. Repeated confirmations can therefore appear between the deliberate
human decision points. Make autonomous execution the explicit default without weakening checks or authority.

## 2. User Stories

- As a user, I want human intervention concentrated at defined approval and review points so that agents complete
  agreed work and resolve routine failures without asking me to manage each step.

## 3. Non-Goals

- **Scope Excluded**: changing gate policy, required reviews, bounded review loops, sandbox permissions or delegated
  write boundaries; adding remote integration authority, runtime automation or retry loops.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Execute autonomously inside approved intent

- **Given** agreed intent, sufficient authority and no outstanding required human decision
- **When** implementation choices or routine command failures arise
- **Then** an accepted ADR, the spec constitution and workflow capability direct the agent to choose, inspect, fix,
  revalidate and retry within scope without an extra human confirmation.

### [AC-02] Avoid incidental human gates

- **Given** a helper command or validation that supplies actionable findings
- **When** its behavior or procedure is designed
- **Then** the documents prohibit adding human approval or acknowledgment merely to process those findings and
  distinguish automated checks and agent reviews from human decisions.

### [AC-03] Preserve explicit authority and escalation boundaries

- **Given** a required human gate, a scope or contract change, missing authority, an explicit review stop or an
  unresolved problem the agent cannot solve within the agreement
- **When** the agent reaches that boundary
- **Then** it escalates to the responsible decision maker and preserves actual partial state; no document permits
  bypassing checks, access restrictions, delegated scope or approval denial.
