---
id: PROP-adaptive-swarm-development-target
title: Target Living Spec Structure for PROP-adaptive-swarm-development
status: draft
proposal: PROP-adaptive-swarm-development
created_at: 2026-11-06
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  - file: docs/usecases/delivery/UC-advance-an-idea.md
---

# [Blueprint] PROP-adaptive-swarm-development: Target Living Spec Structure for Agent Swarm-driven Rapid Development in Adaptive Mode

This document defines the target blueprint of how the `docs/` backbone (Living Spec) will evolve if proposal
PROP-adaptive-swarm-development is accepted. It represents a hypothesis plan subject to adjustment during implementation.
Upon handoff, it is copied into `specs/` to serve as a baseline for `plan.md` boundaries and `reconcile.md` targets.

---

## 1. System Capabilities Plan (docs/capabilities/)

### 1.1 `CAP-DLV-adaptive-development` Updates
- **Scope & Role Expansion**:
  - Update Section 1 (Summary) and Section 2 (Scope) to formally include the autonomous multi-agent swarm pipeline alongside
    the existing ideation/clarification roles.
  - Clarify that while explicit research teams remain a separate bundle (`CAP-DLV-deep-research`), code authoring swarms are
    natively supported within `adaptive-dev`.
- **Business Rules and Policies (Updates & Additions)**:
  - **Rule 1 (Distribution and subagents)**: State that swarm role definitions are authored under `roles/` inside
    the bundle, and Planning resolves whether they are invoked purely via dynamic file contracts or paired with 2~3 functional
    archetype subagents (`PADR-skill-local-swarm-roles`).
  - **Rule 12 (Support roles)**: Expand optional support delegation to distinguish between ideation roles (`product-clarifier`,
    `product-researcher`, `usage-reviewer`) and execution swarm roles (`architect`, `builder`, `qa-tester`, `reviewer`).
  - **Rule 13 (Role boundaries & Worktree isolation)**: Add clause that when parallel builders are dispatched, the coordinator
    MUST supply disjoint file touch boundaries (`_Boundary`) or assign isolated git worktrees created via devkit's worktree
    lifecycle (`PADR-worktree-isolated-parallel-workers`).
  - **New Rule (Sprint Contract)**: WHEN the coordinator initiates swarm execution, the Architect role MUST establish a
    Sprint Contract defining target interface signatures and builder file allocations before implementation begins.
  - **New Rule (Adversarial QA Gate)**: BEFORE completing a swarm sprint or updating mutable context, the QA Tester MUST
    execute `just test-affected` and verify zero lint, type, or test regressions.

---

## 2. Use Cases Plan (docs/usecases/)

### 2.1 `UC-advance-an-idea`
- **Main Success Scenario Updates**:
  1. User invokes `/adaptive-dev` with a feature request or rapid development goal.
  2. Coordinator checks active approach (`[development] approach = "adaptive-dev"`).
  3. Coordinator delegates to `architect.md` to analyze requirements and generate a Sprint Contract with interface contracts
     and disjoint file boundaries.
  4. Coordinator dispatches parallel `builder.md` subagents in dedicated worktrees or assigned boundaries.
  5. Builders author code and unit tests, verifying locally.
  6. Coordinator integrates worker branches into the active branch.
  7. Coordinator delegates to `qa-tester.md` to run `just test-affected`, `just check`, and `just lint-check`.
  8. If defects are found, the QA Tester produces exact failure traces and routes them back to the responsible Builder for repair.
  9. Coordinator delegates to `reviewer.md` for a sanity check on diff cleanliness and boundary compliance.
  10. Coordinator records updated facts in `.devkit/adaptive-dev.md` and reports completion with verification results to the user.
- **Extensions**:
  - *3a. Goal requires ideation/clarification rather than coding*: Coordinator routes to `product-clarifier` or `product-researcher`
    instead of the execution swarm.
  - *5a. Builder encounters unresolvable dependency contradiction*: Worker pauses and reports blocker to Coordinator for replanning.
  - *7a. QA Tester discovers test regressions*: Defect report is routed back to Step 4 for targeted builder remediation (at most 2 iterations).

---

## 3. Architecture & Decision Impact (docs/architecture/ & docs/decisions/)

### 3.1 `docs/architecture/ARCH-05-2-components.md`
- Clarify catalog bundle ownership for `adaptive-dev`: `devkit_catalog/adaptive_dev/bundle/` houses the skill, `roles/`
  (`architect.md`, `builder.md`, `qa-tester.md`, `reviewer.md`), and `references/` (`orchestration.md`, `sprint-contract.md`).

### 3.2 Promoted ADRs (docs/decisions/)
- `PADR-skill-local-swarm-roles` graduates to an accepted ADR upon proposal acceptance.
- `PADR-worktree-isolated-parallel-workers` graduates to an accepted ADR upon proposal acceptance.

---

## 4. Development Conventions & Governance (docs/development/ & .devkit/)

- **Bundle Layout for `adaptive-dev`**:
  ```text
  packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/
  ├── bundle.toml
  ├── AGENTS.md
  ├── skills/
  │   └── adaptive-dev/
  │       ├── SKILL.md
  │       ├── references/
  │       │   ├── discovery.md
  │       │   ├── evidence-and-iteration.md
  │       │   ├── orchestration.md
  │       │   └── sprint-contract.md
  │       └── roles/
  │           ├── architect.md
  │           ├── builder.md
  │           ├── qa-tester.md
  │           ├── reviewer.md
  │           ├── product-clarifier.md
  │           ├── product-researcher.md
  │           └── usage-reviewer.md
  └── templates/
      └── adaptive-dev.md
  ```
- **Testing & Packaging**:
  - `packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py` verifies all role files exist, remain under 12KB,
    and project no native subagents.
  - `packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py` verifies clean installation from wheel.

---

## 5. System Before & After Comparison (Before & After)

| Aspect | As-Is (Current SDD vs. Adaptive-dev) | To-Be (Proposed Adaptive Swarm Mode) |
| :--- | :--- | :--- |
| **Execution Flow** | SDD: Strict serial pipeline (`spec` → `plan` → `tasks` → `develop` → `review` → `sync`).<br/>Adaptive: Early-stage ideation only. | Adaptive: Fast, parallel 4-stage swarm (Sprint Contract → Parallel Builders → Adversarial QA → Checkpoint). |
| **Concurrency & Workers** | SDD: One worker per task turn in serial worktree.<br/>Adaptive: No code execution workers. | Adaptive: N parallel builders operating concurrently in isolated worktrees or disjoint file boundaries. |
| **Artifact Overhead** | High ceremony: `spec.md`, `plan.md`, `tasks.md`, `reconcile.md`, worker envelopes, PADRs. | Zero ceremony: Lightweight Sprint Contract + active state in `.devkit/adaptive-dev.md`. |
| **Collision Protection** | Controlled via strict task boundaries and manual integration. | Automated via Architect boundary contracts and git worktree isolation (`devkit worktree`). |
| **Verification Gate** | Heavy review and reconcile checks across full Living Spec. | Fast, automated verification via `just test-affected` run by a dedicated QA Tester role. |
| **Graduation Path** | Pre-determined before work begins. | Voluntary: Rapid prototyping in swarm mode, with optional SDD adoption when stable. |
