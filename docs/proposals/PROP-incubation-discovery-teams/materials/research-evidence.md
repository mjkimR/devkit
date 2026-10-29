# Research evidence and alternatives

This note supports PROP-incubation-discovery-teams. Observations concern the inspected contracts and source
assets at Planning input `4ef0edc2b9f78fb50a0b7346f74103bbbcfeed2b`. No new role implementation or live
discovery-team exercise has run in Planning.

## Existing mechanisms and gaps

- `CAP-DLV-idea-incubation` already permits adaptive evidence-driven iteration, optional roles and mutable context.
- `skills/incubate/references/discovery.md` lines 3–9 compare a few candidates and then select a narrow first
  implementation. This is a plausible early-convergence risk, not a measured reliability defect.
- Existing product-clarifier handles framing and next questions, incubation-researcher one uncertainty per call,
  and usage-reviewer observed interaction. Their contracts do not supply an end-to-end alternative designer,
  cross-candidate critic or initial document/roadmap synthesis assignment.
- Shared distribution projects role contracts across hosts. Existing evidence and boundary validation can be
  reused; adding an execution engine or separate master process is unsupported by the present need.

## Placement and entry alternatives

| Option | Benefit | Cost/risk | Disposition |
| --- | --- | --- | --- |
| Expand only automatic routing in `/incubate` | Few entry names; same current context | A small question may trigger wide research or team cost without the user selecting that activity | Keep existing lightweight routing; not the preferred broad-team entry |
| Explicit `/incubate-research` in incubation | Clear user intent; shared product context and optional roles; no additional package | One additional skill and conditional references to maintain | Recommended; incorporates the explicit-entry preference |
| Separate discovery bundle or wheel | Could serve unrelated research outside product incubation | Extra selection and duplicated policy/context conventions; independent ownership not established | Not needed for this bounded feature |
| Full swarm runtime | Could own native scheduling and communications | New execution dependencies, host-specific enforcement and infrastructure unrelated to the guidance gap | Outside scope |

## Role configuration alternatives

A department-only split (market, frontend, backend) can deepen one shared product assumption. Use common
research assignments plus independent candidate lenses when direction is open. One generic researcher can be
instantiated for several bounded topics. A separate research role per industry or data source is unnecessary.

Add only three distinct responsibilities: developing one alternative, examining shared assumptions, and drafting
evidence-backed planning artifacts. Keep the invoking Host as master and preserve all existing role IDs.
The critic is not required for every action and need not invent findings.

## Artifact evidence from the independent scout

The scout inspected the document system and returned a read-only report against the same head.

- Current context already permits useful document links and mutable resume facts
  (`CAP-DLV-idea-incubation`, current-context section).
- Docs-bundle `seed/docs/README.md` assigns research/experiment evidence to `docs/materials/` and leaves
  approvals/retention to the selected approach.
- `CAP-DOCS-document-model` defines indexed material, but no dedicated discovery material template. Free-form
  evidence notes can remain proportionate; use indexed material semantics only when identity is needed.
- Capability/use-case/decision templates carry stronger meanings than an unvalidated product hypothesis.
  Keep proposed behavior and recommendations labelled, and apply native authoring rules when actually used.
- `ADR-roadmap-and-milestones` and the milestone template carry explicit goal, exit, membership and review
  semantics. A discovery roadmap is not an implicit use of those delivery commitments.
- Existing contracts and deterministic format checks do not establish research truth or planning quality.
  Bounded observed agent walkthroughs and artifact inspection are required for semantic evidence.

The scout result is recorded in this proposal's scout envelope. No scout writes, index changes or HEAD changes
occurred; before/after snapshot was `e5776fe1ff913d5bec358743fe641dbfdcd39697`.

## Primary-source patterns

Sources were inspected during the preceding research in this task's conversation. They motivate design choices,
not proof of this proposal's effectiveness.

- [Anthropic, Building effective agents](https://www.anthropic.com/research/building-effective-agents),
  2024-12-19: orchestrator–workers supports dynamic decomposition; evaluator–optimizer is suited to clear
  evaluation criteria. This informs separate generation, comparison and research assignments.
- [Anthropic, multi-agent research system](https://www.anthropic.com/research/multi-agent-research-system),
  2025-06-13: explicit task division and independent context help broad research, while dependencies and token
  cost constrain its suitability. No reported benchmark is extrapolated to product strategy or this role set.
- [Product Talk, Opportunity Solution Trees](https://www.producttalk.org/opportunity-solution-trees/):
  compare solutions through underlying assumptions and tests. The framework is not a complete product/company
  strategy method; it informs discriminating experiments.
- [Doshi and Hauser, creativity and diversity study](https://arxiv.org/abs/2312.00506), version 2024-03-14:
  AI-assisted short stories became more similar. This is a caution about relying on generated diversity,
  not direct evidence about software product strategy or multi-agent superiority.

## Proposed evaluation boundary

Development should observe real bounded agent runs on matched fixtures with candidate/base guidance,
identifiable inputs and host/model bounds. Review whether candidates differ materially, claims have supporting
sources, counter-evidence changes the synthesis, missing facts remain explicit and another context can resume.
Synthetic role-return fixtures can exercise fold-back behavior but cannot substitute for live research evidence.
There is no proposed minimum token savings, numeric quality score or global-optimality claim.
