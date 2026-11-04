---
id: ADR-shared-role-authoring
title: Own role placement in shared asset authoring guidance
summary: "For authors choosing skill-local or registered roles, we keep placement and bounded-loading criteria in the common authoring instruction, to avoid global metadata and duplicated rules, accepting host-dependent execution settings."
status: accepted
created_at: 2026-11-04
---

# [ADR-shared-role-authoring] Own role placement in shared asset authoring guidance

Superseded in part by `ADR-role-authoring-reference`: placement of detailed role guidance and the direction of its conditional pointers.

## 1. Context & Problem Statement

Skill-only registered roles expose metadata beyond their invoking procedure. Shared asset writing already owns
conditional loading, but lacks a role-placement criterion. `ADR-skill-local-research-roles` demonstrates the
skill-local pattern without establishing a general authoring rule.

## 2. Decision Drivers

- Avoid unnecessary global role metadata.
- Preserve native settings and explicit permission limits.
- Keep one owner for shared writing criteria.

## 3. Considered Options

- Expand skill-authoring into skill/subagent configuration authoring: combines distinct procedures and broadens its trigger.
- Keep role placement in agent-asset-writing and link from the playbook: shares the criterion without widening the playbook.

## 4. Decision Outcome

- The common instruction covers subagents and defaults skill-only roles to local files, with independent selection
  or unavailable per-invocation host settings as registration reasons. → `CAP-HARN-agent-guidance` section 4.3 (SHOULD).
- The playbook points to that instruction when delegation is needed; role loading uses bounded assignments and
  reports host limits without claiming prompt-enforced permissions. → `CAP-HARN-agent-guidance` section 4.3 (SHOULD).

## 5. Consequences

Authors can avoid global role metadata without losing procedural detail. Native role settings require explicit
assessment. Existing bundles are not migrated by this writing change.

## 6. Confirmation

Existing authoring bundle tests check distribution, self-containment and budgets. Hygiene checks cover wording.
Review only for the placement criteria, conditional routing and truthful host limitations.
