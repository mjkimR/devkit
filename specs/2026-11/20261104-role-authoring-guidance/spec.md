---
id: SPEC-role-authoring-guidance
title: Author skill-local roles and registered subagents
summary: Define shared authoring criteria for skill-local role instructions and registered subagents.
status: completed
created: 2026-11-04
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-role-authoring-guidance] Author skill-local roles and registered subagents

## 1. Problem Statement & Motivation

Shared authoring guidance does not distinguish internal role instructions from globally registered subagents.
Authors need a placement criterion that avoids unnecessary global metadata while preserving native host settings.

## 2. User Stories

- **US-1**: As an asset author, I want one shared role-placement criterion and a skill-authoring pointer to it.

## 3. Non-Goals

- **Scope Excluded**: role runtime or manifest changes, migration of other bundles, broadening the playbook into native subagent configuration authoring.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Shared placement criterion
- **Given** an author editing a skill, playbook, instruction or subagent
- **When** they read agent-asset-writing
- **Then** it defaults skill-only roles to internal Markdown and identifies independent selection or required host settings as reasons for registration.

### [AC-02] Bounded role loading
- **Given** a skill-local role
- **When** the author defines delegation
- **Then** the guidance specifies the assigned role path, first read, bounded task and return, minimal context and actual host permission limits without claiming Markdown enforces tools or sandbox settings.

### [AC-03] Single guidance owner
- **Given** a skill authoring task requiring delegation
- **When** the author follows the playbook
- **Then** it references the shared role-placement section without duplicating that policy or widening its overall purpose; synchronized consumer assets carry both edits.

## Source feedback

`FB-skill-local-role-authoring`: add the shared criterion and conditional playbook pointer.
