---
id: PROP-local-orch-resource-manager-target
title: Target Living Spec for a reusable lifecycle resource manager
summary: "Maps lifecycle resource manager delegation, execution authority and model selection to the existing Host and CLI contracts."
status: draft
proposal: PROP-local-orch-resource-manager
created_at: 2026-10-29
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
  - file: docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md
  - file: docs/architecture/ARCH-04-1-ecosystem-boundaries.md
  - file: docs/steering/glossary.md
---

# [PROP-local-orch-resource-manager-target] Target Living Spec for a reusable lifecycle resource manager

## 1. Capabilities and use cases

- `CAP-DLV-delivery-workflows`: add manager lifetime, first-use creation, reuse, job/result boundary, selected
  model level and recovery after context loss. Preserve one-shot Planning/Development workers.
- `CAP-INT-mcp-services`: distinguish Host business authority from delegated execution of exact approved effects.
  Preserve readiness, digest checks, route limits and partial-result recovery.
- `UC-drive-development-to-integration` and `UC-incubate-and-hand-off-a-proposal`: show delegated preparation,
  handoff, authorized execution and cleanup, including return to the Host for decisions.

## 2. Architecture and decisions

- `ARCH-04-1-ecosystem-boundaries`: separate Host decisions/supervision from manager execution, bounded to one
  conversation and repository.
- `docs/steering/glossary.md`: register the lifecycle resource manager and refine the Host definition if accepted.
- A Planning PADR records the execution boundary and evidence-based model default. On acceptance, supersede only
  affected Host-only clauses of `ADR-host-cli-lifecycle-authority` and `ADR-orchestration-workers`.

## 3. Agent assets and verification

Add the role under the spec bundle's `subagents/`. Update `spec-orchestrate`, `spec-delegate`, `spec-integrate` and
relevant worktree/handoff references. Keep dispatch and decision guidance in the Host; move operating procedures
to the manager. Existing distribution projection and model presets remain unchanged.

Add proportionate bundle contract/projection checks. Retain Planning evidence for repeated jobs, lightweight
versus mid-tier execution and main-context reduction. Record the provisional standard default, compact overrides
and Antigravity standard inheritance explicitly. Use native continuation mechanisms and identify untested
hosts rather than claiming complete live coverage.

## 4. Before and after

| Concern | Current behavior | Intended behavior |
| --- | --- | --- |
| Execution | Host reads instructions and operates CLI | Reusable manager operates existing CLI and returns concise results |
| Main context | Operations coexist with user decisions | Decisions, coordination and material exceptions remain |
| Lifetime | Planning/Development workers run one turn | Workers stay one-shot; manager serves recurring jobs |
| Model choice | Lifecycle operations use the Host model | Initial standard default with compact override; cross-host preset limits remain explicit |
| Authority | Host carries authority; CLI guards effects | Same authority and guards with explicit delegated execution |
