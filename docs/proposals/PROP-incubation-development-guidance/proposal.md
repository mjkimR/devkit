---
id: PROP-incubation-development-guidance
title: Develop and resume an idea without SDD lifecycle records
summary: Provides incubation entry guidance, optional product clarification, research
  and usage verification roles, and resumable current product context.
status: reviewing
created_at: 2026-10-28
target_area: delivery/
priority: medium
size: L
planning_effort: medium
dev_effort: medium
milestone: MS-idea-incubation
boundaries:
  owns:
  - packages/
  - docs/capabilities/
  - docs/usecases/
  - docs/architecture/
  - docs/decisions/
  - guides/
  excludes: []
task_kind: feature
workflow: sdd-proposal
depends_on:
- PROP-incubation-lifecycle-policy
---

# [PROP-incubation-development-guidance] Develop and resume an idea without SDD lifecycle records

## 1. Background & Hypothesis

MS-idea-incubation requires a development path from an incomplete idea to a working representative flow without per-change SDD Units. Existing SDD Planning and Backlog roles do not provide product discovery or incubation context. This is a new development experience rather than a structural refactor.

## 2. Technical Spike Questions

- **Q1**: Which bundle and package own incubation guidance without installing SDD entry obligations?
- **Q2**: How does the entry skill adapt interviews, brainstorming, bounded research and implementation to the next useful action?
- **Q3**: Which current-context artifact and role outputs allow a later session to resume without preserving discarded experiments?

## 3. Proposed Design & Impact

Provide an incubation entry skill, optional product clarification, research or feasibility, and actual-usage verification support. Define current goal, retained decisions, unresolved questions, observed results, run instructions and next action. Select exact asset ownership and context format during Planning.

Expected acceptance checks:

- An incomplete idea reaches a useful next action without a complete backlog or SDD Unit.
- Research or feasibility experiments expose evidence, limits and the decision informed.
- A representative app flow can be run and verified, then reconstructed within the agreed goal without per-change SDD records.
- Optional roles cover clarification, research and usage verification without mandatory invocation each iteration.
- A later session resumes from current context; abandoned choices can be replaced or removed.

- **Scope Excluded**: A universal application stack, scaffold catalog, mandatory SDD graduation, policy-engine implementation and baseline adoption.

## 4. Lifecycle & Retirement Criteria

Planning settles the direction before acceptance and handoff to one feature spec. If Planning finds independently deliverable work requiring multiple specs, return this draft for decomposition. This draft records remaining milestone scope; it claims no implemented or verified behavior.
