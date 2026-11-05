---
id: PROP-design-solution-exploration
title: Add an explicitly invoked general design ideation skill
summary: "Add a skill-local team that reframes general design problems, explores materially different solution mechanisms and returns useful directions with tradeoffs without a mandatory validation program."
status: draft
created_at: 2026-11-05
target_area: capabilities/delivery/
priority: medium
size: M
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/
    - packages/devkit-catalog/pyproject.toml
    - packages/devkit-catalog/README.md
    - packages/devkit-catalog/tests/integration/bundles/
    - packages/devkit-catalog/tests/e2e/bundles/
    - docs/capabilities/delivery/
    - docs/usecases/delivery/
    - docs/architecture/ARCH-05-2-components.md
    - guides/
  excludes:
    - packages/devkit/src/
    - packages/devkit-dist/src/
    - packages/devkit-spec/src/
    - .devkit/managed/
    - .agents/skills/
task_kind: feature
planning_effort: medium
dev_effort: medium
---

# [PROP-design-solution-exploration] Add an explicitly invoked general design ideation skill

## 1. Background & Hypothesis

The user wants an explicitly invoked team for finding less conventional and more useful solutions than a single
agent's ordinary suggestions. Its main use is general design work, including software/system architecture,
data models, module boundaries, processing flows and development workflows. It is not a UI/UX-specific skill.

The agreed goal is to find worthwhile solution directions for a supplied problem by revisiting familiar premises
and exploring different mechanisms. The result should help the user decide how to approach the design. It is
not an unlimited search for novel ideas, a business incubator or an automatic implementation workflow.

Hypothesis: independent exploration, optional external references and bounded criticism can expose alternatives
that a single framing would miss. Roles are means of expanding the design space, not evidence of superior
reasoning. The user prefers adapting existing patterns and refining through use; comparative-effectiveness
experiments are not a prerequisite.

### User decisions and evidence status

- Use an explicitly invoked skill with local Markdown roles and fresh contexts where supported.
- Center the skill on general design problems rather than UI/UX ideation.
- Finish with useful directions and tradeoffs; market validation, implementation and proof of team superiority
  are not part of the default goal.
- Keep this proposal separate from the UI/UX improvement and deep-research improvement proposals. It need not
  wait for either to be implemented.
- No actual design problem was exercised by this drafting task. Examples below are hypothetical, not validated
  technical recommendations. This proposal is self-contained without the separately retained research record.

## 2. Technical Spike Questions

No runtime spike, benchmark or further literature review is required before authoring the skill. Planning should
settle the following:

- **Q1:** Confirm the public name. `design-explore` is the working recommendation; its description should name
  general solution design explicitly so it is not mistaken for a visual-design-only entry.
- **Q2:** Set the minimum input framing and output shape without requiring a formal brief or fixed idea count.
  Infer the problem from supplied context and ask only when a missing constraint changes the exploration.
- **Q3:** Choose a small set of exploration heuristics and role instructions. Prefer one reusable explorer with
  different premise assignments over a large catalog of specialist personas.
- **Q4:** Define how to retain a useful result in the consumer's requested destination without introducing a new
  document kind, permanent memory, approval record or automatic delivery workflow.

## 3. Proposed Design & Impact

### Goal and representative use

Given a design problem, discover materially different ways of solving it and make their benefits, costs and
assumptions clear enough for the user to choose a direction. Challenge proposed means while preserving the
actual goal and hard constraints. A supplied solution is not automatically a requirement.

Representative requests include deciding how components coordinate work, simplifying a data model, reconsidering
module ownership, changing a processing pipeline or avoiding complexity in a planned feature. Explorers may
suggest eliminating a component, moving responsibility, changing when work happens, reversing a dependency,
reusing an existing mechanism or solving the problem outside the initially proposed subsystem.

For example, a request to design cross-process status sharing can explore centralized ownership, an existing
persistent store or asynchronous events. Each option should explain its coordination mechanism, failure behavior
and adoption cost. Merely substituting three database products does not necessarily create three different designs.
Do not introduce distributed infrastructure solely to make an option look more novel.

### Proposed packaging

Add an opt-in content-only bundle to `devkit-catalog`, following `ARCH-05-2-components`. Use existing bundle
registration and user-only invocation. Preserve the local-role distribution principle illustrated by
`ADR-skill-local-research-roles` without assuming that research-specific decision automatically governs this bundle.
No new package, runtime, dependency, global specialist registration or automatic bundle selection is proposed.

Proposed layout, not final public naming or created assets:

```text
design-explore/
├── SKILL.md
├── roles/
│   ├── solution-explorer.md
│   ├── reference-researcher.md
│   └── design-critic.md
└── references/
    ├── orchestration.md
    └── exploration-methods.md
```

The coordinator assigns different premises to separate instances of `solution-explorer.md`. Example lenses are
simplest sufficient design, removal of a conventional assumption and transfer of a mechanism from another domain.
An unusual premise can initially relax a preference, but any conflict with a hard constraint must remain explicit.
The coordinator compares actual returned mechanisms rather than counting personality labels as diversity.

### Exploration process

1. Recover the problem, intended benefit, existing design, hard constraints and open preferences. Use only relevant
   supplied or project context; do not require the whole architecture to be documented before exploring.
2. Choose independent questions or premises. Keep small questions inline. Where separate context is useful,
   dispatch fresh general agents with the selected role path, self-contained facts, scope, expected return and
   observable stop condition. Initial explorers should not see one another's conclusions.
3. Use reference research when an external mechanism, implementation precedent or technical uncertainty could
   change the options. Research supports design exploration; no exhaustive survey or web search quota is required.
4. Compare directions on how they solve the problem, added and removed complexity, coupling, failure behavior,
   migration/adoption cost and consequences relevant to the user's constraints. Select relevant criteria rather
   than scoring every option across a universal checklist.
5. Use a critic when it can expose a consequential assumption or improve a candidate. Permit zero findings and
   normally one useful refinement pass. Preserve unusual directions with plausible benefits instead of forcing
   consensus or rejecting every uncertainty.
6. Return a compact set of useful directions, a recommendation when justified and the unresolved choice, if any.
   Name a next check only when a concrete unknown changes that choice. Do not turn optional checks into a new
   research or validation program. Implementation starts only through a separate request and existing workflow.

### Expected result

A useful direction explains the problem it solves, its distinguishing mechanism, why it is worth considering,
its main tradeoff and the assumption most likely to change the recommendation. Include a sketch, data shape,
sequence or concrete example when it makes the mechanism understandable. Such examples are illustrative and
not production changes. Do not generate a fixed number of weak alternatives to fill a template.

Keep novelty and usefulness distinguishable. Familiar designs can be the recommendation; unconventional ideas
can expose a useful simplification even when their entire premise is unsuitable. The final synthesis should
preserve important differences instead of averaging candidates into a generic feature list.

No source edits, benchmark suite, market study, mandatory prototype or formal design document are implied by
invoking this exploration skill. Honor a requested output destination; otherwise return the result in conversation.
Read-only source inspection and relevant public research may support the result within the assigned boundaries.

### Reuse and boundaries

Use [Anthropic's agent prompts](https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents/prompts)
as a delegation reference and [Agency Agents](https://github.com/msitarzewski/agency-agents) as a role-structure
reference. Their full workflows, persona biographies, memory claims and success targets are not requirements.
Preserve applicable attribution and licenses when adapting text. Neither reference proves this skill's effectiveness.

Do not depend on or automatically invoke deep-research, UI/UX improvement or adaptive-dev. This entry explores
solution directions; deep-research investigates a question through sourced evidence; UI/UX improvement changes
interfaces and experience within the requested delivery scope. Similar coordination patterns can be independently
contained in each bundle. No new cross-feature runtime dependency is in scope.

Only the invoking skill loads its role instructions. Separate contexts do not isolate shared resources or erase
ambient project guidance. Roles return proposals or evidence within explicit boundaries and do not commit,
publish, select a final product direction or create delivery approvals.

### Expected scope and acceptance examples

The source/test parents in the boundary accommodate the new bundle, registration and focused installation checks.
Reconcile the behavior into a capability and use case and keep architecture/consumer guidance aligned. Do not
change other catalog bundles or add application runtime behavior.

- A general architecture or data-design question produces relevant solution mechanisms, not a UI redesign.
- A feature request can be reframed to question whether a new feature/component is necessary while preserving
  the user's actual goal and constraints.
- Independent assignments can produce different approaches before synthesis; trivial wording or technology-brand
  variations are not presented as substantive diversity.
- A simple question can finish without a team, critic or web survey. No fixed count, debate or consensus is required.
- An uncertain benefit is stated without making comparative validation a prerequisite for using the skill.
- The final result helps choose a design direction and does not automatically implement, alter settings or publish.
- Packaging checks verify opt-in deployment and local role files. Semantic review checks the examples and authority
  boundaries without claiming to measure creativity or outperform a single agent.

### Scope excluded

- A UI/UX-focused ideation entry or duplication of the separate UI/UX improvement skill.
- Unbounded business/product idea generation, market validation or automatic execution of proposed designs.
- A mandatory research report, fixed brainstorming cast, benchmark program or iteration until benefit is proved.
- New document schemas, global role metadata, persistent memory, agent runtime or changes to project governance.
- Implementation or plan acceptance during this drafting task.

## 4. Lifecycle & Retirement Criteria

Keep the proposal in `draft`. The user requested recording the direction, not accepting Planning or starting
Development. The public name, concise role behavior and retention convention remain Planning choices.
The intended implementation fits one content-bundle and documentation change. Use the normal proposal
acceptance, handoff and retirement lifecycle if the user chooses to proceed.
