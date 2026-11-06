---
id: ADR-skill-local-swarm-roles
title: Reusable prefixed subagents with optional role teams
summary: "For adaptive delegation, we propose reusable prefixed archetypes with on-demand role contracts and optional two-level teams, to support project extensions, accepting host-specific capability checks and coordination overhead."
proposal: SPEC-adaptive-swarm-development
status: accepted
supersedes: ADR-adaptive-development-and-research
supersedes_clause: "Adaptive-dev role-set and role-authority clauses only; approach, current-context and research-material decisions remain in force."
created_at: 2026-11-06
---

# [ADR-skill-local-swarm-roles] Reusable prefixed subagents with optional role teams

## 1. Context & Problem Statement

Adaptive development already registers optional product support roles, but has no code-writing team contract.
General execution settings and task-specific specialization have different lifecycles. Registering every persona
expands the public agent surface; using only local role files leaves recurring execution configuration to each caller.
Neither registration nor role-file placement alone establishes native permission enforcement or model selection.

The existing capability excludes a mandatory hierarchy and a new model router. Optional role leads can delegate
local subtasks while the Host keeps user-facing authority and final integration. Registration and topology therefore
need separate decisions.

## 2. Decision Drivers

- Reuse common execution contracts across compatible callers.
- Add project specialists without editing shipped agents.
- Preserve direct work and flat delegation for small assignments.
- Bound nested authority, ownership and session-wide capacity.
- Use existing host projections and model levels without distribution changes.
- Keep docs/catalog installation independent of SDD and other role catalogs.

## 3. Considered Options

### Registration

- Existing direct work and general agents with role files: small surface, but recurring configuration stays with callers.
- Prefixed archetypes with role files: reusable execution defaults, with additional metadata and projection maintenance.
- Registered core personas plus a role catalog: convenient for recurring domain work, with more coupled public identities.
- Register every specialist: explicit configuration per role, with the largest maintenance and metadata surface.

### Team topology

- Flat only: simple ownership and capacity accounting, but the Host handles every subtask.
- Optional role leads with one child level: local coordination when useful, with extra context transfer and occupied slots.
- Mandatory or unbounded nested teams: extra orchestration for small tasks and harder interruption/capacity management.

## 4. Decision Outcome

The choice is prefixed archetypes with role overlays, supporting optional role leads.

- `adaptive-dev` owns the public `swarm-planner`, `swarm-worker` and `swarm-verifier` assets; compatible
  callers can reuse installed contracts without importing private orchestration or sibling role files.
- The `agents` preset selects only the three public archetypes; `core` adds them to the existing adaptive entry and
  support assets. Shared agents have no adaptive entry prerequisite and follow their caller's governing workflow.
- Source model/effort defaults remain omitted; existing bundle-qualified project model policy applies.
- Projects extend behavior through their own prefixed agents or bounded role files; the default set is not an extension cap.
- Task overlays narrow assignments and cannot expand execution permissions or Git authority. The planner stays
  read-only; the verifier may write assigned test/probe artifacts while product sources and Git remain read-only.
  Worker commits require explicit assignment authority.
- The Host chooses direct, flat or nested execution per task. A role lead owns the aggregate result of its assignment.
- Nested execution stops at Host → lead → child and uses a Host-assigned session-wide child budget, including waiting leads.
- Unsupported nesting or insufficient capacity produces flat, direct or sequential execution with explicit limitations.
- Host support status and subagent model levels use existing distribution contracts. No native enforcement or model
  savings is inferred from registration alone.

`CAP-DLV-adaptive-development` rules 1, 12, 13 and 19 and its reusable-agent interface restate these clauses;
`UC-advance-an-idea` extensions 5b through 5b4 cover optional teams and fallback. `ARCH-05-2-components`
restates catalog ownership. This decision partially supersedes the role-set clauses of
`ADR-adaptive-development-and-research`. Its approach, current-context and research-material decisions are retained.

## 5. Consequences

- A small reusable execution vocabulary supports task specialization without registering every persona.
- A lead can coordinate independent subtasks, but adds context transfer and consumes a slot while waiting.
- Public agent IDs need stable ownership and project extensions need distinct names.
- Role compatibility and actual host capabilities must be checked at dispatch; Markdown is not a permissions boundary.
- Bundles retain self-contained assets; optional external callers handle availability and their own fallback.

## 6. Confirmation

Catalog integration and installed-consumer tests check prefixed assets, host projections, project extensions
and installation without `devkit-spec`. Representative invocation exercises check flat/nested dispatch, capacity
fallback and actual permission status. The Planning projection and read-only nesting observations are in
[feasibility-spike.md](../../materials/2026-11/20261106-adaptive-swarm-development/feasibility-spike.md). `SPEC-adaptive-swarm-development` retains actual isolated fixture-writing, aggregate-failure and dirty-checkpoint
observations using generic authored-contract emulation. Native named-role invocation, native enforcement,
unexercised runtimes and performance remain unverified; static checks do not establish them.
Review only for semantic ownership and overlay compatibility; packaging tests do not prove either.
