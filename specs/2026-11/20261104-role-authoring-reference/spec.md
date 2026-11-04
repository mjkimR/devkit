---
id: SPEC-role-authoring-reference
title: Load role authoring through a playbook reference
summary: Move role placement, delegation and path-resolution guidance into the skill-authoring reference with conditional routing.
status: completed
created: 2026-11-04
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-role-authoring-reference] Load role authoring through a playbook reference

## 1. Problem Statement & Motivation

Role-specific authoring detail is loaded with every common writing task. Keep it in the skill-authoring
reference and load it only when delegated work or role paths are being authored.

## 2. User Stories

- **US-1**: As an asset author, I want role placement and path guidance together in a conditional reference.

## 3. Non-Goals

- **Scope Excluded**: runtime, template variables, host-specific substitutions, changes to existing role behavior or migration of other bundles.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Conditional ownership
- **Given** the authoring bundle
- **When** an author reads the common instruction
- **Then** it contains only a conditional route for role-specific guidance, and skill-authoring links its roles reference when delegation is needed.

### [AC-02] Complete role guide
- **Given** a role authoring task
- **When** the reference is loaded
- **Then** it covers local versus registered placement, each invocation path, bounded assignments, host limitations and skill-root path resolution with a concrete example.

### [AC-03] Installed reference
- **Given** a synchronized consumer
- **When** the skill-authoring playbook is retrieved
- **Then** the linked role reference is deployed and readable, without duplication of its detailed policy in the common instruction.
