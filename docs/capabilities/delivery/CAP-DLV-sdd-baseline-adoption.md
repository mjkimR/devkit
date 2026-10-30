---
id: CAP-DLV-sdd-baseline-adoption
aliases:
  - CAP-DLV-incubation-sdd-baseline
title: SDD baseline adoption
summary: "An explicitly invoked spec playbook verifies the retained adaptive-development product through implementation, current documents and actual checks before an exact-effects SDD activation decision."
area: delivery
status: active
created_at: 2026-10-28
usecases:
  - UC-adopt-sdd-from-adaptive-development
  - UC-adopt-in-an-existing-repository
entrypoints:
  - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/sdd-baseline/SKILL.md
---

# [CAP-DLV-sdd-baseline-adoption] SDD baseline adoption

## 1. Summary

The `spec:core` bundle supplies the explicit `spec/sdd-baseline` playbook and its ordinary material report template.
It establishes an evidenced baseline for the user-selected retained adaptive-development product before subsequent
changes use SDD. `ADR-adopt-sdd-through-an-evidenced-baseline-playbook` selects this guidance procedure instead of a
new runtime, CLI or retrospective feature Unit. Baseline preparation can remain incomplete while the product stays in
adaptive development.

## 2. Scope & Boundary

- **In-Scope**: voluntary entry, retained-scope comparison, current-state document repair, actual project/usage
  evidence, a bounded material report, activation effects and partial-state recovery.
- **Out-of-Scope**: development-approach ownership and enforcement (`CAP-DLV-project-policy`); shared document
  formats (`CAP-DOCS-document-model`); legacy debt containment (`CAP-HARN-agent-guidance`); broad drift review
  (`CAP-DLV-drift-reconciliation`).
- **Scope Excluded**: automatic graduation, a new baseline CLI/workflow/Unit, reconstructed experimentation history,
  automatic legacy moves, unrelated product corrections and a universal SDD settings profile.

## 3. Business Rules & Policies

1. **Explicit entry**: WHEN the user invokes or confirms `sdd-baseline`, the coordinating agent MUST begin bounded
   preparation without changing the effective approach. Size, time and experiment count do not invoke it.
2. **Preparation state**: WHILE preparing the baseline, the agent MUST keep the approach adaptive-dev, including when
   installing the spec package or selecting SDD assets. Installed assets alone do not establish readiness.
3. **Retained coverage**: WHEN comparing retained product items, the agent MUST map behavior, important structure,
   current choices and verification methods to implementation, current documents and source-specific evidence.
   Each item is `verified`, `gap` or `excluded`; exclusions name their reason and never count as verified coverage.
4. **Actual evidence**: WHEN reporting verification, the agent MUST distinguish performed command/usage outcomes
   from failed, skipped or unavailable checks. Format-check success proves its checked conditions, not semantic readiness.
5. **Readiness threshold**: IF a retained-scope mismatch or required document/check/usage evidence gap remains,
   THEN the agent MUST leave adoption unready. A user-selected scope change may remove an excluded item from
   retained scope; a required retained item cannot be waived into readiness.
6. **Current choices**: WHEN drafting retained-choice documents, the agent MUST state current known reasons without
   invented past alternatives or approvals. Existing accurate documents and SDD history are preserved.
7. **Exact activation effects**: WHEN the ready source, retained scope and policy effects are presented, the agent
   MUST obtain or reuse explicit user authority bound to those same effects before activation. An existing spec
   integration provider remains; configuring a missing spec provider or a necessary project-to-spec provider change is presented and authorized explicitly.
8. **Evidence freshness**: IF relevant source or dirty content changes before activation, THEN the agent MUST
   revalidate affected evidence before claiming readiness.
9. **Partial failure**: IF installation, policy update or sync fails, THEN the agent MUST report actual partial
   state and supported recovery without claiming successful adoption or automatic rollback.
10. **Future routing**: WHEN activation completes, the agent MUST verify SDD inspection, selected guidance, sync
    consistency and ordinary SDD routing for subsequent work. The baseline itself creates no historical Unit or envelope.

Mechanical entry/reference assertions are in
`packages/devkit-spec/tests/integration/bundles/spec/test_sdd_baseline_guidance.py`.
Scripted sample-app exercises in `packages/devkit-spec/tests/e2e/bundles/spec/test_sdd_baseline_scenarios.py`
execute actual commands and label simulated user decisions. Retained-scope completeness remains semantic
coordinator/reviewer assessment; there is no deterministic baseline readiness engine.

## 4. Interfaces & Data Contracts

`uv run devkit playbook get spec/sdd-baseline` retrieves the procedure; retrieval authorizes no execution.
The report defaults to `docs/materials/<YYYY-MM>/<YYYYMMDD>-sdd-baseline/report.md`, or reuses the repository's
ordinary evidence location. It has no workflow binding, Unit anchor or lifecycle status.

The report records repository/HEAD and relevant dirty identity, selected scope and exclusions, retained-item
implementation/document/evidence links, actual commands/interactions and environments, outcomes/limits,
gaps/dispositions, ready effects, actual final state or recovery. Adaptive-dev current context is optional semantic input;
no filename or schema parser is required. Synthetic exercises identify simulated decisions separately from terminal observations.

Approach inspection uses `uv run devkit config show`: `configuration.development.approach` and
`sources["development.approach"]`. Authorized activation edits the shared `.devkit/config.toml` development
table and, when required and explicitly authorized, its integration provider. Existing approval/worktree/other
integration/project-check settings remain unchanged unless their change was authorized.

Completion checks run `uv run devkit sync`, `uv run devkit config show`, `uv run devkit spec policy` and
`uv run devkit sync --check`. Actual observations, not an expected result, establish completion. Subsequent
work uses the normal SDD route; existing command exit/error contracts remain with their owning capabilities.
