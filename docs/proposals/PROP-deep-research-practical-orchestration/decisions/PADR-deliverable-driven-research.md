---
id: PADR-deliverable-driven-research
title: Keep research oriented to the requested deliverable
summary: "For bounded research, we align assignments and synthesis with the requested deliverable and use selective verification, accepting semantic review instead of a mandatory effectiveness benchmark."
proposal: PROP-deep-research-practical-orchestration
status: draft
created_at: 2026-11-05
---

# [PADR-deliverable-driven-research] Keep research oriented to the requested deliverable

## 1. Context & Problem Statement

A bounded research team can produce supported findings while missing the artifact the user needs or imposing
unwanted follow-up work. Repeating all investigator searches also duplicates work without necessarily addressing
the consequential evidence gap. `MAT-agent-team-design-pilot` records these operational observations without a
comparative performance claim.

## 2. Decision Drivers

- Deliver the requested practical output under the user's stated constraints.
- Preserve factual qualification, source provenance and actual access restrictions.
- Keep coordination and follow-up proportionate to a bounded question.
- Retain opt-in roles and existing distribution/runtime boundaries.

## 3. Considered Options

- Keep factual validation and generic research synthesis: simple, but it leaves output fit and unwanted
  prerequisites implicit.
- Add a mandatory critic and effectiveness comparison: explicit checks, but it adds cost even when a small
  request can finish inline and conflicts with a declined validation program.
- Use deliverable-driven assignments and a coordinator-owned usefulness check with selective verification:
  addresses output fit while retaining judgment about consequential source gaps.

## 4. Decision Outcome

Choose deliverable-driven assignments and coordinator-owned checks because they make output fit visible without
adding a required role or experiment.

- The run brief names the requested deliverable, intended use, known constraints and stop condition; assignments
  identify their contribution. → `CAP-DLV-deep-research` proposed deliverable-framing rule (SHOULD).
- The coordinator checks requested artifacts, intended next action and unnecessary prerequisites before retention;
  an optional critic receives these criteria when relevant. → `CAP-DLV-deep-research` proposed usefulness rule (SHOULD).
- Source reopening targets consequential gaps, conflicts or suspect support rather than repeating every
  investigation. → `CAP-DLV-deep-research` proposed selective-verification rule (SHOULD).
- An ordinary retrieval failure permits bounded authorized recovery; definite refusal or ambiguous authorization
  stops access to that resource. → `CAP-DLV-deep-research` proposed retrieval-recovery rule (MUST).
- Declined comparative validation is not an adoption prerequisite; uncertain benefits remain explicit.
  → `CAP-DLV-deep-research` proposed proportionate-follow-up rule (MUST).

These clauses refine research operation; they replace no earlier ADR decision and change no material immutability,
citation, implementation, Git or publication authority.

## 5. Consequences

- A practical-reference request can yield useful repo/file guidance in its first retained answer.
- Useful criticism remains available without requiring another agent on every run.
- The coordinator still judges source sufficiency; selective verification can miss a weak claim, so decisive gaps
  remain grounds for a targeted source check or an explicit unverified statement.
- Recovery consumes the original research bound. Missing coverage remains visible when that bound ends.
- Revisit a specific wording defect when ordinary use exposes it; no benefit-validation program is required.

## 6. Confirmation

Review only for output usefulness and selective research judgment: review the semantic examples in the proposal's
`target-docs.md` against the changed source instructions and `CAP-DLV-deep-research`.

Run the existing integration and installed-consumer checks under
`packages/devkit-catalog/tests/integration/bundles/test_deep_research.py` and
`packages/devkit-catalog/tests/e2e/bundles/deep_research/` for opt-in deployment, local-role ownership and explicit
retention/authority boundaries. These checks do not measure empirical effectiveness.
