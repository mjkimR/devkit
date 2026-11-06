---
id: PROP-adaptive-swarm-development-target
title: Target Living Spec for Reusable Adaptive Subagents
summary: "Prospective capability, use-case and ownership updates for prefixed adaptive subagents, optional role leads and source-specific combined verification."
status: draft
proposal: PROP-adaptive-swarm-development
created_at: 2026-11-06
targets:
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  - file: docs/usecases/delivery/UC-advance-an-idea.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/decisions/2026-11/20261102-adaptive-development-and-research.md
---

# [PROP-adaptive-swarm-development-target] Target Living Spec for Reusable Adaptive Subagents

These are prospective changes after implementation. Existing Living Spec contracts remain in force during Planning.

## 1. Capability: CAP-DLV-adaptive-development

Preserve clarification, implementation, usage verification, independent docs/catalog installation and optional roles.
Add reusable code-writing delegation without a mandatory pipeline, fixed hierarchy or runtime model router.

- Rule 1 (Explicit selection): define `core` as the existing adaptive assets plus execution archetypes, and `agents`
  as only the three public archetypes. The agents preset leaves the adaptive entry/pointer unselected and changes
  neither approach nor caller lifecycle authority. Extend deployed contents to the three prefixed archetype contracts and their supported
  native projections. Keep existing product-support roles; do not renumber the rule as a role-storage policy.
- Rule 2 (Independent installation): keep installation independent of `devkit-spec` and sibling role catalogs.
- Rule 9 (Truthful verification): describe worker, combined and applicable landed-target checks with exact source
  identities, commands, outcomes and unverified areas.
- Rule 12 (Optional support): allow direct work, flat delegation and optional role leads according to task needs.
- Rule 13 (Role boundaries): add parent-to-child authority narrowing, overlay compatibility, two child levels at most
  and the Host's session-wide budget, including waiting leads.
- Rule 14 (Current context ownership): retain exclusive Host ownership and require useful failure/interruption facts;
  checkpointing does not depend on passing tests.
- Keep existing product-support roles' no-index/HEAD-mutation contract. Define code-writing archetypes' permitted
  Git actions separately; role overlays cannot grant additional authority.
- Add a bounded-assignment clause: before delegated implementation, the Host supplies goal, source/base identity,
  absolute ownership, permitted actions, checks, stop condition and expected return.
- Add a writer-isolation clause: concurrent writers use separate worktrees and parents do not write concurrently
  into child-owned worktrees. Serialize when isolated execution is unavailable.
- Add reuse/extension clauses: one owner per public agent ID; optional compatible callers supply their own role
  contracts; project specialists use distinct prefixed IDs; shipped defaults stay independently usable. No `skill`
  prerequisite or source model/effort default is added to public archetypes. Model policy stays bundle-qualified.
- Scope the bundle constitution's approach guard to adaptive product iteration, preserving generic caller use
  under SDD. Distinguish product support roles' no-commit clause from explicitly assigned worker commit authority.
- Give verifiers an explicit ignored probe/test-output scope without permission to change product sources or Git.
- Add recovery clauses: unsupported nesting falls back to flat/direct execution, and cleanup preserves active,
  dirty or unmerged results until collected or separately authorized for removal.

Restate the promoted decisions from `PADR-skill-local-swarm-roles` and
`PADR-worktree-isolated-parallel-workers` at those clauses. Keep performance outcomes unmeasured until exercised.

## 2. Use Case: UC-advance-an-idea

Keep the ordinary adaptive loop as the main scenario. Add conditional delegation extensions:

1. The Host checks the effective approach and current product facts.
2. The Host chooses the next useful action and its verification.
3. For a small task, the Host acts directly.
4. For separable work, the Host supplies bounded assignments to compatible installed agents.
5. If a role lead is useful and nesting/capacity permit, it delegates children within the assigned allowance.
6. Writers return source-specific changes and checks; leads verify their aggregate assignments.
7. The Host verifies and integrates the combined result through the project's existing authorized route.
8. The Host updates current context with retained results, limitations and next actions.

Extensions cover missing nesting, exhausted slots, unavailable harness commands, incompatible overlays, write-boundary
violations, combined-check failure and interruption. Failed checks route to bounded repair or an explicit unresolved
result. No arbitrary fixed retry count applies to all projects.

## 3. Architecture and Decisions

Update `ARCH-05-2-components` only for catalog content ownership: adaptive-dev owns its archetypes, local role
contracts and orchestration references. Optional external callers may reuse installed public contracts; sibling
bundles do not import private assets or acquire mandatory dependencies.

On promotion, the role PADR partially supersedes relevant role-set clauses of `ADR-adaptive-development-and-research`;
retain its approach, current-context and research-material decisions. Existing projection schemas and shared model
levels remain distribution-owned and unchanged.

## 4. Proposed Bundle Contents

```text
adaptive_dev/bundle/
├── bundle.toml
├── AGENTS.md
├── subagents/
│   ├── product-clarifier.md
│   ├── product-researcher.md
│   ├── usage-reviewer.md
│   ├── swarm-planner.md
│   ├── swarm-worker.md
│   └── swarm-verifier.md
├── skills/adaptive-dev/
│   ├── SKILL.md
│   ├── references/          # existing references plus conditional orchestration guidance
│   └── roles/
│       ├── architect.md
│       ├── builder.md
│       ├── qa-tester.md
│       └── reviewer.md
└── templates/
    └── current-context.md   # existing template; project context remains .devkit/adaptive-dev.md
```

Native subagent contracts declare actual support per host. Role files describe bounded tasks and do not repeat or
widen archetype permissions. Existing product role paths and template identity are retained.

## 5. Verification Plan

- Extend `packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py` for default prefixed assets,
  supported projections, both presets, absolute role resolution, distinct project extensions/collision refusal,
  model-policy keys and bundle self-containment.
- Extend `packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py` for wheel installation
  with docs/catalog and without `devkit-spec`, including archetype projections and agents-only use under SDD.
  Docs currently brings devkit-agt transitively; independence means no SDD requirement, not a no-harness claim.
- Record representative direct/flat/nested invocations, slot fallback, incompatible roles, combined failure and
  interruption recovery. Static packaging checks do not establish semantic runtime behavior.
- Use the consuming project's documented checks. This repository keeps affected-test full fallback, required
  lint/types/rules, selected E2E and final-target verification over the saved baseline interval.

No assertion that the bundle projects zero native subagents is retained: it already registers three support roles,
and this proposal adds three execution archetypes.

## 6. Planning Evidence and Handoff

The concrete assignment example, host declaration matrix, ordered file owners and AC mapping are in
`PROP-adaptive-swarm-development` section 5. Source/projection and bounded read-only nesting observations are in
[feasibility-spike.md](materials/feasibility-spike.md). Development still authors the retained assets, installation
checks and semantic exercises; the Planning prototypes are not shipped bundle contents.
