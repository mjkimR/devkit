---
id: PROP-design-explore-counterarguments
title: Optional counterargument and response in design exploration
summary: "Extend the existing design critic with a bounded optional response and refinement exchange for consequential design disagreements."
status: accepted
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
    - docs/usecases/delivery/UC-explore-a-design-problem.md
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

Planning recommendation for direction acceptance:

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

### Planning decisions

- **Necessity and smaller alternative:** retain the existing three roles and one critique/refinement pass. The
  change makes the missing author response and per-objection coordinator disposition explicit. A permanent red/blue
  team adds a cast without filling another responsibility. Keeping only the existing wording leaves no instruction
  to let an author rebut a mistaken objection or mark a missing response.
- **Trigger:** use the exchange only when a supported objection can change a candidate's feasibility, tradeoff or
  recommendation against the actual goal or a hard constraint. Mere preference, a fixed objection quota and zero
  supported findings do not trigger it. A simple question remains inline.
- **Response packet:** after independent initial exploration, the coordinator passes the actual candidate,
  objection, evidence, failure condition, affected decision and unchanged constraints to its original explorer
  when available. Reuse the existing role with an explicit response assignment. If that explorer cannot return,
  the coordinator may analyze the response inline and discloses the limitation; it invents no author's return.
- **Response and judgment:** for each selected objection, the responder accepts and revises, rebuts with inspected
  evidence or an explicit inference, or names a bounded unknown. The coordinator returns the objection, actual
  response/revision, its own reasoned disposition and remaining decision-changing uncertainty. There is no required
  serialized schema, retained document, scoring or consensus.
- **Bound:** one critic pass and at most one author response per affected candidate in the normal exchange, followed
  by coordinator synthesis. The critic does not automatically get another reply. Before any further pass, name a
  concrete unresolved question that can change the recommendation and a finite pass/time bound. If there is no
  such check or the bound is reached, return the unresolved question and stop.
- **Failure and evidence:** unavailable sources, failed roles and unavailable fresh contexts stay visible. A response
  unsupported by inspected evidence is an inference or unknown, not a refutation proved by the role label.
- **Decision record:** `PADR-optional-design-critique-response` records this lasting capability refinement. It does
  not replace `ADR-explicit-solution-exploration`: invocation, role locality and output authority remain in force.
- **Delivery surface:** the intended contract drafts and exact source/test paths are in `target-docs.md`. No runtime,
  CLI, shared subagent metadata, package dependency, manifest asset, architecture edge or product screen is added.

## 4. Lifecycle & Retirement Criteria

This proposal is in Planning with `medium` Planning and Development effort and estimated size `M`. Priority is
`low` because the existing critic already addresses part of the need. It has no prerequisite proposal.

The direction is ready for acceptance after Challenger findings are folded or presented with their disposition.
The concrete gap, trigger, response packet and stop condition are specified above; no user fact is needed to
choose the proposed local instruction refinement.

Candidate Development acceptance checks:

- **AC1:** Given a simple design question or zero supported critic findings, the flow returns useful results
  without creating a debate or requiring extra roles.
- **AC2:** Given a decision-changing objection, one exchange records the evidence, the author's response or
  revision, and the coordinator's disposition of that specific objection.
- **AC3:** Given disagreement after the normal exchange, the coordinator returns the unresolved assumption; any
  additional pass starts only with a named decision-changing question and finite bound, and no implementation
  starts from exploration authority.
- **AC4:** Given no independent child contexts or an unavailable author response, inline passes and missing
  coverage are disclosed; the result contains no invented independent finding, author reply or agreement.
- **AC5:** Given an objection whose response is an unsupported inference or whose evidence is inaccessible, the
  synthesis retains that evidence limit instead of declaring the objection refuted.

Acceptance, rejection and handoff follow the existing proposal lifecycle.
