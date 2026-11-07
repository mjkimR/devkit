---
id: PROP-adaptive-task-contracts
title: Adaptive task decomposition and role specialization
summary: "Strengthen adaptive task decomposition and role overlays with explicit interfaces, ownership and completion evidence while preserving optional delegation."
status: draft
created_at: 2026-11-07
target_area: capabilities/delivery/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
  - packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/references/delegation.md
  - packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/references/orchestration.md
  - packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/roles/
  - packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/subagents/swarm-planner.md
  - packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py
  - docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  - docs/usecases/delivery/
  - docs/decisions/
  excludes:
  - packages/devkit-dist/src/
  - packages/devkit/src/
  - .devkit/managed/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-adaptive-task-contracts] Adaptive task decomposition and role specialization

## 1. Background & Hypothesis

CAP-DLV-adaptive-development already defines optional teams, bounded authority, isolated writers and aggregate
verification. Its architect, builder, qa-tester and reviewer overlays primarily restate assignment and return
boundaries. Architect partitioning names interfaces but does not explain when shared contracts prevent useful
parallel execution. Different files can still implement mutually incompatible interfaces.

The hypothesis is that deliverable-based partitioning and concise role-specific reasoning guidance improve
handoff quality without adding agents or imposing a fixed team sequence.

### Scope and exclusions

Strengthen existing partitioning and role overlays. Preserve caller-owned lifecycle authority, optional delegation,
source-specific evidence and serial fallback. New runtime scheduling, agent buses, public agent IDs, model routing,
feature dependency edges and mandatory planning artifacts are excluded.

## 2. Technical Spike Questions

- **Q1:** What minimum task brief identifies deliverable, owner, dependency, shared interface, completion condition
  and integration responsibility without duplicating the existing delegation payload?
- **Q2:** When should a shared interface be agreed before fanout, and when is direct or sequential work cheaper?
- **Q3:** Which checks distinguish the four overlays while keeping them short and compatible with external callers?

## 3. Proposed Design & Impact

### Candidate design

- Partition by independently checkable deliverables and dependency edges rather than by activity labels or file count.
- Before concurrent implementation, identify shared contracts and assign their ownership. Sequence unresolved
  foundational contracts before their consumers. Do not require a persisted DAG or task ledger.
- For each delegated unit, supply one owner, completion evidence, expected handoff and dependencies alongside the
  existing goal, permissions, absolute boundaries and source identity.
- Architect checks coupling, assumptions that invalidate the split and integration boundaries. Builder checks the
  agreed interface and failure handling. QA tests representative behavior and reproducing failures. Reviewer checks
  regression risk, caller compatibility, error handling and evidence, separating confirmed defects from hypotheses.
- Preserve conditional role loading and existing no-expanded-authority rules. Explain native versus emulated
  capabilities without promising enforcement from instructions alone.

### Expected acceptance scenarios

- **AC-01:** Given two disjoint file scopes sharing an unresolved API, when the coordinator partitions the work,
  then it identifies and assigns the API contract before dependent concurrent writes.
- **AC-02:** Given independent deliverables, when delegated, then each brief identifies one owner, dependencies,
  completion condition and expected integration handoff without requiring all roles.
- **AC-03:** Given an atomic change or unavailable isolation, when choosing execution, then direct or serial work
  preserves the same result evidence without manufacturing a team.
- **AC-04:** Given each overlay, when reviewed against a representative assignment, then its instructions supply
  distinct role-specific checks and preserve the execution agent's permission and lifecycle limits.
- **AC-05:** Catalog packaging, self-containment and projection checks pass. Those checks do not claim to establish
  model behavior; execution evaluation is tracked separately in PROP-adaptive-behavior-evaluation.

### Evidence and references

The comparison inspected documentation, not comparative execution performance:
- [OmO category and skill separation](https://github.com/code-yeongyu/oh-my-openagent/blob/HEAD/docs/reference/features.md).
- [VoltAgent task distributor](https://github.com/VoltAgent/awesome-codex-subagents/blob/HEAD/categories/09-meta-orchestration/task-distributor.toml).
- [VoltAgent reviewer](https://github.com/VoltAgent/awesome-codex-subagents/blob/HEAD/categories/04-quality-security/reviewer.toml).

Use these as design references, not vendored prompts or a requirement to retain their model defaults.

## 4. Lifecycle & Retirement Criteria

Keep this draft in Backlog until explicit pickup. Planning settles task-brief detail and overlay checks, then
acceptance and handoff follow the existing proposal lifecycle. One spec can deliver the guidance, affected asset
tests and Living Spec reconciliation. Completion requires the acceptance scenarios and relevant repository checks;
no runtime or model-performance claim follows from document validation.
