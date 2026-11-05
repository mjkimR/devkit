---
id: PROP-design-explore-counterarguments
title: Optional counterargument and response in design exploration
summary: "Extend the existing design critic with a bounded optional response and refinement exchange for consequential design disagreements."
status: draft
created_at: 2026-11-05
target_area: docs/capabilities/delivery/
priority: low
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/design_explore/
    - packages/devkit-catalog/tests/integration/bundles/test_design_explore.py
    - packages/devkit-catalog/tests/e2e/bundles/design_explore/
    - docs/capabilities/delivery/CAP-DLV-design-exploration.md
    - docs/usecases/delivery/
    - docs/decisions/
  excludes:
    - packages/devkit-spec/
    - packages/devkit-dist/
    - packages/devkit-catalog/src/devkit_catalog/deep_research/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-design-explore-counterarguments] Optional counterargument and response in design exploration

## 1. Background & Hypothesis

`CAP-DLV-design-exploration` already supplies independent solution exploration and an optional `design-critic`.
The orchestration reference normally allows one critique/refinement pass. The critic returns supported findings,
failure conditions and surviving benefits; zero findings is valid.

The missing explicit procedure is a response from the candidate's author to a concrete counterargument before the
coordinator makes a recommendation. A bounded exchange could expose unsupported objections and improve a design
without adding a permanent red/blue team or requiring consensus.

## 2. Technical Spike Questions

- **Q1 — Trigger:** Which unresolved assumptions or competing mechanisms warrant an exchange beyond the existing
  critique/refinement pass? Identify an example where a reply could change the choice.
- **Q2 — Role reuse:** Can solution-explorer and design-critic cover the exchange with explicit assignments, or is
  any additional role needed? Prefer role reuse unless a distinct responsibility is demonstrated.
- **Q3 — Independence:** What information is shared only after independent first passes to preserve distinct
  mechanisms and prevent the coordinator's preferred answer from becoming every role's premise?
- **Q4 — Stop condition:** What bounds a useful response, and how are unresolved disagreements returned without
  forced consensus, repeated persuasion or a mandatory minimum number of objections?

## 3. Proposed Design & Impact

Recommended starting direction, subject to Planning:

1. Keep small questions inline and existing independent exploration as the default.
2. When a consequential disagreement remains, give the critic the actual candidate and decision criteria. Require
   the objection's evidence, failure condition and effect on the choice.
3. Give the candidate's explorer one opportunity to accept the objection and revise, rebut it with evidence, or
   identify a bounded unknown. Treat the exchange as the existing critique/refinement pass made explicit.
4. Have the coordinator compare the actual response against the objection. Return the surviving alternatives,
   resolved issues and decision-changing uncertainties rather than votes or a manufactured winner.
5. Default to one exchange. An additional pass needs a specific unresolved question that can change the choice
   and an explicit effort bound; absence of disagreement requires no exchange.

Illustrative exchange: a critic identifies a stale-cache failure in a proposed ownership model; the explorer
supplies an invalidation mechanism or narrows the consistency promise; the coordinator judges that revised
mechanism against the user's latency and correctness requirements.

Changes are limited to design-explore's skill-local contracts, examples and their verification. Preserve its
conversation-first output, explicit invocation, optional roles and lack of implementation authority. No new feature
edge, shared subagent registration or runtime orchestration engine is proposed.

**Scope excluded:** mandatory red/blue teams, an adversarial debate for every design, voting/scoring, forced
consensus, experiments required to prove team superiority, and redesign of deep-research or SDD review roles.

## 4. Lifecycle & Retirement Criteria

This is a queued draft with `medium` Planning and Development effort and estimated size `M`. Priority is `low`
because the existing critic already addresses part of the need. It has no prerequisite proposal.

Planning is ready for acceptance when one concrete gap in the existing procedure, the optional trigger, response
contract and stopping condition are settled. If the existing wording already suffices, narrow this proposal to
examples or reject it rather than adding redundant orchestration.

Candidate Development acceptance checks:

- **AC1:** Given a simple design question or zero supported critic findings, the flow returns useful results
  without creating a debate or requiring extra roles.
- **AC2:** Given a decision-changing objection, one exchange records the evidence, the author's response or
  revision, and the coordinator's disposition of that specific objection.
- **AC3:** Given disagreement after the bound, the result names the unresolved assumption without claiming
  consensus or initiating unrequested implementation.
- **AC4:** Given no independent child contexts, inline passes are disclosed and never presented as independently
  produced agent findings.

Acceptance, rejection and handoff follow the existing proposal lifecycle.
