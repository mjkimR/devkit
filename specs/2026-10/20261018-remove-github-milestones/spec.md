---
id: SPEC-remove-github-milestones
title: Remove GitHub milestone guidance
summary: "Remove the opt-in GitHub milestone bundle and its recommendations while preserving repository-owned roadmap documents."
status: completed
created: 2026-10-18
related_capabilities:
  - CAP-DIST-content-packages
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-remove-github-milestones] Remove GitHub milestone guidance

## 1. Problem Statement

The optional github-milestones catalog bundle assigns roadmap ownership to GitHub, conflicting with
`ADR-roadmap-in-repository`. Remove the bundle and its consumer recommendations.

## 2. User Story

As a coding agent, I want installation guidance consistent with repository-owned milestones so that planning has one owner.

## 3. Non-Goals

- **Scope Excluded**: Changes to document milestones, issue integrations, external GitHub resources, or host-observer behavior.
- **Assumptions**: Remove the complete bundle, including issue-linking guidance; preserve historical ADRs and completed specs.

## 4. Acceptance Criteria

### [AC-01] Catalog no longer ships the bundle

- **Given** the catalog package sources
- **When** its wheel is built and bundle entry points are inspected
- **Then** github-milestones is absent from resources and registration, and host-observer remains available.

### [AC-02] Consumer guidance and smoke coverage agree

- **Given** current installation guides, architecture, READMEs and consumer smoke checks
- **When** references to the removed bundle are inspected
- **Then** no active recommendation or installation command remains, and smoke still verifies catalog opt-in deployment using host-observer.

### [AC-03] Repository milestone implementation is preserved

- **Given** document milestone sources and tests
- **When** the removal diff and existing milestone tests are checked
- **Then** document milestone sources are unchanged and the existing milestone tests pass.
