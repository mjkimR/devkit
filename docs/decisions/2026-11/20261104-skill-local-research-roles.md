---
id: ADR-skill-local-research-roles
title: Keep research roles inside the explicitly invoked skill
summary: "For research roles needed only by one skill, we ship local role instructions and spawn general subagents, to avoid global role metadata, accepting host-inherited execution settings."
status: accepted
created_at: 2026-11-04
supersedes:
  - ADR-adaptive-development-and-research
---

# [ADR-skill-local-research-roles] Keep research roles inside the explicitly invoked skill

## 1. Context & Problem Statement

Registered research roles expose descriptions outside explicit research invocation. The four procedures need
separate assignments, but do not need independent global selection. There are no installed consumers requiring
compatibility machinery.

## 2. Decision Drivers

- Keep role metadata out of global context.
- Preserve bounded research, evidence and coordinator ownership.
- Reuse skill directory distribution without a role runtime.

## 3. Considered Options

- Keep registered roles and restrict their descriptions: simple, but metadata remains globally visible.
- Ship role instructions inside the skill: selected children load them on demand, without native role settings.

## 4. Decision Outcome

- Deep research ships its four role documents inside the skill and registers no research subagents. Bundle ownership, optionality and retained materials remain unchanged.
  → `CAP-DLV-deep-research` rule 1 (MUST).
- A general subagent receives the selected role path and bounded assignment, with a fresh context where supported.
  Role instructions confer no native tool or sandbox settings. → `CAP-DLV-deep-research` rule 11 (MUST).

- Supersedes in part `ADR-adaptive-development-and-research`: the registered research-role projection and role-policy migration clauses only; bundle ownership, optionality and retained materials remain unchanged.

## 5. Consequences

Global role discovery no longer exposes research-only metadata. Role-specific host settings are no longer supplied
by the bundle. Stale policy keys must be removed and custom instructions ported to the skill override if present.

## 6. Confirmation

Catalog integration tests verify local role files, absent native projections and basic cleanup on sync. The
installed-consumer test verifies wheel packaging without devkit-spec. Review checks assignment guidance; no test
claims reliable model obedience or execution isolation.
