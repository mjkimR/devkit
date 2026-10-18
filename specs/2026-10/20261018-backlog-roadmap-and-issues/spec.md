---
id: SPEC-backlog-roadmap-and-issues
title: 'Backlog: repository roadmap and next-work selection'
summary: Gives Backlog a repository-owned roadmap of milestone documents ordered by depends_on, links Units to milestones, preserves request provenance through decomposition and handoff, and lets spec-next recommend the next work without issue tracker integration.
status: in-progress
created: 2026-10-18
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-backlog-roadmap-and-issues] Repository roadmap and Backlog

## 1. Problem Statement & Motivation

Agents can track one Unit but cannot inspect a validated repository roadmap or choose the next queued request.
Implement the accepted repository-owned direction of `ADR-roadmap-in-repository` and `ADR-milestone-documents`.

## 2. User Stories

As a development agent, I want validated milestone membership and request provenance, so I can recommend the next
work and maintain the roadmap without an external tracker. This extends `US-route-development-intent`.

## 3. Non-Goals

- **Scope Excluded**: GitHub issue fields, options, intake, closing, tracker synchronization and autohub integration.
- **Scope Excluded**: CLI sorting, roadmap viewers, estimates, goal IDs, per-namespace milestones and direct draft acceptance.
- **Scope Excluded**: retroactive milestone assignment to completed specs, automatic milestone transitions and branch-blind close recommendations.

## 4. Acceptance Criteria & Behavioral Contracts

### Scenario 1: [AC-01] Milestone identity and discovery
- **Given** a global document at docs/roadmap/MS-release-1-0.md with id, title, summary, status and created_at
- **When** documents are indexed, listed, resolved or searched
- **Then** its kind is milestone, its ID is MS-release-1-0, and done/dropped milestones are hidden by default but remain resolvable and available with history.

### Scenario 2: [AC-02] Milestone format and deterministic fixes
- **Given** a milestone missing required metadata or carrying an unsupported status or path
- **When** the format, summary and ID rules run
- **Then** violations identify missing fields, non-English or missing summary, statuses outside planned/active/done/dropped, and invalid global paths; safe fixes derive the MS ID and fill status planned, never draft.

### Scenario 3: [AC-03] Membership and dependency validation
- **Given** proposal/spec milestone fields and milestone depends_on lists
- **When** reference rules run
- **Then** milestone takes one existing MS ID only on proposal/spec anchors; depends_on takes existing MS IDs only on milestones; cycles including self-cycles are errors, and targeting one member still detects a cycle through untargeted milestones.

### Scenario 4: [AC-04] Authoring and provenance
- **Given** an existing milestone and a draft parent proposal
- **When** proposal new or spec new receives --milestone, or proposal new receives --decomposed-from
- **Then** values are validated before writing; the parent must exist, be draft and not be in Planning; handoff carries milestone, decomposed_from and supersedes as provenance, retaining unresolved historical origins without reference errors.

### Scenario 5: [AC-05] Settled milestone member advisories
- **Given** done or dropped milestones with unsettled proposal/spec anchor members on the base
- **When** a whole-workspace hygiene check runs
- **Then** separate stable warning codes identify done and dropped milestones with unsettled members; completed specs and rejected proposals do not trigger warnings, warnings have deterministic remediation and do not change success exit codes.

### Scenario 6: [AC-06] Backlog lifecycle procedure
- **Given** an agent managing repository requests
- **When** it follows the Backlog guidance
- **Then** queued requests and decomposition results are drafts with provenance; activation checks dependencies, close checks base and activity branches, drop offers member reassignment/clearing/rejection, and all milestone transitions remain explicit user decisions with no tracker operations.

### Scenario 7: [AC-07] Next-work selection
- **Given** queued drafts and milestone metadata
- **When** spec-next finds no in-progress Unit
- **Then** it recommends Planning-eligible drafts by critical first, milestone rank, milestone created_at/ID, priority, size, draft created_at/ID; it reports unready/done/dropped and needs_decompose drafts as Backlog actions, recognizes reviewing/accepted or activity-branch Units as in progress, and reports the roadmap review due at three done milestones or 2027-01-31 until a roadmap-review ADR exists.

### Scenario 8: [AC-08] Templates and scope exclusions
- **Given** the spec bundle is deployed
- **When** milestone templates, seeded docs and quick references are inspected
- **Then** a milestone template and roadmap location are discoverable, goals link to milestone documents, membership is declared only on Units, and no issue field or tracker workflow is introduced.

## 5. Implementation Assumptions

Milestones are global; namespaced Units may reference them. Historical milestone outgoing references are checked only
when explicitly targeted, as with completed spec history. Request provenance is shape-checked but does not require
its source proposal to survive deletion. Existing live-branch enumeration is reused by procedures; no new scheduling
or tracker command is introduced. Documentation and procedural ACs are verified by inspection and bundle contract tests.
