---
id: SPEC-adaptive-documenter
title: Adaptive documenter role
summary: "Add a skill-local documenter overlay for swarm-worker and connect retained-result document delegation."
status: completed
created: 2026-11-13
related_capabilities: [CAP-DLV-adaptive-development]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-adaptive-documenter] Adaptive documenter role

## 1. Problem Statement & Motivation

Document assignments lack a specialist overlay for comparing retained implementation with project documents.

## 2. User Stories

- **US-1**: As the coordinator, I want a documenter overlay for swarm-worker so retained implementation is reflected in current-state documents.

## 3. Non-Goals

- **Scope Excluded**: A registered subagent, mandatory delegation, runtime changes, additional authority or changes to Host current-context ownership.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Installed documenter overlay

- **Given** a consumer selects adaptive-dev:core.
- **When** sync projects the adaptive-dev skill.
- **Then** roles/documenter.md is available relative to the installed skill and uses swarm-worker without registering a documenter subagent.

### [AC-02] Bounded document delegation

- **Given** retained implementation has been integrated.
- **When** the coordinator delegates useful separable document writing.
- **Then** documents.md routes to swarm-worker with roles/documenter.md, exclusive document paths, described source identity and governing documents.
- **Then** the role compares source and documents, updates warranted current-state documents, reports conflicts, runs document checks and returns paths, source identity and unverified areas.
- **Then** current-context writes and final integration remain with the Host, and the agreed shared-interface exception remains available.
