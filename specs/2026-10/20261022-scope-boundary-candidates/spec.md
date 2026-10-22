---
id: SPEC-scope-boundary-candidates
title: Drop entrypoint candidates once a spec declares its code boundary
summary: Once tasks.md declares _Boundary code paths, the work scope registry compares a spec unit by its declared and observed code only, so the entrypoints of a broad capability target no longer report overlaps outside the unit's boundary.
status: planned
created: 2026-10-22
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-scope-boundary-candidates] Drop entrypoint candidates once a spec declares its code boundary

## 1. Problem Statement & Motivation

<Describe the problem, who has it and why it matters now.>

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Drop entrypoint candidates once a spec declares its code boundary so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>
