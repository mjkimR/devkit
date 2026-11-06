---
id: PADR-skill-local-swarm-roles
title: Swarm subagent and role architecture models
summary: For swarm subagents in adaptive development, we weigh skill-local roles against archetype and core-global hybrid models, to balance context footprint, native tool gating, and model specialization, retaining the choice for resolution in Planning.
proposal: PROP-adaptive-swarm-development
status: draft
created_at: 2026-11-06
---

# [PADR-skill-local-swarm-roles] Swarm subagent and role architecture models

- **Status**: Draft
- **Date**: 2026-11-06

---

## 1. Context & Problem Statement

Adaptive development requires specialized roles (coordinator, architect, builder, qa-tester, reviewer) to operate
as a rapid, autonomous development swarm. Unlike narrow single-task utilities (such as `deep-research`), rapid development
is a core activity impacting the entire repository. Registering all personas as global subagents creates severe system
prompt bloat and platform lock-in. Conversely, restricting all execution to pure skill-local role documents forces child
agents to inherit the coordinator's model tier and prevents native tool sandboxing (e.g. restricting an architect from
modifying files).

A balanced architectural model is required that provides necessary tool gating and model routing without global token bloat.

## 2. Decision Drivers

- **Context Window Economy**: Minimize persistent system prompt overhead across unrelated developer chat sessions.
- **Native Tool Sandboxing & Safety**: Enable host-level tool restrictions (e.g., read-only for planners, full execution for verifiers).
- **Cost & Speed Routing (Model Tiers)**: Allow high-speed/lower-cost models (e.g., Flash) for high-volume builders, while preserving reasoning models (e.g., Pro) for architecture and planning.
- **Persona Extensibility**: Allow developers to easily author or import specialized personas (from `agency-agents` or `awesome-codex-subagents`) without modifying global platform configurations.
- **Daily Ergonomics**: Support both autonomous multi-agent swarm execution and optional direct single-role invocation in chat.

## 3. Considered Options

- **Option 1: Pure Skill-Local Roles (Model 1)**: Zero registered subagents. The coordinator spawns general subagents and passes role markdown files on demand. Cleanest global footprint, but lacks native tool gating and model tier differentiation.
- **Option 2: Archetype Subagents + Role Overlays (Hybrid Model A)**: Register 2~3 broad capability archetypes globally (`swarm-planner`, `swarm-worker`, `swarm-verifier`) with tailored tool permissions and model tiers. The coordinator passes specialized `roles/<role>.md` files to the appropriate archetype at runtime.
- **Option 3: Core Global Subagents + Long-Tail Catalog (Hybrid Model B)**: Register 3 primary daily roles (`architect`, `builder`, `qa-tester`) globally for direct chat and swarm use, while maintaining long-tail/domain personas (security, ui, refactorer) as on-demand `roles/*.md` files.
- **Option 4: Fully Registered Static Subagents (Model 4)**: Register every persona as an independent global subagent. Maximizes native platform integration, but incurs unacceptable prompt overhead and platform-specific lock-in.

## 4. Decision Outcome

We frame the choice between **Option 2 (Archetype Subagents + Role Overlays)**, **Option 3 (Core Global + Long-Tail Catalog)**,
and **Option 1 (Pure Skill-Local)** as an active Planning spike to be resolved based on host platform capabilities and token measurements:

- The proposal retains the comparative evaluation of Hybrid Model A (Archetype Subagents) and Hybrid Model B (Core Global) alongside Pure Skill-Local Roles.
- In all candidate models, the long-tail persona catalog is authored and distributed as plain Markdown contracts under `roles/` within `devkit-catalog`. → `CAP-DLV-adaptive-development` rule 1 (MUST).
- If an archetype hybrid is selected, the bundle registers at most 3 functional archetypes to bound global context overhead.
- Planning will measure token footprints and verify whether host subagent invocations reliably accept dynamic role file payloads before final ADR acceptance.

## 5. Consequences

- **Positive**: Prevents premature architectural lock-in, enabling empirical measurement of token overhead vs. tool sandboxing benefits.
- **Positive**: Retains compatibility with upstream role libraries (`agency-agents`, `awesome-codex-subagents`).
- **Trade-off**: Requires Planning to define the exact invocation contract for passing role files to archetype subagents.
- **Follow-up**: Test whether the host environment (`Antigravity`, `OpenAgent`, `Codex`) reliably supports `invoke_subagent` with explicit file-path role assignments across subagent types.

## 6. Confirmation

Planning spike benchmarks will record token consumption, subagent startup latency, and tool permission enforcement across the candidate models before advancing the PADR to an accepted ADR.
