---
id: PROP-incubation-discovery-teams
title: Incubation discovery teams for product direction and roadmap
summary: "Extend opt-in incubation with host-orchestrated discovery teams that research ambiguous ideas, compare product directions, and prepare an evidence-backed initial document set and roadmap before development."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-29
target_area: delivery/
priority: high                        # critical | high | medium | low
size: L
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/incubation/bundle/
    - packages/devkit-catalog/tests/integration/bundles/
    - packages/devkit-catalog/tests/e2e/bundles/incubation/
    - packages/devkit-catalog/README.md
    - docs/capabilities/delivery/CAP-DLV-idea-incubation.md
    - docs/usecases/delivery/
    - docs/architecture/ARCH-05-2-components.md
    - docs/decisions/
  excludes:
    - packages/devkit/src/
    - packages/devkit-dist/src/
    - packages/devkit-spec/src/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-incubation-discovery-teams] Incubation discovery teams for product direction and roadmap

## 1. Background & Hypothesis
`CAP-DLV-idea-incubation` supports adaptive discovery, research, implementation and usage checks with optional
roles and mutable current context. Its present clarification guidance quickly narrows a candidate to a
representative implementation. Existing support roles do not define how a coordinator maintains several product
hypotheses, commissions broad research, compares evidence and prepares initial documents and a roadmap before
development.

The requested outcome is a reusable incubation-owned subagent configuration for ambiguous ideas and early
roadmaps. A master coordinates temporary teams and may use a devil's advocate to examine shared assumptions.
The hypothesis is that explicit exploration assignments and evidence-based synthesis can improve initial
direction-setting without introducing SDD lifecycle records or a new agent execution engine.

One feature can deliver and verify the bundle guidance, role contracts and document/roadmap handoff together.
The size is L because the coordination contract and semantic walkthroughs span discovery and artifact synthesis.

## 2. Technical Spike Questions
- **Q1**: Extend `/incubate`, add an optional focused discovery entry, or introduce a separate bundle?
- **Q2**: Which existing roles should expand, and which specialized contracts add a distinct responsibility?
- **Q3**: How should the master split, reconcile and stop independent investigations while preserving the user's
  goal, uncertainty, evidence limits and publication authority?
- **Q4**: What initial document set and roadmap can be useful before implementation without inventing current
  capabilities, settled architecture or SDD delivery commitments?
- **Q5**: Which bounded observed scenarios distinguish broader exploration from more agent activity or prose?

## 3. Proposed Design & Impact
Planning will compare alternative ownership and role configurations, draft the recommended orchestration and
artifact contract, identify Living Spec targets, and run an independent challenger before direction acceptance.
Planning effort and the recommended Development effort are medium.

Scope includes opt-in discovery-team guidance, bounded delegation, research provenance, competing product and
architecture hypotheses, optional adversarial examination, document synthesis, roadmap dependencies and resume.
Existing approach policy, projection mechanisms and user decision boundaries remain authoritative.

Scope Excluded: a swarm runtime, native host settings, automatic project approach changes, a new release wheel,
mandatory execution of all roles, automatic implementation or SDD adoption, and changes to the feedback handoff
pipeline. Incubation is not selected in this development checkout; inspect its source constitution without changing
repository configuration merely to author the proposal.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr incubation-discovery-teams "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept incubation-discovery-teams --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff incubation-discovery-teams.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
