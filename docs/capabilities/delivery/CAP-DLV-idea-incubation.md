---
id: CAP-DLV-idea-incubation
title: Idea Incubation
summary: "An opt-in content bundle supports iterative product work and explicit research teams that compare directions, retain initial documents and a roadmap, and resume from mutable current facts without SDD records."
area: delivery
status: active
usecases:
  - UC-incubate-an-idea
  - UC-research-an-idea-and-shape-a-roadmap
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/incubation/bundle/skills/incubate/SKILL.md
  - packages/devkit-catalog/src/devkit_catalog/incubation/bundle/skills/incubate-research/SKILL.md
---

# [CAP-DLV-idea-incubation] Idea Incubation

## 1. Summary

The opt-in `incubation` catalog bundle supplies `/incubate` for adaptive product iteration,
`/incubate-research` for explicitly selected discovery-team work, six optional support roles and a
current-context template. The invoking agent is the coordinator (master). A product can remain in incubation;
research completion does not start development or imply eventual SDD adoption.

`ADR-extend-incubation-with-optional-discovery-teams` owns entry/role placement.
`ADR-keep-discovery-plans-distinct-from-delivery-commitments` owns the initial document/roadmap distinction.

## 2. Scope and Boundary

- **In-Scope**: adaptive clarification, bounded research/experiments, representative implementation and actual
  usage, explicit research-team coordination, competing directions, optional criticism, initial document/roadmap
  drafts, mutable current facts and resume.
- **Out-of-Scope**: shared approach policy (`CAP-DLV-project-policy`), generic projection
  (`CAP-DIST-agent-projections`), document formats (`CAP-DOCS-document-model`), project build/test tools and the
  separate baseline readiness/activation procedure (`CAP-DLV-incubation-sdd-baseline`).
- **Scope Excluded**: a runtime scheduler, agent bus, new wheel, mandatory role sequence, model routing, fixed
  management hierarchy, automatic approach switching, automatic implementation/publication, per-change SDD
  artifacts and reconstructed experiment history.

## 3. Business Rules and Policies

1. **Explicit selection**: WHERE `incubation:core` is selected, sync MUST deploy the bundle's entries and roles
   without seeding context or product documents. Test: `packages/devkit-catalog/tests/integration/bundles/test_incubation.py`.
2. **Independent installation**: The bundle MUST install with docs/catalog without a devkit-spec distribution.
   Test: `packages/devkit-catalog/tests/e2e/bundles/incubation/test_installed_consumer.py`.
3. **Approach inspection**: WHEN either entry starts product work, the coordinator MUST inspect the effective common
   development approach rather than infer it from bundle selection.
4. **Inactive entry**: IF the approach is not incubation, THEN the entry MUST stop product actions and report the
   shared configuration action before any user-directed approach change.
5. **Unreadable policy**: IF policy inspection fails, THEN the coordinator MUST report the actual error and next
   configuration action without performing product work.
6. **Adaptive clarification**: WHEN the next action needs a product decision, the coordinator SHOULD reuse known
   answers and ask only the consequential missing decision.
7. **Bounded evidence**: WHEN research or an experiment informs work, the coordinator MUST distinguish observations,
   assumptions, limitations and the decision informed; an experiment names its write boundary and stop condition.
8. **Representative implementation**: WHEN implementation is retained, the coordinator MUST provide executable run
   and verification instructions for its representative flow.
9. **Truthful verification**: WHEN reporting a check, the coordinator MUST identify actual source/artifact-specific
   execution and limitations; skipped, unavailable or inconclusive evidence remains unverified.
10. **Iteration scope**: WHILE the product goal and constraints hold, the coordinator MAY reconstruct retained code,
    tests and documents without per-change SDD Units, approvals, envelopes or immutable experiment history.
11. **Changed direction**: IF the goal or constraints change, THEN the coordinator MUST obtain user direction before
    dependent work.
12. **Optional support**: WHERE a separable question or usage scope warrants delegation, the coordinator MAY invoke
    the corresponding support role; no action requires all roles or a fixed team count.
13. **Role boundaries**: WHEN a role is invoked, the coordinator MUST supply one goal, absolute boundaries,
    source/artifact identity, permitted actions, stop condition and expected output before verifying the actual
    return. The role reports native/emulated availability truthfully.
14. **Current context ownership**: WHEN retained resume facts change or work pauses, the coordinator MUST update
    project-owned `.devkit/incubation.md`; roles return evidence or drafts instead of editing that file.
15. **Context preservation**: WHEN sync, removal or re-selection runs, sync MUST preserve existing project-owned
    context and discovery notes. Tests: catalog integration and installed-consumer tests.
16. **Voluntary adoption**: WHEN the user explicitly requests SDD adoption, the coordinator MUST leave activation to
    the separately available baseline procedure while explaining preparation with incubation still active.
17. **Explicit research entry**: WHERE the research skill is selected, the bundle MUST declare `invocation = "user"`;
    a topic match permits a suggestion, not automatic team research. Native projection follows
    `CAP-DIST-agent-projections`. Test: `test_research_entry_projects_explicit_invocation_for_each_host`.
18. **Independent alternatives**: WHILE direction is open, the coordinator SHOULD develop materially different
    premises independently before sharing peer conclusions, then compare them under relevant common criteria.
19. **Research provenance**: WHEN a claim informs a direction, the investigation MUST retain its inspected source,
    material date/version and limits while distinguishing vendor claims, inference, contradictions and unknowns
    from observation. Synthetic users and fixtures are scenario input.
20. **Optional criticism**: WHEN shared assumptions or unsupported convergence need examination, the coordinator
    MAY use discovery-critic; zero supported findings is a valid return.
21. **Initial synthesis**: WHEN retaining research documents and a roadmap, the coordinator MUST distinguish
    recommendations, actual user decisions, assumptions and proposed behavior rather than claim implemented
    capability or implicit delivery commitment.
22. **Bounded partial result**: IF evidence, delegation or research effort is insufficient, THEN the coordinator
    MUST retain actual partial evidence and missing coverage without inventing a winner, execution or runtime limit.
23. **Research completion**: WHEN the research entry returns, the coordinator MUST report its bounded outcome and
    next decision; implementation and publication require their own user authority.
24. **Useful alternatives**: WHEN research choices affect resume, current facts SHOULD link retained notes, surviving
    alternatives and conditions that would reopen a choice.
25. **Research workspace**: WHEN scratch writes are needed, the coordinator MUST allocate separate run/task paths
    under `.devkit/transient/incubation-research/`, verify Git ignore/untracked state where applicable, and grant
    only explicit task scratch writes; product source and retained synthesis stay read-only to members.
26. **Selective promotion**: WHEN retaining research outputs, the coordinator MUST select useful synthesis and
    evidence rather than copy the whole run, and resolve retained references without transient-only dependencies;
    allocation edits no ignore rule and does not automatically delete scratch.

Distribution checks enforce file/metadata contracts. Discovery, evidence comparison, optionality, synthesis and
resume are semantic agent contracts. `SPEC-incubation-discovery-teams` retains bounded observed exercises and
their limitations; keyword assertions alone do not establish them.

## 4. Interfaces and Data Contracts

### Distribution and entry

Install devkit-docs and devkit-catalog, then select `uv run devkit add incubation` (`incubation:core`).
Both skills and six common role contracts use existing projection mechanisms. No incubation runtime or CLI is added.

`uv run devkit config show` exposes `configuration.development.approach` and its source.
Entries require incubation; invalid policy propagates `DEVELOPMENT_CONFIG_INVALID`, exit 2.
A valid SDD result produces a guidance-level stop with the shared `[development] approach = "incubation"` action,
not a new error code. Selection/invocation changes no approach. Read `get-context incubation` once and the docs
context/instructions before relevant document work.

`/incubate-research <idea or decision>` accepts natural-language goals and existing documents. The Host frames
a question/bound, commissions useful assignments, validates evidence, compares directions and retains a
proportionate synthesis. `/incubate` can suggest this doorway and await selection while keeping small work inline.
Research terminates with the outcome and next action; a subsequent authorized product action can consume it.

### Optional roles

| Role | Result | Source and Git boundary |
| --- | --- | --- |
| product-clarifier | Candidate users/problems, alternatives and missing questions | Read-only; no invented user decision |
| incubation-researcher | Evidence for one uncertainty, or an explicitly bounded experiment | Read-only by default; assigned scratch notes or prototype writes only |
| direction-explorer | One distinct premise, intended usage, trade-offs, critical assumptions and discriminating evidence | Product read-only; assigned scratch notes only; no production implementation or winner declaration |
| discovery-critic | Cross-candidate framing/evidence findings and failure conditions, or zero findings | Product read-only; assigned scratch notes only; no decision or demanded consensus |
| discovery-planner | Draft product framing, research/architecture notes and conditional roadmap | Product read-only; assigned scratch notes only; no context or retained-synthesis writes |
| usage-reviewer | Expected versus observed representative usage | Read-only product source; assigned test-data interactions only |

The coordinator allocates a collision-free run and per-task directories under `.devkit/transient/incubation-research/`.
Git-backed runs verify exact ignored/untracked paths before scratch writes; absent Git is reported. Members can
write notes only in assigned task directories, with separate authority for experiments. The coordinator promotes
selected synthesis, evidence and important rejected alternatives, validates durable references, and does not
automatically delete scratch or change ignore rules. No allocation registry or CLI is added.

Every role leaves the index and HEAD unchanged and commits/publishes nothing. A result contains status
(`completed`, `needs_input` or `failed`), summary, source/artifact identity, observations with evidence/failure
conditions, recommendation or draft, assumptions and unverified areas. An experiment also returns actual changed
paths, commands and outcomes. The Host verifies boundaries and evidence before fold-back; direct communication
is optional host functionality and never changes authority. There is no SDD envelope requirement.

### Documents, roadmap and resume

Logical output covers a product brief, research/alternatives, direction/architecture notes and an initial
outcome/dependency roadmap. Combine or separate these contents according to useful scope; no file count is required.
Reuse existing destinations, defaulting new labelled discovery/planning notes to project-owned `docs/materials/`.
Apply indexed material rules when identity is needed. A roadmap keeps learning and conditional build work distinct,
with evidence/validation signals and no unsupported dates.

Native capability/use-case/decision/milestone semantics apply only when their subject warrants them; a research
recommendation creates no current capability, user approval or delivery Unit.

`.devkit/incubation.md` remains mutable project-owned Markdown, not managed/transient state or a parsed lifecycle.
Keep current goals, choices versus assumptions, source-specific checks, unresolved evidence and exact note links,
useful surviving alternatives/reopening conditions and the next action. Remove superseded experiments only when
they no longer inform work. A fresh context rechecks identities and applicability instead of replaying history.
