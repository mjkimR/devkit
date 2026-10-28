---
id: SPEC-milestone-non-binding
title: Non-binding milestone guidance
summary: "Milestone guidance states that a milestone frames a theme without binding Planning, so agents never treat its goal, exit condition or non-goals as constraints on design options."
status: planned
created: 2026-10-28
related_capabilities: [CAP-HARN-agent-guidance]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-milestone-non-binding] Non-binding milestone guidance

## 1. Problem Statement & Motivation

A milestone frames a large theme; scope and requirements are concretized and settled only in proposal Planning.
The milestone template and the Backlog guidance never say so, and the template's `Exit condition` and `Non-goals`
sections read like requirements. Agents discussing a design therefore judge options against milestone wording,
which the user has to correct.

## 2. User Stories

- **US-1**: As a user designing work under a milestone, I want the agent to judge options on their merits so that
  a rough theme document does not constrain decisions Planning has not made yet.

## 3. Non-Goals

1. **Scope Excluded**: Milestone statuses, frontmatter, completion review or merge procedures; no new status is added.
2. **Scope Excluded**: Editing existing milestone documents under `docs/roadmap/`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The milestone template states that it does not bind Planning
- **Given** an agent creates or reads a milestone from `templates/milestone.md`
- **When** it reads the template's guidance
- **Then** the guidance states that the milestone, in any status, frames direction only, that proposal Planning
  settles scope and requirements, and that its goal, exit condition and non-goals are not constraints on design options

### [AC-02] Backlog guidance applies the same boundary
- **Given** the `spec` skill's Backlog reference
- **When** an agent reads its Milestones section
- **Then** it states the same non-binding boundary for design discussions and Planning

### [AC-03] The Living Spec stays in step
- **Given** `CAP-HARN-agent-guidance` describes milestones
- **When** the guidance changes
- **Then** the capability states the same boundary, and `devkit sync --check` and `just rules-check` pass
