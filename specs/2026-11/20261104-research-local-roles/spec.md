---
id: SPEC-research-local-roles
title: Skill-local deep research roles
summary: Load deep-research role instructions only within the explicitly invoked skill, without global subagent registration.
status: planned
created: 2026-11-04
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---


# [SPEC-research-local-roles] Skill-local deep research roles

## 1. Problem Statement & Motivation

Registered research roles expose metadata outside the explicitly invoked skill. Keep their instructions local to
`CAP-DLV-deep-research` while preserving research boundaries.

## 2. User Stories

- **US-1**: As a consumer, I want research roles loaded only for assigned research tasks.

## 3. Non-Goals

- **Scope Excluded**: distribution schema changes, a general role runtime, other bundles and authoring policy changes.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Skill-local deployment
- **Given** a consumer selecting deep-research
- **When** sync runs for supported hosts
- **Then** the four role documents ship inside the explicit-only skill and no research subagent is registered.

### [AC-02] Bounded invocation
- **Given** an explicitly invoked research task
- **When** a role is useful
- **Then** a general subagent reads only its assigned role document first, with bounded input and no conversation inheritance where supported; permissions and returns remain explicit.

### [AC-03] Existing installations
- **Given** an earlier installation
- **When** it syncs the updated bundle
- **Then** unedited role projections are removed, edited projections remain subject to existing ownership safeguards, retained materials survive, and guides explain obsolete role settings and overrides.
