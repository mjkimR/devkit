---
id: PROP-ux-design-exploration
title: Add an explicitly invoked UI/UX improvement skill
summary: "Add an optional skill-local team that improves interface design and user flows through proportionate diagnosis, reference discovery, design, implementation and verification within the user's requested scope."
status: accepted
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
    - guides/install/bundle-recommendations.md
  excludes:
    - packages/devkit/src/
    - packages/devkit-dist/src/
    - packages/devkit-spec/src/
    - packages/devkit-viewer/
    - .devkit/managed/
    - .agents/skills/
task_kind: feature
planning_effort: medium
dev_effort: medium
workflow: sdd-proposal
---

# [PROP-ux-design-exploration] Add an explicitly invoked UI/UX improvement skill

## 1. Background & Hypothesis

The user wants better UI/UX results than the ordinary suggestions produced by a single agent. They prefer an
explicitly invoked skill with local Markdown roles, including design, unconventional suggestions, references
and criticism, so those instructions do not populate unrelated work. They want to reuse existing instructions
and refine them through use rather than run comparative experiments before adoption.

The skill's goal is overall UI/UX improvement. Producing alternatives is one means of achieving that goal,
not the required final product. A normal improvement request should be able to reach actual changes and
proportionate verification within its authorized scope. Diagnosis-only or proposal-only requests retain their
narrower boundaries. Product changes start only after the applicable delivery workflow permits them.

Hypothesis: one coordinator can select useful independent perspectives, combine them into coherent design
changes and carry the requested improvement through the project's normal delivery process. The skill should
address flow quality and visual quality together, while keeping the work focused on the supplied product goal.

### User choices and evidence limits

- Explicit invocation and skill-local roles are the selected packaging direction.
- The user explicitly broadened the objective from making improvement alternatives to improving UI/UX overall.
- No same-task comparison, blind scoring or evidence of superiority is required before adoption.
- No concrete product or screens were supplied; proposed workflows below are not observed product outcomes.
- This draft provides direct references and a self-contained rationale. It does not require the separate
  research material or its transient execution records to be understood.

## 2. Planning Decisions

- **Public entry:** `uiux-improve` is both the bundle and skill name. Its description names overall interface and
  user-flow improvement; `invocation = "user"` prevents implicit invocation through supported projections.
- **Intake and completion:** recover the target, user outcome, relevant artifacts and constraints. Reuse supplied
  context instead of requiring a brief. Finish with the applied changes, actual verification and material limits;
  a diagnosis-only request finishes with findings. Alternatives and a formal design document are optional.
- **Workflow boundary:** the skill provides design guidance while the consumer's existing development workflow
  controls implementation, records, checks, commit and integration. It does not select a development approach,
  install delivery tooling or automatically invoke a sibling skill. A missing required approval leaves changes
  pending through that workflow instead of being treated as design completion.
- **Distribution:** ship one content-only catalog bundle, one user-invoked skill, four local role files and two
  references. No globally registered role, pointer or always-loaded design instruction is introduced.
- **Optional delegation:** keep a small, concrete request inline. For an open-ended request, dispatch only useful
  design, unconventional-design, reference or critique assignments. First passes receive independent inputs.
  One bounded critique/refinement pass is available; no cast, count, score or consensus is required.
- **Authorship:** write original concise guidance informed by the retained reference analysis. Link upstream
  repositories for provenance; no upstream source file or prose excerpt needs to be copied. If Development
  chooses to copy text, inspect that revision's license and preserve required attribution before committing it.
- **Retention:** honor an explicitly requested destination; otherwise report in conversation. Product changes and
  design artifacts follow the consumer's ownership conventions. No new persistent memory or document kind is added.

`PADR-uiux-improvement-workflow-boundary` records the lasting delivery and local-role boundary. Public naming,
reference selection and role assignments remain reversible implementation choices. No runtime spike, further
literature survey, product usability experiment or agent-team comparison is needed for this content delivery.
There are no unresolved product decisions for this Planning turn. Development remains `medium` for packaging,
instruction review and consumer-workflow compatibility.

## 3. Proposed Design & Impact

### Goal and representative use

Improve the interface and experience serving a supplied user goal. This can include navigation and information
architecture, task steps, feedback and recovery, interaction details, hierarchy, typography, spacing, responsive
behavior, accessible operation and visual character. Select the relevant dimensions instead of auditing all of
them on every invocation. New or missing screens can be designed when they serve the requested flow.

Example requests include improving a confusing settings flow, making a dashboard easier to scan, giving a
landing page more character, simplifying onboarding or improving a product's UI/UX across a bounded set of
surfaces. The coordinator can suggest an initial focus for a broad request without turning it into a mandatory
research project. Preserve supplied design-system and product constraints unless the user authorizes changing them.

### Packaging and ownership

Add an opt-in content bundle to `devkit-catalog`, following the existing content-only bundle layout in
`ARCH-05-2-components`. Register its entry through the existing `devkit.bundles` mechanism and declare user-only
invocation. No auto-selection, global specialist registration, runtime module or new Python dependency is proposed.

Use the skill-local-role approach illustrated by `ADR-skill-local-research-roles`: general subagents read the
selected role file and receive a self-contained assignment, with fresh context where supported. That ADR owns
the existing research-specific decision. `PADR-uiux-improvement-workflow-boundary` records this bundle’s decision.

Selected skill layout inside `devkit_catalog/uiux_improve/bundle/skills/`, to be created in Development:

```text
uiux-improve/
├── SKILL.md
├── roles/
│   ├── designer.md
│   ├── unconventional-designer.md
│   ├── reference-researcher.md
│   └── critic.md
└── references/
    ├── orchestration.md
    └── design-guidance.md
```

The coordinator owns the result, changes and delivery report. Roles return evidence, concrete suggestions or
design artifacts. Parallel source edits are unnecessary for the first version; the coordinator can implement
accepted elements without creating another specialist. Role text is behavioral guidance, not host-enforced
permission or filesystem isolation. Only selected role bodies are loaded.

### Improvement process

1. Recover the target, user goal, current artifacts and constraints from the request and available project context.
   Ask only for missing information that changes the work. Inspect the running UI when available; identify
   screenshot-, code- or text-only limitations when actual interaction cannot be checked.
2. Select useful perspectives. A designer can improve task flow and hierarchy; an unconventional designer can
   challenge safe defaults; a researcher can find relevant mechanisms; a critic can identify concrete harms.
   For independent first passes, do not share peer conclusions until their returns are available.
3. Synthesize a coherent direction. Produce alternatives when the choice matters, not as a mandatory deliverable.
   Preserve a worthwhile unusual idea when it serves the goal. Resolve routine design choices within the request;
   involve the user when a product decision or scope change is necessary.
4. Apply the changes when the user requested improvement and the existing project workflow permits implementation.
   Continue through that workflow's required records, checks and approvals. A review-only request stops with findings;
   a skill invocation never overrides an explicit read-only constraint or grants publication authority.
5. Inspect the resulting UI and representative interactions using available tools. Run checks appropriate to the
   actual change. Report what changed, what was actually checked and any material limitation. If useful, do one
   bounded critique/refinement pass; do not require repeated review until a score or consensus is achieved.

A normal improvement request finishes with the changed interface or flow and its verification status, not merely
an idea list. If execution is blocked by a missing product choice, artifact or tool, preserve useful partial work
and identify that specific blocker. Do not substitute a generic design report for requested implementation.

### Role behavior and references to adapt

- [Agency Agents design roles](https://github.com/msitarzewski/agency-agents/tree/main/design) provide examples
  of separating UI design, UX concerns and distinctive expression into role files.
- [Whimsy Injector](https://github.com/msitarzewski/agency-agents/blob/main/design/design-whimsy-injector.md)
  provides ideas for purposeful delight and micro-interactions. The unconventional designer should also explore
  flow and layout alternatives rather than only animation, playful copy or decorative effects.
- [Impeccable](https://github.com/pbakaus/impeccable) provides useful perspectives through `critique`, `bolder`,
  `distill`, `delight` and `polish`. Adapt selected guidance without adopting its installer, CLI, detector or hooks.
- [Anthropic's research prompts](https://github.com/anthropics/claude-cookbooks/tree/main/patterns/agents/prompts)
  provide an optional delegation reference for the researcher. Research serves the improvement; it does not
  become an exhaustive survey or mandatory phase.

Criticism should be specific to the task and artifacts, allow zero findings and suggest practical repairs.
Do not copy automatic first-pass failure, fixed issue quotas, mandatory revision cycles, invented remembered
experience or unsupported success percentages. Keep upstream attribution and license obligations when copying.
These repositories are reusable instruction references, not proof that this composition improves every result.

### Context and delivery boundaries

Keep the bundle independent from deep-research and adaptive-dev. It should not automatically invoke either entry,
change the selected development approach or import private instructions from another bundle. Reuse the distribution
mechanism, not another skill's runtime state. No new cross-feature runtime edge is in scope.

A fresh child reduces conversation carryover but does not remove ambient instructions or isolate shared resources.
The invoking conversation retains the final result; a separate session remains available when the user wants
stronger separation from later work. Do not introduce persistent role memory or global UI/UX guidance.

Formal adoption of the deep-research improvement proposal is not a prerequisite. This bundle can implement its
own concise delegation and usefulness checks without waiting for another work unit to land.

### Expected scope and acceptance examples

The boundary parents accommodate files that do not exist yet. Development is limited to these additions and
shared registration/document edits:

- Add `packages/devkit-catalog/src/devkit_catalog/uiux_improve/__init__.py` and `uiux_improve/bundle/` below that
  package, containing `bundle.toml` and the selected skill tree above.
- Register `uiux-improve = "devkit_catalog.uiux_improve"` in `packages/devkit-catalog/pyproject.toml`; the initializer
  stays empty and no dependency or runtime feature edge is added.
- Add `packages/devkit-catalog/tests/integration/bundles/test_uiux_improve.py` for opt-in selection, invocation
  metadata, local-role deployment, absent global roles and self-contained content.
- Add `packages/devkit-catalog/tests/e2e/bundles/uiux_improve/test_installed_consumer.py` for wheel installation and
  public CLI selection with dist/catalog and no required spec/docs tooling. Reuse existing consumer-test support.
  Existing parameterized `test_bundles.py` should cover registration without changes.
- Add the capability and use case named in `target-docs.md`; update the catalog README,
  `ARCH-05-2-components` and `guides/install/bundle-recommendations.md` for layout, selection and invocation.
  The promoted PADR is the only planned decision-document addition.

Other catalog bundles, application packages, viewer screens, shared distribution behavior, existing governance
and consumer products remain outside this delivery. No screens are drafted because this task delivers an agent
skill rather than a concrete product interface.

- Explicit selection deploys the entry and local roles; unrelated work receives no globally registered UI/UX roles.
- An improvement request can proceed from inspection through implementation and appropriate verification under
  the existing workflow; a diagnosis-only request changes no product source.
- The same entry supports flow simplification and visual refinement without forcing either an alternatives-only
  output or an exhaustive audit of every UI/UX dimension.
- A role is invoked only for a useful assignment; independent first passes do not inherit peer conclusions.
- Critics can return zero issues, research can be skipped, and no comparative-effectiveness test gates use.
- Distribution/installation checks verify packaging and invocation behavior. Review checks instruction semantics;
  neither kind of check claims proven aesthetic quality or superiority to a single agent.

### Scope excluded

- General business-idea discovery, market validation or a standalone problem-solving ideation skill.
- Mandatory multi-agent casts, debate rounds, numeric design scores or benchmark programs.
- A new design editor, screenshot engine, browser runtime, scheduler or global agent-role framework.
- Wholesale repository installation or mandatory external services such as Figma.
- Changing a consumer's workflow, bypassing its approvals or implementing a consumer product in this skill-delivery task.

## 4. Lifecycle & Retirement Criteria

Planning leaves the proposal `reviewing`, with a committed challenger round, folded findings, target-document
blueprint and worker return. The Host reviews that committed source for `plan-accept`; acceptance and
`proposal-handoff` remain separate authorities under the effective policy. Neither is recorded by this worker.
After authorized handoff, one feature spec delivers the bundle, focused checks and Living Spec reflection.
The Planning proposal is retired by the normal handoff lifecycle, with the PADR promoted to an ADR.
