---
id: PROP-incubation-discovery-teams
title: Explicit incubation research entry and discovery teams
summary: "Add an explicit incubation research skill that coordinates bounded discovery teams to compare product directions and retain an evidence-backed initial document set and roadmap before development."
status: reviewing
created_at: 2026-10-29
target_area: delivery/
priority: medium
size: L
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/incubation/bundle/
    - packages/devkit-catalog/tests/integration/bundles/
    - packages/devkit-catalog/tests/e2e/bundles/incubation/
    - packages/devkit-catalog/README.md
    - docs/capabilities/delivery/CAP-DLV-idea-incubation.md
    - docs/usecases/delivery/
    - docs/decisions/
  excludes:
    - packages/devkit/src/
    - packages/devkit-dist/src/
    - packages/devkit-spec/src/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-incubation-discovery-teams] Explicit incubation research entry and discovery teams

## 1. Background & Hypothesis

`CAP-DLV-idea-incubation` supports next-action clarification, research, implementation and usage checks.
Its three optional roles help individual questions, but the guidance quickly narrows a candidate toward a
representative implementation. It does not define a research-team entry, independent product hypotheses,
cross-hypothesis criticism or synthesis into initial documents and a roadmap before development.

The intended outcome is an explicitly invoked skill in the existing opt-in incubation bundle. The invoking
Host is the master: it frames the research, commissions temporary teams, compares evidence, retains useful
documents and presents direction decisions to the user. A separate master subagent is unnecessary.

The hypothesis is that a distinct research entry and bounded assignments can broaden early exploration while
keeping existing lightweight incubation available. This is a testable guidance design, not evidence of globally
optimal decisions or improved model reliability. One feature can deliver the entry, roles, synthesis and semantic
walkthroughs together; size L does not require two specs.

## 2. Planning Questions and Recommendations

| Question | Recommendation and reason |
| --- | --- |
| Where should it live? | Keep it in `incubation:core` in devkit-catalog. It shares product context and approach policy, installs without devkit-spec, and adds no runtime package. |
| How does a user start? | Explicit `/incubate-research <idea or decision>`. Existing `/incubate` remains the iterative product entry; it can suggest research when helpful but does not silently start a broad team run. |
| Who is master? | The invoking Host, with adaptive task allocation and synthesis. Members return evidence or drafts and do not own user decisions. |
| Which roles? | Reuse product-clarifier and incubation-researcher; add direction-explorer, discovery-critic and discovery-planner. Keep usage-reviewer for relevant existing flows or prototypes. |
| What is the output? | A proportionate, project-owned research and planning set, linked from current context. Proposed behavior remains labelled as proposed; no automatic development or SDD commitments. |
| How is exploration bounded? | Each wave names its question, assignments, evidence limits and stop condition. The master revises assignments as findings arrive; native runtime limits remain host-owned. |

The entry preference is incorporated into this design. Placement, role ownership and artifact semantics are
captured by PADR-extend-incubation-with-optional-discovery-teams and
PADR-keep-discovery-plans-distinct-from-delivery-commitments.

## 3. User Entry and Expected Usage

Inputs are natural language, with existing documents or links when available. A user need not fill a form,
name agents or provide a complete backlog. Reuse known constraints and ask only missing decisions that change
the research target.

Examples:

```text
/incubate-research I want a tool for organizing technical research.
Compare current products and workarounds, explore different product directions,
and propose initial documents and a roadmap for a solo-maintained product.

/incubate-research Reconsider the direction in these product notes and roadmap.
Compare an independent product, an integration into an existing tool, and a local tool.

/incubate-research Evaluate local-first and server-backed designs for this intended workflow.
Find what evidence would change the architecture choice before we build it.
```

These are example prompts, not predetermined candidate sets or mandatory investigations.

The entry reads effective approach policy. Product discovery through this incubation entry requires
`approach=incubation`, as existing incubation does. Bundle installation and invocation never change approach.
Authoring these assets in devkit's own SDD repository does not activate the consumer entry.

A return includes the current question and scope, evidence coverage and limits, compared directions,
recommendation versus user decisions, resulting document paths, a conditional roadmap and the next decision
or useful investigation. Returning a draft recommendation is valid when evidence is insufficient for commitment.

## 4. Master and Team Contract

1. Recover current goal, user decisions, constraints, documents and unresolved alternatives. Separate fixed user
   constraints from implementation assumptions that remain open.
2. Frame the next decision and provisional comparison criteria before favoring an implementation. Broad initial
   scanning may refine the problem framing; it does not authorize inventing a product goal.
3. Select useful assignments and a bounded first wave. Use different questions or design premises rather than
   sending identical prompts to several agents. A small question can stay inline.
4. Give each assignment one goal, evidence starting points, a question or candidate lens, absolute boundaries,
   permitted tools/actions, expected return and a stop condition. State source/artifact identity and missing inputs.
5. For open direction, develop materially distinct hypotheses independently before sharing peer conclusions.
   Share confirmed facts and constraints. After first returns, direct communication may clarify evidence where
   the host supports it; a message grants no authority or scope change.
6. Validate source support, actual actions, uncertainty and boundaries before folding returns together. Merge
   duplicate investigations, pursue decision-changing gaps and stop low-value work.
7. Use discovery-critic when cross-candidate assumptions, important trade-offs or unsupported convergence need
   examination. Zero findings is valid. The critic can request a discriminating investigation; no finding requires
   an endless debate or forced consensus.
8. Compare credible surviving directions with the same relevant scenarios and criteria. Preserve incompatible
   assumptions instead of blending all suggested features into an incoherent product.
9. Choose the next permitted investigation, or present a provisional direction and decisions only the user can
   settle. User values and goal changes are not settled by model votes.
10. Ask discovery-planner to draft a proportionate document set and roadmap from the compared evidence. The Host
    checks and saves the retained synthesis, updates current context and reports unresolved decisions.
11. Stop this research action with its stated outcome and next action. Implementation starts only when the user
    has authorized it; no `/incubate`, SDD handoff or publication is implied by research completion.

Bounds describe task scope and research effort the coordinator can actually control. Exact token usage, hard
cancellation, slot enforcement and native sandbox guarantees are reported only when the host provides them.
There is no fixed agent count, hierarchy depth or required execution of every role. Existing host permissions,
refusal handling and boundary checks remain in force; a missing native role is not silently represented as run.

### Role set

| Role | Assignment | Return and boundary |
| --- | --- | --- |
| product-clarifier, retained | User/problem framing, candidate user groups, success signals and genuinely missing decisions | Evidence-backed framing and questions; no invented user decision |
| incubation-researcher, retained | One market, competitor, alternative workflow, domain or technical question per instance | Claim/source map, observations, contradictions, unknowns and next check; experiments only in explicitly assigned boundaries |
| direction-explorer, added | Develop one product or architecture hypothesis from a distinct premise | Target usage, value, trade-offs, critical assumptions, failure evidence and smallest discriminating test; no production implementation |
| discovery-critic, added | Examine the question, candidate set, shared assumptions, evidence and proposed selection | Supported failure conditions and smaller alternatives; no obligation to invent objections, choose a winner or edit files |
| discovery-planner, added | Synthesize compared evidence and a provisional/user-selected direction | Draft initial document sections and conditional roadmap with evidence links; no invented approvals, dates or delivery Units |
| usage-reviewer, retained | Exercise an available representative flow or prototype when actual interaction can inform a choice | Expected/observed behavior and coverage; no fabricated user validation or product-source repair |

New discovery roles return drafts or evidence by default. Only the Host writes current context and retained
synthesis. Existing researcher experiment writes remain a separately assigned permission, not a team-wide grant.

## 5. Research, Initial Documents and Roadmap

Research should cover the questions needed to distinguish viable directions. Relevant comparisons can include
direct competitors, adjacent products and current manual workarounds. Record source links, date/version when
material, what was actually inspected, the claim supported and what remains inference. Product marketing is
evidence of a vendor claim, not proof of user adoption or observed usability. An AI-generated user persona or
mock interview is an assumption exercise, not a real user's behavior.

Default logical contents are:

- Product brief: intended users, problem, representative usage, value hypothesis, constraints and proposed scope.
- Research and alternatives: source-backed findings, unknowns, materially distinct directions and trade-offs.
- Direction and architecture notes: recommendation, actual user decisions, assumptions, consequential choices
  to test or defer, and conditions that would reopen a surviving alternative.
- Initial roadmap: outcomes or questions per horizon, ordering/dependencies, validation signals and conditional
  implementation slices. Research work and build work are distinguishable; speculative delivery dates are omitted.

These contents may be one note for a small question or several linked notes for a broad initial investigation.
Reuse useful existing files. With no existing destination, use project-owned notes under `docs/materials/`,
labelled as discovery/planning rather than current product contracts. Use ordinary evidence notes where no indexed
identity is needed; follow installed document instructions for any indexed material. No new document kind or
parser is introduced. The coordinator keeps exact links and current uncertainties in `.devkit/incubation.md`.

Native capability/use-case/decision documents are used only when their semantic subject and authoring policy
apply. A discovery roadmap is not automatically an MS milestone, proposal catalog, work unit or execution promise.
A user explicitly choosing existing milestone semantics can use the installed document conventions, without
making devkit-spec a dependency of this research entry.

The output must expose missing evidence. A research budget ending without a reliable choice yields a useful
partial synthesis and next investigation, not a fabricated winner or completion claim.

## 6. Acceptance and Verification Intent

Development will turn these scenarios into detailed spec AC and record actual walkthrough evidence.

| Scenario | Observable outcome |
| --- | --- |
| Ambiguous initial idea | The entry reuses known facts, identifies the decision and asks only consequential missing information; it does not force a framework or select a product goal for the user. |
| Competing directions | The master commissions distinct premises before sharing peer conclusions, then compares the returned assumptions and evidence under common criteria. A lone viable candidate has an explicit constraint/evidence explanation. |
| Broad competitor research | A bounded sample of claimed comparisons is traceable to inspected primary sources, while marketing claims, stale facts, user behavior and unknowns remain distinguishable. |
| Cross-hypothesis criticism | A critic catches a supported common assumption or evidence gap, or legitimately returns no finding; neither consensus nor an arbitrary score establishes correctness. |
| Document and roadmap synthesis | Proposed behavior stays proposed, unknowns survive synthesis, dependencies are coherent, and research completion creates no implicit implementation authority or SDD records. |
| Fresh-context resume | Another context can recover current candidates, evidence, decisions and reopening conditions from retained files without replaying the conversation. |
| Small existing question | The coordinator can work inline or use one role; no mandatory team, document suite or criticism round appears. |
| SDD/invalid approach | The consumer research entry follows existing incubation policy and performs no product writes or implicit approach switch. |
| Docs/catalog-only consumer | The explicit entry and six optional roles distribute/project without devkit-spec, and new contracts use no SDD-only invocation or envelope command. |
| Unavailable delegation or budget exhaustion | The result names missing role coverage/remaining questions and returns a bounded partial result; no role result, evidence or hard runtime guarantee is fabricated. |

Use manifest, projection, reference and installation tests in the existing catalog test tiers. Re-run
`just test-affected`, relevant lint/type checks and rules for the implementation. Test inherited role IDs and
current-context preservation; consumer installation continues to exclude devkit-spec.

Semantic confirmation requires observed bounded agent exercises, not just keyword assertions. Compare the
existing guidance and candidate guidance on the same small discovery fixtures with identified inputs, host/model
settings and bounds. Include an ambiguous product, an architecture trade-off, and a competitor claim with
contradictory or unavailable evidence. Review candidate distinctness, source support, unsupported commitments,
resume fidelity and coordinator effort. Replayed synthetic role returns test fold-back handling only and must be
labelled as such. If actual delegated execution is unavailable, that coverage remains unverified for the user.
These exercises provide bounded evidence, not a claim of universal discovery quality.

## 7. Impact, Non-Goals and Planning Status

Owned implementation targets are incubation assets, catalog README/tests, `CAP-DLV-idea-incubation`, the existing
incubation use case and a focused research use case. The package/component boundary remains content-only.
The two PADRs cover role/entry ownership and the distinction between discovery outputs and delivery commitments.

Scope Excluded: a swarm runtime, cross-host agent bus, scheduler, model router, new wheel, automatic approach
switching, fixed management tiers, production implementation by the research entry, SDD adoption and changes to
the existing feedback handoff pipeline. Native P2P is optional host functionality; structured returns suffice.

Planning uses medium effort. Current evidence is contract/asset inspection, primary-source pattern research and
independent scout analysis and a zero-finding challenger review. The proposal-targeted and committed-snapshot
governance checks passed with 21 rules and no findings; affected documentation tests passed 12 tests. A pytest
cache-write warning did not affect those results. Role implementation and semantic quality are not yet verified. The bundle is not selected
in this development checkout, so source authoring does not require activating it here.

## 8. Lifecycle

The user's request supplies plan intent. Direction acceptance and Development handoff remain separate configured
boundaries. Planning ends with a reviewed, committed proposal, evidence, PADRs and Living Spec blueprint.
Development begins only after the applicable user decisions; this proposal does not itself ship or activate roles.
