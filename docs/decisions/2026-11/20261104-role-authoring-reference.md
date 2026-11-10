---
id: ADR-role-authoring-reference
title: Load detailed role authoring through the skill-authoring reference
summary: "For occasional role-authoring tasks, we keep placement, delegation and path guidance in a playbook reference, to reduce common instruction context while preserving one owner, accepting a conditional lookup."
status: accepted
created_at: 2026-11-04
supersedes:
  - ADR-shared-role-authoring
---

# [ADR-role-authoring-reference] Load detailed role authoring through the skill-authoring reference

## 1. Context & Problem Statement

Detailed role placement and path instructions are irrelevant to most sentence-level asset edits. They belong
with skill orchestration authoring and can be loaded together only when needed.

## 2. Decision Drivers

- Keep common writing guidance short.
- Preserve one authoritative role guide and its permission distinctions.
- Keep role placement and path authoring together and discoverable.

## 3. Considered Options

- Retain detailed rules in the common instruction: immediately available, but loaded for unrelated edits.
- Keep a skill-authoring reference with conditional pointers: one lookup when needed, less common context.

## 4. Decision Outcome

- `skill-authoring/references/roles.md` owns role placement, bounded delegation and path-resolution authoring;
  the common instruction and playbook route to it conditionally. → `CAP-HARN-agent-guidance` section 4.3 (SHOULD).
- Existing local-versus-registered criteria, invocation distinctions and permission limits remain unchanged;
  the playbook retains its skill/playbook authoring trigger. → `CAP-HARN-agent-guidance` section 4.3 (SHOULD).

- Supersedes in part `ADR-shared-role-authoring`: the guidance-location clauses for detailed role guidance and the direction of its conditional pointers; other authoring and permission decisions remain unchanged.

## 5. Consequences

Common asset edits no longer load detailed role instructions. Role authors perform a conditional reference read.
No runtime, host variable or existing role behavior changes.

## 6. Confirmation

The authoring bundle integration test retrieves the installed playbook and verifies its linked reference files.
Asset hygiene checks and review verify conditional routing and preservation of the moved guidance.
