---
id: SPEC-worker-guidance-and-fixtures
title: Clarify worker handoffs and isolate Git test fixtures
summary: "Define unsolicited decision recording, official documentation reads, Host synchronization, link-repair scope and Git fixture isolation."
status: completed
created: 2026-10-20
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-worker-guidance-and-fixtures] Clarify worker handoffs and isolate Git test fixtures

## Problem and user story

As an orchestration Host, I need clear handoff and integration responsibilities so workers can preserve decisions,
verify external facts, and run isolated tests without expanding their write authority.

## Non-Goals

No envelope schemas, blanket network grants, production registry behavior, automatic scope derivation, or worker
receipt-write exceptions. No change to pending-question answers or integration approval policy.

## Acceptance Criteria

### [AC-01] Unsolicited direction
- **Given** a user direction without a recorded question,
- **When** Planning incorporates it,
- **Then** the proposal/PADR and subsequent worker record capture the decision without fabricated questions or a new envelope kind; existing pending questions and recorded-assumption settlements still use their existing answer procedure.

### [AC-02] Official documentation authority
- **Given** a design depends on external platform facts,
- **When** the Host delegates it,
- **Then** the payload specifies necessary official-document reads separately from mutations; when unavailable, the Host supplies verified evidence, and unverified facts are not treated as settled design.

### [AC-03] Host synchronization
- **Given** changed bundle sources and a moved base,
- **When** the Host prepares integration,
- **Then** official sync and receipt updates follow base incorporation and precede final verification and approval; base projections are synchronized after landing, without worker receipt-write authority.

### [AC-04] Isolated Git fixtures
- **Given** pytest basetemp inside an active worktree,
- **When** scope tests use plain fixture directories and nested Git repositories,
- **Then** plain directories raise SPEC_SCOPE_NOT_A_WORKTREE while fixture repositories and linked worktrees remain discoverable, with the Git ceiling scoped to tests.

### [AC-05] Link repair scope
- **Given** a delegated move or deletion,
- **When** the Host prepares boundaries,
- **Then** it inspects inbound references and grants exact link-repair-only paths; an unexpected target requires narrow expansion rather than a general write exception.

## Source feedback

- `FB-planning-direction-change-without-question`
- `FB-planning-platform-facts-unverifiable-offline`
- `FB-worker-bundle-edit-leaves-receipt-stale`
- `FB-worker-fixtures-inherit-git-context`
- `FB-worker-scope-misses-link-repairs`

## Assumptions

These clarify existing Host/worker duties and test isolation; no existing MUST or architecture decision changes.
