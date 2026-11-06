---
id: PLAN-adaptive-swarm-development
spec: SPEC-adaptive-swarm-development
---

# Technical Plan: Reusable Adaptive Subagents

## 1. Constitution & Invariant Review

`SPEC-adaptive-swarm-development` follows `ADR-skill-local-swarm-roles` and `ADR-worktree-isolated-parallel-workers`. Existing distribution projections, model policy and caller lifecycle remain authoritative. No new feature edges or runtime dependencies are introduced. `ARCH-05-2-components` permits catalog-owned content and mirrored integration/E2E tests.

## 2. Architecture Overview & Impact

Adaptive-dev owns three public archetypes, four local roles and conditional orchestration guidance. Core retains six assets and adds three archetypes; agents selects exactly those three. Scope the approach guard to adaptive product iteration; compatible external callers retain their own workflow. Product-support roles retain no-commit contracts. Writers can commit only when expressly assigned. Planner descendants remain read-only; verifier writes only assigned ignored outputs.

## 3. Component & Interface Design

Assignments carry goal, source/base, absolute readable role and ownership boundaries, permitted actions, checks, stop condition, depth/Host-wide allowance and expected return. Return status, exact source/commits, changed paths, commands/outcomes, defects and unverified areas. Overlay permissions intersect the archetype and caller authority. Resolve local roles from the loaded skill directory and external overlays by verified caller-owned absolute path. Prefer direct work; use flat or Host→lead→child only when useful and available, at most two child levels.

## 4. Error Handling & Edge Cases

Unknown/exhausted allowance or missing nesting selects direct/flat/serial execution without settings changes. Concurrent writers own separate worktrees; parent writes wait for child return. Verify actual changes before integration. Host owns final integration and current context. Preserve dirty/unmerged checkpoints on failure or interruption, collect children and record next action before cleanup. Bound repair in each assignment.

## 5. Verification & Test Plan

Connect real bundle selection, projections, extension collision, model policy and context preservation in catalog integration tests. Extend installed-wheel E2E without devkit-spec and agents-only under SDD. Retain semantic direct/flat/depth-two role-file exercises separately from packaging and native-runtime claims. Compare recorded Planning baseline to final projection counts/preset behavior; report native runtime and performance limits.

Run bundle validate/plan, just lint-check catalog, just check catalog, just test-affected --base 441bfde9603497c652d9cd6aac7c2688f0a2603a, and devkit rules check --ci --base main. Commit tested source, run selected E2E through devkit exec at a fixed ref, collect final result. Independent code-reviewer and reconcile-reviewer verify scope and Living Spec. Host verifies eventual landed HEAD independently.
