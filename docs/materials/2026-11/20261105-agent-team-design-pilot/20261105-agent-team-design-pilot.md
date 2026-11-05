---
id: MAT-agent-team-design-pilot
created_at: 2026-11-05
summary: "Evidence and provisional operating patterns for explicitly invoked agent teams supporting UX improvement, divergent ideation and research, with reusable repository references, a bounded deep-research pilot and a lightweight adoption path."
---

# [MAT-agent-team-design-pilot] Optional agent teams for UX and divergent ideation

## Research outcome

For UI/UX improvement and idea discovery, adopt useful existing role and design instructions through an
explicitly invoked skill. Use `agency-agents` for role definitions, `impeccable` for design guidance and Anthropic's
Cookbook for research delegation. Keep the existing deep-research-style coordinator and plain role files.
No same-task comparison, benchmark or proof of team superiority is a prerequisite for adoption. The user rejects
the cost of that validation program and prefers using a small configuration, then adjusting friction as it appears.
Team superiority remains unverified; that evidence limit does not block this practical adoption path.

The useful design variable is the division of evidence, premises and outputs. Personality labels alone do not
establish diversity. Repository selection and operating sketches below are recommendations the user asked to
retain. They are not implemented capabilities, delivered skills or authorization to begin implementation.

## Brief and actual user decisions

The user has two goals: pilot the deep-research bundle and find references for useful agent-team configurations.
The motivating problem is ordinary UI/UX suggestions and idea lists from a single agent. Candidate roles include
criticism, unconventional ideation and web reference discovery. Intended usage is a personal coding/design
workflow where the owner judges alternatives before a separate implementation request.

The user chose an explicitly invoked skill plus role Markdown files, modeled on the deep-research bundle.
Avoiding influence on unrelated work is a constraint. The user explicitly declined same-task comparisons and
validation until a benefit is established because the combined time, token and attention costs are too high.
They requested reusable repository references and accepted retaining the recommended lightweight direction.
No product, screenshots, user observations or existing prototype were supplied. No skill implementation or
publication was requested. A dedicated worktree was subsequently requested for this material update.

This investigation compared task suitability, operating alternatives and relevant primary evidence. It did not
produce a product redesign, test real users, measure team quality against a baseline or benchmark model choice.

## Reusable repository references

The coordinator inspected the following upstream repository pages and linked files on 2026-11-05. Links use
upstream `main`, so they identify inspected locations rather than immutable revisions. These are source and
configuration references; no installation or runtime test of these repositories was performed.

### Agency Agents: role definitions and team composition

[msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) is the closest reference for the user's
idea of specialists with different personalities and responsibilities. Roles are Markdown files grouped by field.
Useful starting locations are:

- [Design roles](https://github.com/msitarzewski/agency-agents/tree/main/design): UI Designer, UX Researcher and
  UX Architect illustrate responsibility separation.
- [Whimsy Injector](https://github.com/msitarzewski/agency-agents/blob/main/design/design-whimsy-injector.md):
  playful interactions, microcopy and unexpected moments. Its scope is delight and brand expression rather than
  general product invention; broaden the assignment when using it as inspiration for a wild ideator.
- [Reality Checker](https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-reality-checker.md):
  a skeptical review perspective. Do not import its default `NEEDS WORK`, automatic first-pass incompleteness
  or prescribed revision cycles into this lightweight workflow. Keep concrete objections and allow zero findings.
- [Nexus Spatial discovery example](https://github.com/msitarzewski/agency-agents/blob/main/examples/nexus-spatial-discovery.md):
  an example of outputs from multiple roles combined into a product direction. Use its organization as a reference,
  not its market claims or the author's reported effectiveness as independently verified evidence.

Borrow selected role responsibilities and deliverable structures. Omit unrelated code examples, persistent-memory
instructions and numeric success targets that have no supplied evidence. Wholesale installation is unnecessary.

### Impeccable: concrete design perspectives

[pbakaus/impeccable](https://github.com/pbakaus/impeccable) supplies design guidance and named operations rather
than serving only as a team orchestrator. Its [skill directory](https://github.com/pbakaus/impeccable/tree/main/.agents/skills/impeccable)
contains the entry skill and supporting agents, references and scripts. Useful perspectives advertised in the
repository are `critique` for design assessment, `bolder` for stronger expression, `distill` for simplification,
`delight` for personality and `polish` for finishing quality.

Proposed transfer: use `critique` to inform the critic, `bolder` and `delight` to inform an unconventional designer,
and `distill` for a simplifying alternative. These are suggested mappings, not an inspected native team recipe.
Borrow the design guidance without adopting the installer, detector, hooks, CLI or project-file conventions.

### Anthropic Cookbook: coordinator and research assignments

[Anthropic's agent prompt directory](https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents/prompts)
contains a [research lead](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/prompts/research_lead_agent.md)
and [research subagent](https://github.com/anthropics/claude-cookbooks/blob/main/patterns/agents/prompts/research_subagent.md).
Use the separation between task allocation, focused investigation, result return and coordinator synthesis.
Adapt tool names to the host and omit copied minimum-call quotas or exhaustive-research instructions. Existing
devkit deep-research packaging already supplies the preferred entry-skill/role-file shape.

### Recommended combination

Use Agency Agents as a role-definition reference, Impeccable as a design-content reference and the Cookbook as
a delegation reference. No single repository needs to be adopted in full. Preserve applicable upstream licenses
and attribution when copying text; Agency Agents declares MIT and Impeccable declares Apache-2.0.

## Evidence and references

All sources below were inspected on 2026-11-05. Experimental findings, vendor reports and design-method
analogies have different evidentiary weight. The coordinator verified consequential primary pages and source
versions; agents' returns remain research summaries, not independent replications.

| Reference and inspected scope | Supported conclusion | Limit affecting this decision |
| --- | --- | --- |
| [Kim et al., Towards a Science of Scaling Agent Systems, v3, 2026-04-08](https://arxiv.org/html/2512.08296v3); investigator inspected manuscript, coordinator verified version record and abstract | Controlled comparisons across 260 configurations and six benchmarks show task-dependent coordination effects. Reported relative changes include +80.8% for decomposable financial reasoning and -70% for sequential planning. | These benchmarks do not establish UX or ideation gains. Earlier versions/blogs describe different counts and stronger thresholds; do not turn a fitted saturation threshold into a universal routing rule. |
| [Xu et al., Rethinking the Value of Multi-Agent Workflow, v1, 2026-01-18](https://arxiv.org/html/2601.12307v1); investigator inspected manuscript, coordinator abstract | A single model can execute homogeneous role workflows with comparable performance. A staged single agent is a stronger comparison than a one-shot response. | No creativity/UX evaluation. API cache-saving estimates are partly idealized; exact local costs require measurement. |
| [Hu et al., Multi-agent AI systems outperform human teams in creativity, v1, 2026-05-18](https://arxiv.org/html/2605.17885v1); manuscript results and methods inspected | Five blinded human judges evaluated six tasks. Best team configurations improved over corresponding single-model baselines, with effect sizes d=.39–.61. Persona assignment did not significantly improve overall creativity; three-to-six-agent expansion did not improve it either. | Best-configuration selection and small single-agent samples limit inference. Token controls among discussion conditions are not an equal-budget strong-single-workflow comparison. The headline d=1.50 compares AI teams with human teams. These are rated ideas, not validated products. |
| [Zhong et al., Synthetic Heuristic Evaluation, v1, 2025-07-03](https://arxiv.org/html/2507.02306v1); investigator manuscript, coordinator abstract | Multimodal heuristic review found useful layout issues across two apps, but struggled with some conventions and cross-screen violations. Many model-raised findings were subsequently rated nonissues. | This is not a multi-agent comparison. Pooled reference issues are not an independent exhaustive ground truth. Screenshot review cannot establish actual interaction behavior or user success. |
| [Anthropic, How we built our multi-agent research system, 2025-06-13](https://www.anthropic.com/research/multi-agent-research-system); architecture, delegation, cost and evaluation sections | Vendor experience supports independent breadth-first investigation with explicit objectives, output formats and task boundaries. It reports +90.2% on an internal research evaluation and roughly 15 times chat token use. | Internal results do not isolate teamwork from extra compute. The 15-times denominator is chat, not the single-agent research baseline. This is an operational reference, not UX effectiveness evidence. |
| [Anthropic, Building effective agents, 2024-12-19](https://www.anthropic.com/research/building-effective-agents); parallelization and evaluator patterns | Separate parallel exploration from evaluation/refinement. Clear criteria and stopping conditions make a bounded evaluator useful. | Engineering guidance rather than a comparative UX experiment. The page warns that its tooling discussion has aged; reuse the patterns rather than assuming historical integrations. |
| [NN/G, How to Conduct a Heuristic Evaluation, 2023-06-25](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/); full method page | Review a narrow user task independently before consolidating observations. Heuristics complement actual user research. | Human-evaluator guidance does not establish the optimal number of LLM agents or prove synthetic-user validity. |
| [IDEO.org, Mash-Ups](https://www.designkit.org/methods/mash-ups.html); full method page, publication date unspecified | Specify a desired quality and transfer a mechanism from an analogous domain to produce unusual alternatives. | A human design technique, not evidence that an LLM role or reference embargo improves creativity. |
| [Claude Code, Create custom subagents](https://code.claude.com/docs/en/sub-agents); living documentation | Separate conversation context, Markdown role definitions, tool configuration and startup instructions are distinct concerns. | Product-specific documentation, not a guarantee about another host. A general agent reading a role file does not acquire native tool restrictions. |
| [Claude Platform, Multiagent orchestration](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration); living documentation, Beta at inspection | Separate child histories can coexist with shared filesystem and credentials. Persistent follow-up threads retain context. | An architecture reference, not a dependency recommendation or proof of this local host's isolation. |

A direction explorer also found search-index excerpts for Dow et al. (2010), *Parallel Prototyping*, Jansson and
Smith (1991), *Design Fixation*, and Google's Design Sprint methodology. Direct retrievals timed out, returned
404 or yielded no readable content. That role reported failed fulltext verification. Those excerpts are not used
as verified support for the recommendation; readable NN/G and IDEO sources provide narrower method references.

## Work that benefits from independent contexts

The following suitability judgments are inferences from the evidence, not measured outcomes in this repository.

| Task | Why a team could help | Required result and stop signal |
| --- | --- | --- |
| Broad reference/competitor research | Different sources and domains can be searched independently; each return compresses a large input. | Evidence cards with inspected mechanism, URL, applicability and mismatch. Stop when additional sources repeat patterns. |
| UI/UX problem discovery | Task-flow, recovery/state and visual hierarchy inspections can expose different failure hypotheses. | Screen/state, user intention, observable obstacle, consequence and confidence. Stop when findings become generic taste claims. |
| Alternative interaction design | Different premises can survive long enough to become comparable artifacts. | Annotated states, actions, recovery and tradeoffs for the same task. Stop when differences are only color, wording or layout decoration. |
| Unconventional ideation | Separate mechanisms and analogous domains can widen the option set before selection. | Benefit mechanism, unusual premise, useful constraint, weakest assumption and smallest test. Stop when novelty loses connection to the problem. |
| Architecture investigation or root-cause search | Competing explanations and distinct evidence streams can be checked separately. | Falsifiable hypotheses and discriminating evidence. Keep shared-state execution with a coordinator. |
| Small edits, a single factual lookup or tightly sequential operation | Coordination has little independent work to exploit. | Prefer one agent; reopen team use only after a specific coverage gap appears. |

A team does not supply missing user knowledge. Model agreement is not independent user evidence, and fresh
conversations with the same model and brief can still share blind spots.

## Compared operating directions

| Direction | Value and cost | Provisional choice and reopening condition |
| --- | --- | --- |
| One agent with explicit research, alternatives, critique and revision stages | Lowest coordination cost; can reproduce much role-workflow behavior. Carries earlier framing through all stages. | Suitable for small tasks. It remains an alternative, not a required baseline to run before adopting roles. |
| Independent samples plus coordinator synthesis | Adds separate attempts with little role machinery; isolates whether extra sampling is sufficient. | Available simplification when multiple attempts are useful without specialized responsibilities. No control experiment is required. |
| Constraint-led role team | Separates research, competing mechanisms and evidence-linked critique; costs handoffs and synthesis. | Recommended starting direction for the user's two targets. Adapt existing role instructions and refine through ordinary use. |
| Persistent free-form debate or large personality cast | May support iterative co-development, but adds shared context, anchoring and convergence pressure. | Defer. Use a targeted exchange if a concrete unresolved contradiction needs it; no formal measurement program is required. |

### UI/UX operating sketch

Use a common brief containing the actual user task, screens or executable flow, platform, known failures,
hard constraints and unknowns. Distinguish observed failures from owner preferences.

Two initial assignments can inspect the current flow and propose alternatives under different priorities:
minimum decisions versus visible comparison and recovery. An optional researcher examines direct and adjacent
products and manual workarounds. Research returns mechanisms and applicability, not a gallery presented as proof.

After independent returns, a critic checks the frozen alternatives against the task and constraints. It may return
zero issues. A proposed initial bound is three consequential findings and one revision round, with further work
only for a decision-changing gap. That bound is an operating proposal, not an experimentally optimal number.

Example, entirely hypothetical: resolve conflicting calendar events on mobile without losing attendees. Compare
a guided two-decision flow, side-by-side alternatives and a conflict inbox organized around decisions. Each
candidate supplies detection, choice and confirmation states; primary actions; recovery; one benefit; one harm;
and a task that could distinguish it from the others. Actual UI artifacts were not generated in this run.

Visual quality requires visual artifacts and inspection at the intended viewport. Text-only critique can assess a
flow description but cannot verify visual hierarchy, rendering or perceived polish. Prefer an executable
walkthrough for interactions; label screenshot-only deductions accordingly.

### Ideation operating sketch

Run two independent assignments with different premises: remove a conventional step, and transfer a useful
mechanism from an unrelated domain. Give both the problem and constraints, without peer proposals. An optional
reference researcher can work separately; expose references during refinement if the first pass should avoid
copying familiar patterns. Withholding references is an untested fixation-reduction hypothesis and may cause
rediscovery or impractical ideas.

Require each idea to name its mechanism, intended user benefit, strongest counterexample, unknown and cheap
validation. Evaluate novelty and usefulness separately. Keep one unconventional alternative visible when it has
a plausible benefit; a critic should expose assumptions and repair opportunities rather than eliminate every
uncertain idea. The coordinator preserves incompatible premises instead of blending all ideas into a generic list.

## Proposed packaging and context hygiene

Retain the user's preferred layout: one explicitly invoked entry skill and plain role files under its own
directory. The proposed starting structure is:

```text
design-explore/
├── SKILL.md
├── roles/
│   ├── ux-designer.md
│   ├── wild-ideator.md
│   ├── reference-researcher.md
│   └── critic.md
└── references/
    └── output-format.md
```

These files are proposed, not created. The designer develops a usable direction; the ideator challenges familiar
premises; the researcher finds relevant mechanisms and references. They submit independently, then the critic
reviews once and the coordinator presents alternatives. Select only roles needed for the request. UI refinement
can emphasize the designer; idea discovery can emphasize the ideator and researcher. Different design constraints
can be assigned to repeated instances of the same role without adding permanent role files.

The entry skill would own intake, role selection, artifact identity, comparison, stopping and the final result.
Roles would describe observable work, evidence requirements and failure conditions. A per-run assignment would
supply the goal, known facts, unknowns, exact input versions, absolute role path, read/write boundaries, available
actions, required return fields and an observable research bound. No role needs the entire parent transcript.

Explicit invocation limits activation; it does not remove skill descriptions from host discovery. Fresh child
contexts reduce transcript carryover; they do not erase ambient project instructions or model priors. Role prose
is a behavioral boundary. Host permissions control actual tools and resource access. In this pilot all agents
shared a workspace; task-specific filesystem isolation was not enforced by separate sandboxes.

The coordinator's final synthesis remains in the invoking conversation. For stronger separation from later coding,
use a separate research session and carry only the selected material into the next session. Do not automatically
reload old runs or persist role memories. Follow-up messages reuse the recipient's history; create a fresh agent
when a clean recheck is the objective.

## Lightweight adoption path

1. **Adapt the useful repository instructions.** On a separate implementation request, author the explicit skill
   and selected role files using the references above. No benchmark or comparative-quality approval gate is required.
2. **Use the configuration on an actual request.** Supply the task and available context. Invoke only relevant
   roles, collect their first results, run one useful critique pass and let the coordinator summarize options.
3. **Adjust concrete friction during ordinary use.** If results duplicate one another, change assignments or drop
   a role. If the critic invents objections or stalls progress, narrow it. If the output becomes generic, preserve
   the distinct premises and concrete examples. No repeated trial until a benefit is proved is planned.
4. **Keep product checks proportional to the chosen change.** Inspect an actual UI when making UI claims and
   distinguish imagined user reactions from observations. Normal implementation checks remain separate from
   measuring whether an agent team outperforms a single agent.

Same-task A/B/C comparisons and blind scoring were considered and explicitly declined by the user. They are
outside the adopted path. The unresolved empirical question of team superiority is a limitation, not a blocker.

## Deep-research pilot observations

Starting HEAD was `22141f429f8d8c235ccae85a0be170d2bd3313ec`; Git status and index were initially clean.
The run used three fresh-context general agents in its first wave: empirical investigator, design direction
explorer and operational-pattern investigator. Each received an absolute role path, a bounded question and
restricted note ownership. Parent conversation inheritance was disabled. A fresh critic reviewed their actual
returns after the first wave and reported zero consequential findings against the qualified proposal. That review
was not a blind outcome evaluation or a review of the final material. The coordinator alone retained this material.

The investigator and patterns roles returned completed documentary investigations. The design role returned
partial evidence and an explicit fulltext-verification failure. The coordinator supplied readable method sources
and retained the failed coverage as a limit. This demonstrates execution, independent return collection and
source qualification; it does not demonstrate superior UX, creativity, lower latency or cost efficiency.

The research effort was bounded by one initial return per assignment, at most four substantive sources per
first-wave role, and one critique pass. No hard time/token cap was enforced. Some coordinator source checks
duplicated investigator coverage to verify consequential claims. Token billing and a single-agent baseline were
not measured. One progress update accidentally used Japanese and was immediately followed by Korean; user-facing
language consistency is a pilot defect, not a research finding.

Temporary run: `.devkit/transient/deep-research/run-pilot-20261105-MWHYiC/`. Its exact scratch paths were checked
as ignored and had no tracked files before note writes. The run is optional execution evidence; this material's
claims and references remain understandable without it. No implementation, stage, commit or push occurred.

## Open choices and next action

The first real UI flow or idea request, the exact borrowed role text and the initial role subset remain open.
They can be settled while authoring the skill or using it; no further research or comparative experiment is
required before that work. The next concrete action, if separately requested, is to adapt the referenced
instructions into the proposed explicit skill and role files. No implementation starts from this material alone.

Commit this material through the project's Git policy before a proposal, spec, decision or current-context note
cites `MAT-agent-team-design-pilot` from the base.

Status: complete. The bounded investigation and repository-reference follow-up are complete. No skill was
implemented or installed. Comparative gains and real-user outcomes remain unverified and are not adoption gates.
