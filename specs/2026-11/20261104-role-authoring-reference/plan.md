---
id: PLAN-role-authoring-reference
spec: SPEC-role-authoring-reference
---

# Technical Plan

## 1. Constitution & Invariant Review

Partially supersede the guidance-location clauses of `ADR-shared-role-authoring`; retain its placement and
permission semantics. Preserve bundle self-containment and the playbook's existing trigger.

## 2. Architecture Overview & Impact

Move Role Placement into `skill-authoring/references/roles.md`, split placement, delegation and path-authoring
sections, and retain conditional routes in the common instruction and playbook. Reflect the location in
`CAP-HARN-agent-guidance`. No new feature edge or dependency.

## 6. Verification & Test Plan

Verify the actual installed reference via playbook get in the existing authoring bundle test. Run
`just test-affected`, lint/type checks, sync, hygiene and CI governance. Independent review compares the moved
content with the original and walks local and registered roles plus nested reference path resolution.
