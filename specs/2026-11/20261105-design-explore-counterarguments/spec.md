---
id: SPEC-design-explore-counterarguments
title: Optional counterargument and response in design exploration
summary: "Make one optional author response and coordinator disposition explicit within the existing design critique pass, preserving evidence limits and exploration authority."
status: in-progress
created: 2026-11-05
related_capabilities:
  - CAP-DLV-design-exploration
related_usecases:
  - UC-explore-a-design-problem
workflow: sdd-spec-feature
---

# [SPEC-design-explore-counterarguments] Optional design critique responses

## 1. Problem Statement & Motivation

`CAP-DLV-design-exploration` permits optional criticism and one refinement pass, but the shipped role instructions
omit the candidate author's response and the coordinator's disposition of each objection. Make that exchange
explicit under `ADR-optional-design-critique-response` without adding a role or execution runtime.
The retained Planning comparison is in `docs/materials/2026-11/20261105-design-explore-counterarguments/`.

## 2. User Stories

- **US-1:** As a developer choosing a design, I want a consequential objection tested against the author's actual
  response so a mistaken or answered objection does not silently determine the recommendation.
- **US-2:** As a coordinator, I want a bounded optional exchange with honest missing-response and evidence handling
  so simple questions stay simple and unresolved disagreements remain visible.

## 3. Non-Goals

- **Scope Excluded:** mandatory red/blue teams, fixed casts or objection quotas, voting/scoring, consensus,
  new global roles, runtime orchestration, automatic companion invocation, implementation authority and experiments
  required to prove team superiority.
- **Scope Excluded:** changes to deep-research, delivery workflow policy, manifests, package dependencies or interfaces.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Simple questions and zero findings need no exchange

- **Given** a small design question or no supported decision-changing critic finding.
- **When** the coordinator chooses useful work.
- **Then** the instructions permit inline exploration and zero findings without requiring a critic, author reply,
  fixed cast, debate or objection quota.

### [AC-02] A supported objection receives an actual response and disposition

- **Given** independent initial candidates and an objection that can change feasibility, a consequential tradeoff
  or recommendation against the goal or hard constraints.
- **When** the coordinator selects it for the existing optional critique/refinement pass.
- **Then** the explorer receives the actual candidate, objection, evidence, failure condition, affected choice and
  preserved constraints; it accepts and revises, rebuts with labeled support, or names a bounded unknown.
- **Then** synthesis identifies each selected objection, its actual response/revision and reasoned coordinator
  disposition, with no required serialized schema or retained document.

### [AC-03] The normal exchange is bounded

- **Given** a disagreement after one critic pass and at most one author response per affected candidate.
- **When** the coordinator completes synthesis or selects further work.
- **Then** it returns the unresolved assumption unless a concrete decision-changing question and finite pass/time
  bound are named before another pass; the critic receives no automatic reply and no implementation starts.

### [AC-04] Missing returns and shared contexts remain explicit

- **Given** an unavailable author response or no independent child contexts.
- **When** the coordinator analyzes an objection inline or synthesizes available returns.
- **Then** it discloses missing coverage or shared context and invents no independent finding, author reply or
  agreement; inline analysis is identified as the coordinator's own.

### [AC-05] A response cannot manufacture evidence

- **Given** a rebuttal based on an uninspected claim, unavailable citation or inference.
- **When** the coordinator judges it against the objection.
- **Then** it distinguishes inspected support, inference and unknowns and retains the consequential evidence limit
  instead of declaring the objection refuted solely because a role asserted it.

## 5. Assumptions and Verification Limits

- Existing solution-explorer and design-critic roles cover the response; their initial independent pass remains
  separate from the later response assignment. No accepted invocation, source-access or output-authority clause changes.
- This work ships instructions. Integration and wheel-consumer checks establish content, optionality and packaging;
  semantic review walks the scenarios. They do not measure model obedience or improved design quality.
- No product screen changes or before/after performance/count claim is proposed.
- Design-explore is not selected in the authoring checkout. Read its source contract and test opt-in deployment in
  isolated consumers; keep the project's selection unchanged. Initial `devkit sync --check` passed.
