---
id: MAT-ux-documentation-practice
title: UX documentation and review practice
summary: "Surveys how interface specifications, use-case-to-screen traceability and design reviews are done in practice, what an LLM reviewer can do reliably, and the options devkit has for a UX document kind, authoring guidance and an independent review."
created_at: 2026-10-26
---

# [MAT-ux-documentation-practice] UX documentation and review practice

Research input for `MS-ux-documentation`. External claims cite their source; several primary texts could not be
reached and are cited through secondary sources (section 7). "A consumer project's draft procedure" is an unapplied
draft procedure from one consumer project, reviewed read-only, and is described only by its generic parts.

## 1. What a screen specification contains

Use cases stay free of UI detail; screens carry it. Essential use cases (Constantine and Lockwood, usage-centered
design) describe user intent without a particular interface, so the interface is not fixed too early
([Use case](https://en.wikipedia.org/wiki/Use_case), [Usage-centered design](https://en.wikipedia.org/wiki/Usage-centered_design),
both secondary). devkit's use case writing instruction already requires this: the goal is "not a UI step", and each
step is written as its intent.

A durable screen specification usually holds:

- **Purpose**: the primary task in one verb phrase and the few facts the user needs to commit to it; every other item
  gets an explicit place (a tab, a tooltip, another screen).
- **Content and hierarchy**: what is shown and in which priority, not pixel layout. Constantine and Lockwood derive
  layout from task cases through abstract prototypes.
- **States**: empty, loading, error, disabled and "empty after processing"; a blank container leaves the user unable
  to tell loading from failure from no data ([NN/g, empty states](https://www.nngroup.com/articles/empty-state-interface-design/)).
- **Interactions**: for each control, what happens, and whether it is reversible or needs confirmation.
- **Transitions**: entry points and exits.

Flows: wireframes show one screen and capture interactions poorly, flowcharts show paths without screen context, and
wireflows combine both ([NN/g, wireflows](https://www.nngroup.com/articles/wireflows/)). The text equivalent is a
screen inventory plus a transition table (from, input, condition, to, effect).

Interaction principles are standardized in ISO 9241-110:2020 (suitability for the task, self-descriptiveness,
conformity with expectations, learnability, controllability, use-error robustness, user engagement;
[ISO 9241](https://en.wikipedia.org/wiki/ISO_9241), secondary). Visual attributes (type, colour, spacing tokens) belong
to visual design or a design system; components belong to the implementation.

The consumer project's draft procedure has the same shape: a screen section of job, primary action, decision drivers
and secondary information with a destination for each item; a flow document with the screen list, persistent panels,
a transition table, irreversible actions, acceptance criteria and open questions; four element kinds (screen, panel,
modal, widget); and the rule that the specification is the contract while sketches are point-in-time snapshots. Its
canvas classes, pixel budgets and input-device rules are engine-specific.

**Options**

| Option | Content | Cost |
| --- | --- | --- |
| 1a | Screen spec of purpose, content priority, states, interactions with their effect, exits | Low; independent of the medium |
| 1b | 1a plus a region budget | More precise; tied to a medium, so project-owned |
| 1c | A flow document as its own document, not a section of an index | Simplifies the mechanical checks of section 2 |

## 2. Tracing use cases to screens

The conventional chain is use case step → boundary (screen) → control or entity, from robustness analysis in
use-case-driven object modeling (Rosenberg and Stephens, 2007; [ICONIX](https://en.wikipedia.org/wiki/ICONIX),
secondary). It matches the planned step → screen → capability links. Wireflows attach screens to each step of a task.

Once links are declared, these checks are graph or set arithmetic:

- orphans: a use case step with no screen, a screen interaction that serves no step;
- unknown screen IDs;
- reachability from the start screen;
- dead ends: a screen without an exit, a modal without a close;
- extension coverage: each extension key (`2a`) reaches a screen state, typically an error state.

The consumer project's draft already checks reachability, exits, modal close and unknown IDs over its transition
table. Whether a screen actually supports a step is not mechanical; that needs a walkthrough (section 3).

devkit today: `RULE-traceability-link` reads only the `capabilities` and `usecases` frontmatter lists. Use case steps
cite capabilities in prose, and no rule parses the numbered steps, so step-level checks need new parsing of use case
bodies.

**Options**

| Option | Content | Cost |
| --- | --- | --- |
| 2a | Links plus an orphan rule | Lowest; meets the milestone exit condition |
| 2b | 2a plus the flow graph checks | Moderate; needs a fixed transition table schema |
| 2c | 2b plus extension → state coverage | Highest value for error handling; needs a state ID convention |

## 3. Review methods

| Method | Inputs | Procedure | Output | Limits |
| --- | --- | --- | --- | --- |
| Cognitive walkthrough (Wharton et al., 1994) | Task steps, a persona, the screens | At each step: will the user try the right thing, notice the action, connect it to the goal, see progress? A "no" fails the step | Pass or fail per step with reasons | Centred on learnability for new users; not a substitute for testing ([NN/g](https://www.nngroup.com/articles/cognitive-walkthroughs/)) |
| Heuristic evaluation (Nielsen) | A heuristic list, the interface, a scoped task | Evaluators work alone, then merge | Violations by heuristic | One evaluator finds about 35% of problems, so 3-5 are used ([NN/g](https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/)) |
| Usability testing | Real users, a prototype | Observe task attempts | Observed failures | Needs real users; heuristics do not replace it |

A cognitive walkthrough is a structured traversal of a use case's numbered main scenario and extensions, which is
what devkit use cases already provide.

Evidence on LLM reviewers:

- Duan et al., CHI 2024 ([arXiv 2403.13139](https://arxiv.org/abs/2403.13139)): GPT-4 feedback helped with subtle
  errors and text; its usefulness decreased over iterations.
- UICrit, UIST 2024 ([arXiv 2407.08850](https://arxiv.org/abs/2407.08850)): few-shot and visual prompting with expert
  critiques improved results by 55% (metric not named in the abstract).
- Guerino et al., INTERACT 2025 ([arXiv 2506.16345](https://arxiv.org/abs/2506.16345)): GPT-4o found 21.2% of the
  expert-identified issues and produced false positives.
- Zhong et al., 2025 preprint ([arXiv 2507.02306](https://arxiv.org/abs/2507.02306)): a multimodal LLM found 73-77% of
  issues against 57-63% for human evaluators, but missed conventions and violations spanning several screens.
- Platt et al., VL/HCC 2025 ([arXiv 2512.04262](https://arxiv.org/abs/2512.04262)): issue detection was moderately
  consistent across runs (kappa 0.50); severity ratings were not (Krippendorff's alpha near 0).

An LLM reviewer is credible for a step-by-step walkthrough over declared links, missing states and feedback, and
single-screen content and wording. Severity and priority, taste and brand fit, cross-screen conventions and real-user
validation need a person.

**Options**

| Option | Content | Cost |
| --- | --- | --- |
| 3a | Walkthrough-only reviewer (the four questions per step) | Low; best fit to the evidence |
| 3b | 3a plus a heuristic rubric scored 0/1/2 with cited evidence and no severity | Medium |
| 3c | 3b with several independent runs merged, like 3-5 evaluators | Higher token cost; offsets run-to-run inconsistency |

## 4. Failure modes of agent-designed interfaces

- Convergence to safe, generic layouts: models sample from the high-probability centre
  ([Anthropic, frontend design skills, 2025](https://www.claude.com/blog/improving-frontend-design-through-skills);
  [Anthropic, harness design for long-running apps, 2026](https://anthropic.com/engineering/harness-design-long-running-apps)).
- Lenient self-evaluation: agents skew positive when grading their own work, and an evaluator can talk itself into
  approval (harness design article).
- Information dumping (every field on one screen): no external source found; it is the failure the consumer project's
  draft targets.

Documented mitigations: a separate evaluator tuned to be skeptical; concrete graded criteria with few-shot calibration;
explicitly requested variation between candidates; and a cap on iterations, since usefulness plateaus or drops (Duan et
al.; harness design article). The consumer draft applies the same set: one or two questions first, then two or three
contrasting candidates for the user to choose from; a 0/1/2 rubric scored in a fresh context with evidence for every
score below 2; at most two review rounds; and rubric items a deterministic check decides are reported, not re-judged.

**Options**: 4a a separate reviewer with a rubric; 4b also contrasting candidates in the authoring guidance (one user
choice per screen); 4c also a cap on review rounds (cheap and supported by evidence).

## 5. Wireframe fidelity and medium

Fidelity has three independent dimensions: interactivity, visuals and content
([NN/g](https://www.nngroup.com/articles/ux-prototype-hi-lo-fidelity/)). Reviewing against use cases needs the
content dimension (what each screen shows, its states, where each action leads); visual fidelity matters little at
that stage. The consumer draft forbids detailed character-cell sketches because they distort proportions and agents
copy sketch details as fixed coordinates, which supports keeping a text contract owned by devkit and the wireframe
medium owned by the project. The cost: devkit cannot check that an implementation matches the specification; only
the project's own tools can.

**Options**: 5a text specification only, the medium optional and project-owned; 5b 5a plus a declared evidence slot
(a screenshot or path) that the reviewer reads when present; 5c a devkit-owned wireframe format (excluded by the
milestone's non-goals).

## 6. devkit integration points

- **Use cases**: already intent-level (`usecase-writing` instruction), so the UX layer maps intent steps to screens
  without changing use case prose rules.
- **Links**: whether a step names its screen in prose (as it cites capabilities today) or through a structured field
  decides how the orphan rule parses use cases.
- **Reviewer**: `code-reviewer` is an isolated, read-only subagent bound to the `spec-review` skill; a UX reviewer can
  follow the same pattern with its own skill.
- **Kinds**: the UX kind depends on `PROP-table-driven-document-kinds`.

## 7. Research recommendation and unverified areas

The research recommends 1a with 1c, 2b, 3b, 4b with 4c, and 5a or 5b, and reconsidering 3c if projects report
inconsistent rubric scores across runs. These are inputs to Planning, not decisions.

Not verified against primary texts: Wharton et al. 1994 and Nielsen and Landauer 1993 (cited through NN/g);
Constantine and Lockwood's abstract prototypes and navigation maps; Cockburn's own wording on keeping UI out of use
cases; ICONIX boundary, control and entity detail; ISO 9241-110/210; full-paper metrics of three of the cited papers
(abstracts only; arXiv 2507.02306 is not peer-reviewed). No external source was found for information dumping as a
documented failure mode, and design-system documentation practice was not researched.
