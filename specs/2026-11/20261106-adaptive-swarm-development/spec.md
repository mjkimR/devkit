---
id: SPEC-adaptive-swarm-development
title: Reusable Subagents and Optional Teams for Adaptive Development
summary: "Extend adaptive development with reusable prefixed subagents, on-demand role contracts and optional two-level delegation, preserving direct work and source-specific verification."
status: completed
created: 2026-11-06
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-adaptive-swarm-development] Reusable Subagents and Optional Teams

## 1. Problem and Scope

### 1. Background & Hypothesis

`CAP-DLV-adaptive-development` already supports clarification, research, implementation and usage verification
without per-change SDD records. Its bundle registers three optional support subagents: `product-clarifier`,
`product-researcher` and `usage-reviewer`. The missing capability is a reusable delegation procedure for code-writing
teams, including ownership, nested delegation and verification of their combined result.

SDD already supports isolated workers and nested review delegation (`ARCH-04-delivery-strategy`). This proposal
adapts useful delegation patterns to adaptive development without introducing SDD Units or a mandatory role pipeline.
It does not claim that SDD execution is necessarily serial or that adaptive development is limited to ideation.

#### Core hypothesis

A small set of reusable, prefixed subagents can supply execution capabilities, while on-demand `roles/*.md`
contracts supply task-specific responsibilities. A subagent can execute a bounded task itself or, where the host
supports nesting and the task warrants it, lead a small team of its own subagents. Registration and team topology
are separate choices: either flat or nested execution can use the same registered agents and role documents.

Planning has exercised source-level projection, an agent-only preset and one read-only nested role assignment.
These observations establish bounded feasibility, not completed implementation. Prompt cost, latency, model savings
and native host enforcement remain unmeasured.
The local reference comparison is in [reference-swarm-architectures.md](../../../docs/materials/2026-11/20261106-adaptive-swarm-development/reference-swarm-architectures.md).
Upstream examples motivate patterns; they are not evidence of performance or correctness in devkit.

#### Scope and non-goals

In scope:

- Ship a small default set of general execution subagents with a common prefix in `adaptive-dev`.
- Allow installed prefixed subagents to be reused by compatible callers, and allow projects to add their own agents.
- Keep task and domain specializations in role Markdown files loaded only for the assigned task.
- Support direct work, flat delegation and optional two-level delegation with bounded ownership and concurrency.
- Define worker isolation, combined verification, interruption recovery and current-context ownership.
- Update the capability, use case and catalog ownership description after implementation.
- Verify bundle installation, projection, extension and representative invocation behavior.

Scope excluded:

- A runtime scheduler, daemon, agent bus, automatic agent importer or new package.
- Changes to distribution schemas, host settings, SDD orchestration or shared model-level resolution.
- A mandatory team hierarchy or role sequence for every adaptive action.
- Automatic approach switching, SDD adoption, publication or new approval authority.
- Guaranteed speedup, conflict-free merges, native file-boundary enforcement or model quality equivalence.
- Making other bundles depend on these agents or moving existing SDD roles into a shared registry.

## 2. User Stories

- As a caller, I can reuse execution agents under my existing lifecycle and authority.
- As the Host, I can delegate bounded implementation and verify combined results without a fixed team pipeline.

## 3. Non-Goals

**Scope Excluded:** Runtime/schema changes, host configuration, mandatory teams, new feature edges, performance guarantees and native confinement claims.

## 4. Acceptance Criteria

### Scenario 1 [AC-01]

- **Given** an adaptive task that needs no delegation
- **When** the Host acts
- **Then** it can implement and verify
  directly without creating SDD artifacts or running a fixed team sequence.

### Scenario 2 [AC-02]

- **Given** an independent docs/catalog installation
- **When** `adaptive-dev` is selected and synchronized
- **Then** the three prefixed archetype contracts and their supported projections deploy without `devkit-spec`.

### Scenario 3 [AC-03]

- **Given** a compatible caller and an installed archetype
- **When** the caller supplies its own bounded role
  assignment
- **Then** the agent can return the requested evidence without loading adaptive orchestration or sibling
  bundles' private assets.

### Scenario 4 [AC-04]

- **Given** a project-owned specialized agent or role overlay
- **When** it is selected for a task
- **Then** shipped
  defaults remain unchanged and incompatible permissions or unavailable capabilities are reported explicitly.

### Scenario 5 [AC-05]

- **Given** a nested assignment
- **When** the lead dispatches children
- **Then** depth stays within two child levels,
  all children fit the Host's shared allowance, and each child stays within its parent's authority and ownership.

### Scenario 6 [AC-06]

- **Given** no nested-agent support or insufficient capacity
- **When** the assignment is executed
- **Then** the Host
  flattens or serializes it and preserves the same result and verification contracts without changing host settings.

### Scenario 7 [AC-07]

- **Given** concurrent writing children
- **When** they implement
- **Then** each owns a separate worktree; a parent
  performs no concurrent writes there, and actual changed paths are checked before integration.

### Scenario 8 [AC-08]

- **Given** completed worker results
- **When** the Host reports delivery
- **Then** combined and applicable landed-target
  checks identify their actual SHAs, commands and outcomes; failed or unavailable checks remain explicit.

### Scenario 9 [AC-09]

- **Given** a failed or interrupted assignment
- **When** work pauses
- **Then** current context records retained results,
  active ownership and the next action, and cleanup preserves unmerged or dirty work.

### Scenario 10 [AC-10]

- **Given** an SDD consumer selecting only `adaptive-dev:agents`
- **When** assets synchronize and a compatible
  caller assigns bounded work
- **Then** only the three execution agents deploy, no adaptive entry/pointer or current
  context deploys, and neither the approach nor the caller's lifecycle authority changes.


## 5. Assumptions and Baseline

The accepted proposal premises still hold at input fc02ef0a: existing projections and bundle-qualified policy support the content-only change. Use registered roles where available; generic role-file emulation reports its limits. Current project remains SDD. Public archetypes omit skill, model and effort defaults. The accepted reference baseline is main 441bfde9603497c652d9cd6aac7c2688f0a2603a; compare source/projection behavior with the recorded Planning probe and measure final head behavior without checking out base. Runtime performance is unmeasured.

Retained Planning materials: docs/materials/2026-11/20261106-adaptive-swarm-development/. Development retains semantic evidence inside this Unit.
